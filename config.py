"""
JARVIS / SUVI Voice Assistant - Configuration File
Customized with the user's uploaded voice clone model (Suvi).
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"
VOICE_SAMPLES_DIR = ASSETS_DIR / "voice_samples"
VOSK_MODEL_PATH = ASSETS_DIR / "vosk-model-small-en-us-0.15"
SCREENSHOTS_DIR = Path.home() / "Pictures" / "JARVIS_Screenshots"

# Ensure directories exist
SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
VOICE_SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# User Personalization
USER_NAME = "Sir"
ASSISTANT_NAME = "SUVI"

# Wake Words (Supports both Suvi and Jarvis)
WAKE_WORDS = [
    "hey suvi",
    "suvi",
    "wake up suvi",
    "hello suvi",
    "hi suvi",
    "ok suvi",
    "hey jarvis",
    "jarvis",
    "wake up jarvis",
    "wake up",
    "hello jarvis",
    "hi jarvis",
    "ok jarvis",
    "service",
    "travis"
]

# Audio Settings
MIC_SAMPLE_RATE = 16000
MIC_CHUNK_SIZE = 2000
ENERGY_THRESHOLD = 150
DYNAMIC_ENERGY = True
PAUSE_THRESHOLD = 0.7
PHRASE_TIME_LIMIT = 8

# Selected Microphone Index (None for smart auto-detect)
PREFERRED_MIC_INDEX = None

# Voice & Speech Synthesis (TTS) Settings
# Cloned / matched to user's uploaded "Suvi" voice: natural young Indian English female tone
TTS_ENGINE_PREFERENCE = "edge-tts"
EDGE_TTS_VOICE = "en-IN-NeerjaNeural"
EDGE_TTS_RATE = "+0%"
EDGE_TTS_PITCH = "+2Hz"

SAPI_VOICE_RATE = 180
SAPI_VOICE_VOLUME = 1.0

# Sound Effects
ENABLE_SOUND_EFFECTS = True

# Voice Mode: True = use Suvi cloned WAV clips when matched, False = always use Edge-TTS
USE_CLONED_VOICE = True

# Common Windows Applications Mappings
APP_COMMANDS = {
    "chrome": "start chrome",
    "google chrome": "start chrome",
    "edge": "start msedge",
    "microsoft edge": "start msedge",
    "browser": "start msedge",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "code": "code",
    "vs code": "code",
    "visual studio code": "code",
    "spotify": "start spotify:",
    "terminal": "start wt",
    "command prompt": "start cmd",
    "powershell": "start powershell",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "my files": "explorer.exe",
    "task manager": "taskmgr.exe",
    "settings": "start ms-settings:",
    "control panel": "control.exe",
    "camera": "start microsoft.windows.camera:",
    "paint": "mspaint.exe",
    "word": "start winword",
    "excel": "start excel",
    "powerpoint": "start powerpnt",
    "whatsapp": "start whatsapp:",
    "discord": "start discord:",
    "telegram": "start telegram:"
}

# Web Shortcut URLs
WEB_BOOKMARKS = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://www.github.com",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://chat.openai.com",
    "reddit": "https://www.reddit.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "netflix": "https://www.netflix.com",
    "amazon": "https://www.amazon.com",
    "linkedin": "https://www.linkedin.com",
    "maps": "https://maps.google.com",
    "news": "https://news.google.com"
}

# UI Theme Colors
COLOR_BG_DARK = "#090d16"
COLOR_BG_CARD = "#101726"
COLOR_ACCENT_CYAN = "#00e5ff"
COLOR_ACCENT_GLOW = "#00b4d8"
COLOR_ACCENT_AMBER = "#ffb703"
COLOR_ACCENT_GREEN = "#00f5d4"
COLOR_ACCENT_PURPLE = "#7b2cbf"
COLOR_TEXT_MAIN = "#ffffff"
COLOR_TEXT_MUTED = "#8892b0"
