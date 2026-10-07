"""
JARVIS Sound Effects Engine
Synthesizes and plays futuristic interface audio chimes without external dependencies.
"""
import os
import math
import struct
import wave
import threading
import pygame
from pathlib import Path
import config

# Initialize Pygame Mixer quietly
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
except Exception:
    pass

class SoundEffects:
    def __init__(self):
        self.sounds_dir = config.SOUNDS_DIR
        self._ensure_chimes_generated()

    def _generate_wav(self, filepath: Path, frequencies: list[tuple[float, float]], decay: float = 6.0):
        """
        Synthesizes high-tech harmonic frequencies to a 16-bit WAV file.
        frequencies: list of (frequency_hz, duration_seconds)
        """
        if filepath.exists():
            return
        
        sample_rate = 44100
        total_samples = []

        for freq, dur in frequencies:
            n_samples = int(dur * sample_rate)
            for i in range(n_samples):
                t = i / sample_rate
                # Smooth envelope (fast attack, exponential decay)
                attack = min(1.0, 15.0 * (i / n_samples))
                fade = math.exp(-decay * (i / n_samples))
                # Add fundamental and subtle 1st harmonic
                val = 0.8 * math.sin(2 * math.pi * freq * t) + 0.2 * math.sin(4 * math.pi * freq * t)
                sample = int(32767 * 0.45 * attack * fade * val)
                total_samples.append(sample)

        with wave.open(str(filepath), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            raw_bytes = struct.pack(f'<{len(total_samples)}h', *total_samples)
            wf.writeframes(raw_bytes)

    def _ensure_chimes_generated(self):
        """Creates the futuristic JARVIS sound set if not already on disk."""
        try:
            # Wake chime: Sci-Fi ascending triad (D5 -> A5 -> D6)
            self.wake_path = self.sounds_dir / "wake.wav"
            self._generate_wav(self.wake_path, [(587.33, 0.08), (880.0, 0.08), (1174.66, 0.25)], decay=4.5)

            # Success chime: Crisp double ping (G5 -> C6)
            self.success_path = self.sounds_dir / "success.wav"
            self._generate_wav(self.success_path, [(783.99, 0.09), (1046.5, 0.20)], decay=5.0)

            # Alert chime: Low dual-tone
            self.alert_path = self.sounds_dir / "alert.wav"
            self._generate_wav(self.alert_path, [(440.0, 0.12), (349.23, 0.18)], decay=4.0)

            # Sleep chime: Descending soft chime
            self.sleep_path = self.sounds_dir / "sleep.wav"
            self._generate_wav(self.sleep_path, [(880.0, 0.10), (587.33, 0.20)], decay=4.0)
        except Exception as e:
            print(f"[SoundEffects] Generation notice: {e}")

    def _play(self, filepath: Path):
        """Plays sound asynchronously without blocking voice thread."""
        if not config.ENABLE_SOUND_EFFECTS or not filepath.exists():
            return
        
        def _run():
            try:
                sound = pygame.mixer.Sound(str(filepath))
                sound.set_volume(0.6)
                sound.play()
            except Exception:
                pass

        threading.Thread(target=_run, daemon=True).start()

    def play_wake(self):
        self._play(self.wake_path)

    def play_success(self):
        self._play(self.success_path)

    def play_alert(self):
        self._play(self.alert_path)

    def play_sleep(self):
        self._play(self.sleep_path)

# Global singleton
sound_fx = SoundEffects()
