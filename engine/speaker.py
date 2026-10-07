"""
JARVIS Speech Engine (TTS)
Generates high-definition British AI voice using Edge-TTS with instant offline SAPI5 fallback.
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

        # Offline fallback engine initialization
        self.sapi_engine = None
        if pyttsx3:
            try:
                self.sapi_engine = pyttsx3.init()
                self.sapi_engine.setProperty('rate', config.SAPI_VOICE_RATE)
                self.sapi_engine.setProperty('volume', config.SAPI_VOICE_VOLUME)
                # Select male voice if available (Microsoft David)
                voices = self.sapi_engine.getProperty('voices')
                for voice in voices:
                    if "david" in voice.name.lower():
                        self.sapi_engine.setProperty('voice', voice.id)
                        break
            except Exception as e:
                print(f"[Speaker] Offline SAPI5 warning: {e}")

    def _notify(self, state: str, text: str = ""):
        if self.status_callback:
            try:
                self.status_callback(state, text)
            except Exception:
                pass

    async def _generate_edge_tts(self, text: str, output_path: str):
        """Generates neural speech MP3 using Edge TTS."""
        communicate = edge_tts.Communicate(
            text=text,
            voice=config.EDGE_TTS_VOICE,
            rate=config.EDGE_TTS_RATE,
            pitch=config.EDGE_TTS_PITCH
        )
        await communicate.save(output_path)

    def _speak_edge(self, text: str) -> bool:
        """Attempts to synthesize and play with Edge-TTS."""
        if not edge_tts:
            return False

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_path = f.name

            # Run async edge_tts in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._generate_edge_tts(text, temp_path))
            loop.close()

            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                return False

            # Play audio via Pygame Mixer
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
        except Exception as e:
            # print(f"[Speaker] Edge TTS failed, falling back to SAPI: {e}")
            return False
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def _speak_offline(self, text: str):
        """Offline fallback using pyttsx3 SAPI5."""
        if self.sapi_engine:
            try:
                self.sapi_engine.say(text)
                self.sapi_engine.runAndWait()
            except Exception as e:
                print(f"[Speaker] Offline voice error: {e}")

    def speak(self, text: str, block: bool = True):
        """
        Main speak interface.
        If block is False, speaks asynchronously in a daemon thread.
        """
        if not text or not text.strip():
            return

        def _worker():
            with self._lock:
                self.is_speaking = True
                self._stop_event.clear()
                self._notify("SPEAKING", text)
                print(f"\n[JARVIS]: {text}")

                # 1. Try high-definition neural voice
                success = False
                if config.TTS_ENGINE_PREFERENCE == "edge-tts":
                    success = self._speak_edge(text)

                # 2. Fall back to offline SAPI5 if needed
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
        except Exception:
            pass
        if self.sapi_engine:
            try:
                self.sapi_engine.stop()
            except Exception:
                pass
        self.is_speaking = False
        self._notify("IDLE", "")


# Global singleton instance
speaker = Speaker()
