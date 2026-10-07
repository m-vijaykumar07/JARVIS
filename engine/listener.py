"""
JARVIS Listener Engine
Real-time continuous background acoustic listener using Vosk offline streaming
for zero-latency wake word detection ('Hey Jarvis') and command processing.
"""
import os
import json
import time
import threading
import pyaudio
import speech_recognition as sr
from engine.sound_effects import sound_fx
from engine.speaker import speaker
from engine.commander import commander
import config

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = os.path.exists(str(config.VOSK_MODEL_PATH))
except ImportError:
    VOSK_AVAILABLE = False


class Listener:
    def __init__(self, state_callback=None, transcript_callback=None, wake_callback=None):
        self.state_callback = state_callback
        self.transcript_callback = transcript_callback
        self.wake_callback = wake_callback

        self.is_running = False
        self._thread = None
        self._manual_wake_flag = threading.Event()
        self._is_active_listening = False

        # SpeechRecognizer fallback & command transcription
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = config.ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = config.DYNAMIC_ENERGY
        self.recognizer.pause_threshold = config.PAUSE_THRESHOLD

        # Vosk offline model
        self.vosk_model = None
        if VOSK_AVAILABLE:
            try:
                self.vosk_model = Model(str(config.VOSK_MODEL_PATH))
            except Exception as e:
                print(f"[Listener] Vosk init note: {e}")

    def set_callbacks(self, state_callback=None, transcript_callback=None, wake_callback=None):
        if state_callback:
            self.state_callback = state_callback
        if transcript_callback:
            self.transcript_callback = transcript_callback
        if wake_callback:
            self.wake_callback = wake_callback

    def _notify_state(self, state: str, detail: str = ""):
        if self.state_callback:
            try:
                self.state_callback(state, detail)
            except Exception:
                pass

    def _notify_transcript(self, sender: str, text: str):
        if self.transcript_callback:
            try:
                self.transcript_callback(sender, text)
            except Exception:
                pass

    def _notify_wake(self):
        if self.wake_callback:
            try:
                self.wake_callback()
            except Exception:
                pass

    def start(self):
        """Starts background continuous listening thread."""
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("[Listener] Background acoustic surveillance initialized (Vosk Stream Mode).")

    def stop(self):
        """Stops listening."""
        self.is_running = False

    def trigger_wake_manually(self):
        """Manually wakes JARVIS (from HUD button or hotkey)."""
        self._manual_wake_flag.set()

    def process_typed_command(self, text: str):
        """Executes a command entered via text bar."""
        if not text or not text.strip():
            return
        self._notify_transcript("User", text)
        self._notify_state("PROCESSING", f"Analyzing: {text}")
        response = commander.process(text)
        self._notify_transcript("JARVIS", response)
        speaker.speak(response, block=False)

    def _check_wake_word(self, text: str) -> tuple[bool, str]:
        """Checks if text contains any wake word and extracts trailing command."""
        clean = text.lower().strip()
        if not clean:
            return False, ""

        for w in config.WAKE_WORDS:
            if w in clean:
                idx = clean.find(w) + len(w)
                trailing = clean[idx:].strip()
                return True, trailing
        return False, ""

    def _run_loop(self):
        """Main listening loop."""
        p = pyaudio.PyAudio()
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=config.MIC_SAMPLE_RATE,
                input=True,
                frames_per_buffer=config.MIC_CHUNK_SIZE
            )
            stream.start_stream()
        except Exception as e:
            print(f"[Listener] Mic open error: {e}. Falling back to SpeechRecognition.")
            self._run_fallback_loop()
            return

        kaldi_rec = KaldiRecognizer(self.vosk_model, config.MIC_SAMPLE_RATE) if self.vosk_model else None

        print("[Listener] Live microphone stream active. Ready for 'Hey Jarvis'...")

        while self.is_running:
            # If Jarvis is speaking or active listening is occurring, pause stream reads
            if speaker.is_speaking or self._is_active_listening:
                time.sleep(0.08)
                continue

            # Manual wake triggered from UI
            if self._manual_wake_flag.is_set():
                self._manual_wake_flag.clear()
                self._notify_wake()
                self._listen_for_command(stream)
                continue

            self._notify_state("STANDBY", "Listening for 'Hey Jarvis'...")

            try:
                data = stream.read(config.MIC_CHUNK_SIZE, exception_on_overflow=False)
            except Exception:
                continue

            if speaker.is_speaking:
                continue

            # Feed to Vosk Kaldi Recognizer
            if kaldi_rec:
                if kaldi_rec.AcceptWaveform(data):
                    res = json.loads(kaldi_rec.Result())
                    text = res.get("text", "")
                    if text:
                        print(f"[Acoustic Heard]: {text}")
                        is_wake, trailing = self._check_wake_word(text)
                        if is_wake:
                            self._on_wake_detected(stream, trailing)
                            kaldi_rec.Reset()
                else:
                    partial = json.loads(kaldi_rec.PartialResult()).get("partial", "")
                    if partial:
                        is_wake, trailing = self._check_wake_word(partial)
                        if is_wake:
                            print(f"[Acoustic Partial Wake]: {partial}")
                            self._on_wake_detected(stream, trailing)
                            kaldi_rec.Reset()

        try:
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception:
            pass

    def _on_wake_detected(self, stream, trailing_command: str):
        """Handles wake word trigger."""
        print("[Listener] Wake word confirmed!")
        sound_fx.play_wake()
        self._notify_wake()

        if trailing_command and len(trailing_command.split()) >= 1:
            # User said "Hey Jarvis open chrome" in one breath
            self._execute_command(trailing_command)
        else:
            # User just said "Hey Jarvis", listen for active command
            self._listen_for_command(stream)

    def _listen_for_command(self, stream):
        """Records active command with silence detection and transcribes."""
        self._is_active_listening = True
        self._notify_state("LISTENING", "Listening for command...")

        # Brief greeting acknowledgment
        speaker.speak(f"At your service, {config.USER_NAME}.", block=True)

        print("[Listener] Listening for user directive...")
        self._notify_state("LISTENING", "Speak now...")

        # Transcribe command using Google Speech Recognition for rich vocabulary
        try:
            with sr.Microphone() as source:
                audio = self.recognizer.listen(source, timeout=6.0, phrase_time_limit=config.PHRASE_TIME_LIMIT)
                self._notify_state("PROCESSING", "Analyzing speech...")

                try:
                    command_text = self.recognizer.recognize_google(audio, language="en-US")
                    print(f"[Command Transcribed]: {command_text}")
                    self._execute_command(command_text)
                except sr.UnknownValueError:
                    sound_fx.play_alert()
                    speaker.speak(f"I didn't quite catch that, {config.USER_NAME}.", block=False)
                except sr.RequestError:
                    speaker.speak("Speech recognition network service is currently unreachable.", block=False)

        except sr.WaitTimeoutError:
            print("[Listener] Command wait timed out.")
        except Exception as e:
            print(f"[Listener] Command capture error: {e}")
        finally:
            self._is_active_listening = False
            self._notify_state("STANDBY", "Awaiting 'Hey Jarvis'...")

    def _execute_command(self, command_text: str):
        """Processes and speaks command result."""
        self._notify_transcript("User", command_text)
        self._notify_state("PROCESSING", f"Processing: {command_text}")

        response = commander.process(command_text)
        self._notify_transcript("JARVIS", response)

        speaker.speak(response, block=False)
        self._notify_state("STANDBY", "Awaiting 'Hey Jarvis'...")

    def _run_fallback_loop(self):
        """Standard SpeechRecognition fallback if PyAudio stream fails."""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
            while self.is_running:
                if speaker.is_speaking:
                    time.sleep(0.1)
                    continue
                try:
                    audio = self.recognizer.listen(source, timeout=3.0, phrase_time_limit=4.0)
                    text = self.recognizer.recognize_google(audio).lower()
                    is_wake, trailing = self._check_wake_word(text)
                    if is_wake:
                        sound_fx.play_wake()
                        self._notify_wake()
                        if trailing:
                            self._execute_command(trailing)
                        else:
                            audio_cmd = self.recognizer.listen(source, timeout=5.0, phrase_time_limit=7.0)
                            cmd = self.recognizer.recognize_google(audio_cmd)
                            self._execute_command(cmd)
                except Exception:
                    continue


# Global singleton instance
listener = Listener()
