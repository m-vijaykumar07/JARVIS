import os
import sys
from pathlib import Path

# Ensure jarvis root is in path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from engine.commander import commander
from engine.speaker import speaker
import config

def process_message(message: str) -> str:
    message = message.strip()
    if not message:
        return "I'm listening. Please tell me what you need."

    # Route through unified JARVIS / SUVI Commander
    res = commander.process_structured(message)
    spoken = res.get("spoken", "")
    display = res.get("display", spoken)

    # Speak response using cloned voice
    if spoken:
        speaker.speak(spoken, block=False)

    return display or spoken or "Task completed."
