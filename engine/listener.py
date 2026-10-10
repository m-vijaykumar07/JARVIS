"""
JARVIS Listener Engine
Real-time continuous background acoustic surveillance using Vosk offline grammar-constrained
streaming for zero-latency wake word detection ('Hey Jarvis') and command processing.
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


def find_best_microphone(p: pyaudio.PyAudio) -> tuple[int, str]:
    """
    Selects the active physical microphone or headset.
    Avoids 'Stereo Mix', 'Virtual Audio', 'Sound Mapper', etc.
    """
    candidates = []
    for i in range(p.get_device_count()):
        try:
            info = p.get_device_info_by_index(i)
            if info.get('maxInputChannels', 0) > 0:
                name = info.get('name', '')
                nl = name.lower()
                # Skip loopback / stereo mix
                if any(skip in nl for skip in ['stereo mix', 'mapper', 'primary sound', 'virtual', 'cable']):
                    continue
                candidates.append((i, name))
        except Exception:
            continue

    if not candidates:
        default = p.get_default_input_device_info()
        return default['index'], default['name']

    # 1. Check for Bluetooth Headset/Buds
    for idx, name in candidates:
        nl = name.lower()
        if any(term in nl for term in ['buds', 'headset', 'airpods', 'bluetooth']):
            return idx, name

    # 2. Check for Laptop Realtek / Physical Microphone
    for idx, name in candidates:
        nl = name.lower()
        if 'microphone' in nl or 'mic' in nl:
            return idx, name

    # Fallback to first valid physical candidate
    return candidates[0][0], candidates[0][1]


class Listener:
    def __init__(self, state_callback=None, transcript_callback=None, wake_callback=None):
        self.state_callback = state_callback
        self.transcript_callback = transcript_callback
        self.wake_callback = wake_callback

        self.is_running = False
        self._thread = None
        self._manual_wake_flag = threading.Event()
        self._is_active_listening = False

        self.active_mic_index = 0
        self.active_mic_name = "Detecting..."

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
        if not clean or clean == "[unk]":
            return False, ""

        for w in config.WAKE_WORDS:
            if w in clean:
                idx = clean.find(w) + len(w)
                trailing = clean[idx:].strip()
                return True, trailing
        return False, ""

    def _run_loop(self):
        """Main acoustic surveillance loop."""
        p = pyaudio.PyAudio()

        # Find best active microphone (never Stereo Mix)
        if config.PREFERRED_MIC_INDEX is not None:
            self.active_mic_index = config.PREFERRED_MIC_INDEX
            self.active_mic_name = f"Device Index {self.active_mic_index}"
        else:
            self.active_mic_index, self.active_mic_name = find_best_microphone(p)

        print(f"[Listener] Selected input microphone: [{self.active_mic_index}] {self.active_mic_name}")

        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=config.MIC_SAMPLE_RATE,
                input=True,
                input_device_index=self.active_mic_index,
                frames_per_buffer=config.MIC_CHUNK_SIZE
            )
            stream.start_stream()
        except Exception as e:
            print(f"[Listener] Failed opening device {self.active_mic_index}: {e}. Retrying default.")
            try:
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=config.MIC_SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=config.MIC_CHUNK_SIZE
                )
                stream.start_stream()
            except Exception as ex:
                print(f"[Listener] Critical mic stream failure: {ex}")
                self._run_fallback_loop()
                return

        # Initialize Grammar-Constrained Kaldi Recognizer for maximum wake accuracy
        grammar_list = config.WAKE_WORDS + ["[unk]"]
        grammar_json = json.dumps(grammar_list)

        try:
            kaldi_rec = KaldiRecognizer(self.vosk_model, config.MIC_SAMPLE_RATE, grammar_json)
        except Exception:
            kaldi_rec = KaldiRecognizer(self.vosk_model, config.MIC_SAMPLE_RATE) if self.vosk_model else None

        print("[Listener] Live acoustic surveillance engaged. Waiting for 'Hey Jarvis'...")

        while self.is_running:
            # When speaking or actively recording command, pause wake reads
            if speaker.is_speaking or self._is_active_listening:
                time.sleep(0.08)
                continue

            # Check manual trigger from UI
            if self._manual_wake_flag.is_set():
                self._manual_wake_flag.clear()
                self._notify_wake()
                self._listen_for_command(stream)
                continue

            self._notify_state("STANDBY", f"Mic: {self.active_mic_name[:20]} | Say 'Hey Jarvis'")

            try:
                data = stream.read(config.MIC_CHUNK_SIZE, exception_on_overflow=False)
            except Exception:
                continue

            if speaker.is_speaking or self._is_active_listening:
                continue

            if kaldi_rec:
                if kaldi_rec.AcceptWaveform(data):
                    res = json.loads(kaldi_rec.Result())
                    text = res.get("text", "")
                    if text and text != "[unk]":
                        print(f"[Heard]: {text}")
                        is_wake, trailing = self._check_wake_word(text)
                        if is_wake:
                            self._on_wake_detected(stream, trailing)
                            kaldi_rec.Reset()
                else:
                    partial = json.loads(kaldi_rec.PartialResult()).get("partial", "")
                    if partial and partial != "[unk]":
                        is_wake, trailing = self._check_wake_word(partial)
                        if is_wake:
                            print(f"[Partial Wake Detected]: {partial}")
                            self._on_wake_detected(stream, trailing)
                            kaldi_rec.Reset()

        try:
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception:
            pass

    def _on_wake_detected(self, stream, trailing_command: str):
        """Triggered immediately when wake word is detected."""
        print("[Listener] >>> WAKE WORD CONFIRMED <<<")
        sound_fx.play_wake()
        self._notify_wake()

        if trailing_command and len(trailing_command.split()) >= 1:
            self._execute_command(trailing_command)
        else:
            self._listen_for_command(stream)

    def _listen_for_command(self, stream):
        """Suspends stream, prompts user, and records active command."""
        self._is_active_listening = True
        self._notify_state("LISTENING", "Listening for command...")

        # 1. Stop PyAudio stream temporarily so SpeechRecognition can take the microphone without contention
        try:
            stream.stop_stream()
        except Exception:
            pass

        # 2. Speak greeting acknowledgment
        speaker.speak(f"At your service, {config.USER_NAME}.", block=True)

        print(f"[Listener] Recording user directive on device [{self.active_mic_index}]...")
        self._notify_state("LISTENING", "Speak now...")

        # 3. Capture command using SpeechRecognition on the EXACT physical microphone
        try:
            with sr.Microphone(device_index=self.active_mic_index) as source:
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
            self._notify_state("STANDBY", f"Mic: {self.active_mic_name[:20]} | Say 'Hey Jarvis'")
            # 4. Resume PyAudio stream for continuous background listening
            try:
                stream.start_stream()
            except Exception:
                pass

    def _execute_command(self, command_text: str):
        """Processes and speaks command result."""
        self._notify_transcript("User", command_text)
        self._notify_state("PROCESSING", f"Processing: {command_text}")

        response = commander.process(command_text)
        self._notify_transcript("JARVIS", response)

        speaker.speak(response, block=False)
        self._notify_state("STANDBY", f"Mic: {self.active_mic_name[:20]} | Say 'Hey Jarvis'")

    def _run_fallback_loop(self):
        """SpeechRecognition loop fallback."""
        with sr.Microphone(device_index=self.active_mic_index) as source:
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
                            speaker.speak("Yes sir?", block=True)
                            audio_cmd = self.recognizer.listen(source, timeout=5.0, phrase_time_limit=7.0)
                            cmd = self.recognizer.recognize_google(audio_cmd)
                            self._execute_command(cmd)
                except Exception:
                    continue


# Global singleton instance
listener = Listener()
