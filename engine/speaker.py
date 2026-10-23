"""
JARVIS / SUVI Speech Engine (TTS & Cloned Voice Player)
Combines direct user voice recordings (Suvi cloned clips) with high-definition
Indian English neural voice (Edge-TTS) and offline female SAPI5 fallback.
"""
import os
import sys
import time
import asyncio
import threading
import tempfile
import pygame
from pathlib import Path
import config

try:
    import edge_tts
except ImportError:
    edge_tts = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class Speaker:
    def __init__(self, status_callback=None):
        self.status_callback = status_callback
        self.is_speaking = False
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # Offline fallback engine initialization (select female voice)
        self.sapi_engine = None
        if pyttsx3:
            try:
                self.sapi_engine = pyttsx3.init()
                self.sapi_engine.setProperty('rate', config.SAPI_VOICE_RATE)
                self.sapi_engine.setProperty('volume', config.SAPI_VOICE_VOLUME)
                voices = self.sapi_engine.getProperty('voices')
                for voice in voices:
                    # Select female voice (Zira or any female token)
                    if "zira" in voice.name.lower() or "female" in voice.name.lower():
                        self.sapi_engine.setProperty('voice', voice.id)
                        break
            except Exception as e:
                print(f"[Speaker] Offline SAPI5 warning: {e}")

        # Cloned Voice Audio Samples Map
        self.cloned_clips = {
            "listening": config.VOICE_SAMPLES_DIR / "listening.wav",
            "on_command": config.VOICE_SAMPLES_DIR / "on_your_command.wav",
            "good_morning": config.VOICE_SAMPLES_DIR / "good_morning.wav",
            "task_completed": config.VOICE_SAMPLES_DIR / "task_completed.wav",
            "searching": config.VOICE_SAMPLES_DIR / "searching_info.wav",
            "opening_files": config.VOICE_SAMPLES_DIR / "opening_files.wav",
            "ready_to_help": config.VOICE_SAMPLES_DIR / "ready_to_help.wav",
            "thank_you": config.VOICE_SAMPLES_DIR / "thank_you.wav"
        }

    def _notify(self, state: str, text: str = ""):
        if self.status_callback:
            try:
                self.status_callback(state, text)
            except Exception:
                pass

    def _match_cloned_clip(self, text: str) -> Path | None:
        """
        Intelligently maps any command or response to one of Suvi's authentic cloned voice clips.
        Ensures Suvi's real voice responds to EVERY command.
        """
        lower = text.lower().strip()

        # 1. Listening / Wake prompts
        if any(term in lower for term in [
            "i'm listening", "im listening", "tell me what you need", "what you need",
            "listening. please tell me", "listening for command", "speak now"
        ]):
            clip = self.cloned_clips.get("listening")
            if clip and clip.exists():
                return clip

        # 2. Gratitude / Thanks / Courtesies
        if any(term in lower for term in [
            "thank you", "thanks", "always at your service", "open to your heart",
            "always open to your heart", "thank you, always", "my pleasure", "welcome"
        ]):
            clip = self.cloned_clips.get("thank_you")
            if clip and clip.exists():
                return clip

        # 3. Morning / Startup greeting
        if any(term in lower for term in [
            "good morning", "all systems are ready", "systems are ready",
            "systems nominal", "online and ready"
        ]):
            clip = self.cloned_clips.get("good_morning")
            if clip and clip.exists():
                return clip

        # 4. Opening / Launching apps, files, directories, URLs, websites
        if any(term in lower for term in [
            "opening", "launching", "initializing", "started", "opened", "bring up",
            "opening your files", "opening files", "starting", "launch ", "open ", "browser"
        ]):
            clip = self.cloned_clips.get("opening_files")
            if clip and clip.exists():
                return clip

        # 5. Searching web, looking up data, queries, research
        if any(term in lower for term in [
            "searching", "searching for", "retrieving", "looking up", "search the web",
            "search results", "finding information", "searching for the information"
        ]):
            clip = self.cloned_clips.get("searching")
            if clip and clip.exists():
                return clip

        # 6. Completed tasks, adjustments, changes (Volume, Brightness, Notes, Screenshots, Mute, Window actions)
        if any(term in lower for term in [
            "completed", "task completed", "task has been completed", "successfully",
            "volume set", "volume increased", "volume decreased", "audio muted", "audio unmuted",
            "brightness adjusted", "screenshot captured", "note recorded", "saved note",
            "desktop revealed", "window maximized", "window minimized", "switched to next window",
            "recycle bin emptied", "terminated", "closed", "workstation locked", "cancelled",
            "cleared", "switched"
        ]):
            clip = self.cloned_clips.get("task_completed")
            if clip and clip.exists():
                return clip

        # 7. Help, readiness, exit, standby
        if any(term in lower for term in [
            "ready to help", "if you need anything else", "need anything else",
            "help", "goodbye", "farewell", "bye", "standby"
        ]):
            clip = self.cloned_clips.get("ready_to_help")
            if clip and clip.exists():
                return clip

        # 8. On command / directives / general commands / acknowledgments
        if any(term in lower for term in [
            "on your command", "at your command", "certainly, i'm on", "on command",
            "certainly", "understood", "right away", "executing", "acknowledged",
            "i am on your command", "proceed"
        ]):
            clip = self.cloned_clips.get("on_command")
            if clip and clip.exists():
                return clip

        # 9. Default cloned clip for EVERY command when CLONED_VOICE_EVERY_COMMAND is active
        if getattr(config, 'CLONED_VOICE_EVERY_COMMAND', True):
            clip = self.cloned_clips.get("on_command")
            if clip and clip.exists():
                return clip

        return None

    def _has_dynamic_payload(self, text: str) -> bool:
        """Determines if the text contains specific data/information that should be voiced."""
        lower = text.lower().strip()
        # If it's pure canned action text, there is no separate payload needed
        pure_actions = [
            "opening your files", "task has been completed", "good morning. all systems are ready",
            "i'm listening. please tell me what you need", "thank you, always open to your heart",
            "i am ready to help, if you need anything else", "i am on your command",
            "audio muted, sir.", "audio unmuted, sir.", "desktop revealed, sir.",
            "switched to next window, sir.", "window maximized, sir.", "window minimized, sir.",
            "workstation locked, sir."
        ]
        if any(pure in lower for pure in pure_actions):
            return False

        # If it has specific numbers, times, battery percentages, diagnostics, or detailed AI answers:
        dynamic_markers = [
            "current time", "the time is", "battery is", "cpu load", "ram usage",
            "today is", "weather in", "clipboard contains", "saved notes",
            "based on the data", "cybersecurity", "ethical hacking", "python"
        ]
        if any(m in lower for m in dynamic_markers):
            return True

        # If text is long (>70 chars), it's likely a descriptive conversational answer
        if len(text) > 70:
            return True

        return False

    def _play_wav_clip(self, clip_path: Path) -> bool:
        """Plays real user-recorded WAV soundbite."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            sound = pygame.mixer.Sound(str(clip_path))
            channel = sound.play()
            while channel.get_busy():
                if self._stop_event.is_set():
                    channel.stop()
                    break
                time.sleep(0.04)
            return True
        except Exception as e:
            print(f"[Speaker] Cloned clip playback error: {e}")
            return False

    async def _generate_edge_tts(self, text: str, output_path: str):
        """Generates neural speech MP3 using Edge TTS (Suvi Indian female voice)."""
        communicate = edge_tts.Communicate(
            text=text,
            voice=config.EDGE_TTS_VOICE,
            rate=config.EDGE_TTS_RATE,
            pitch=config.EDGE_TTS_PITCH
        )
        await communicate.save(output_path)

    def _speak_edge(self, text: str) -> bool:
        """Synthesizes and plays with Edge-TTS."""
        if not edge_tts:
            return False

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_path = f.name

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._generate_edge_tts(text, temp_path))
            loop.close()

            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                return False

            if not pygame.mixer.get_init():
                pygame.mixer.init()

            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                if self._stop_event.is_set():
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.05)

            pygame.mixer.music.unload()
            return True
        except Exception:
            return False
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def _speak_offline(self, text: str):
        """Offline fallback using pyttsx3 (Female voice)."""
        if self.sapi_engine:
            try:
                self.sapi_engine.say(text)
                self.sapi_engine.runAndWait()
            except Exception as e:
                print(f"[Speaker] Offline voice error: {e}")

    def speak(self, text: str, block: bool = True):
        """
        Main speak interface.
        Plays cloned voice recording if matched, else synthesizes with Suvi neural voice.
        """
        if not text or not text.strip():
            return

        def _worker():
            with self._lock:
                self.is_speaking = True
                self._stop_event.clear()
                self._notify("SPEAKING", text)
                print(f"\n[SUVI]: {text}")

                # 1. Play Suvi cloned audio clip for every command
                if getattr(config, 'USE_CLONED_VOICE', True):
                    clip_path = self._match_cloned_clip(text)
                    if clip_path and not self._stop_event.is_set():
                        success = self._play_wav_clip(clip_path)
                        # If the text is an action confirmation with no dynamic data, we are done!
                        if success and not self._has_dynamic_payload(text):
                            self.is_speaking = False
                            self._notify("IDLE", "")
                            return

                # 2. Synthesize using Suvi neural Indian voice
                success = False
                if config.TTS_ENGINE_PREFERENCE == "edge-tts":
                    success = self._speak_edge(text)

                # 3. Offline fallback
                if not success and not self._stop_event.is_set():
                    self._speak_offline(text)

                self.is_speaking = False
                self._notify("IDLE", "")

        if block:
            _worker()
        else:
            threading.Thread(target=_worker, daemon=True).start()

    def stop(self):
        """Interrupts ongoing speech."""
        self._stop_event.set()
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.stop()
        except Exception:
            pass
        if self.sapi_engine:
            try:
                self.sapi_engine.stop()
            except Exception:
                pass
        self.is_speaking = False
        self._notify("IDLE", "")


# Global singleton
speaker = Speaker()
