"""Safe allow-list for Windows desktop actions connected to JARVIS engine."""
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from engine.system_actions import system_actions
from engine.speaker import speaker

_ACTIONS = {
    "calculator": "calc",
    "notepad": "notepad",
    "explorer": "explorer",
    "chrome": "chrome",
    "screenshot": "screenshot",
}

def allowed_actions():
    return [
        {"id": "calculator", "label": "Open Calculator"},
        {"id": "notepad", "label": "Open Notepad"},
        {"id": "explorer", "label": "Open File Explorer"},
        {"id": "chrome", "label": "Open Chrome"},
        {"id": "screenshot", "label": "Take Screenshot"},
    ]

def run_allowed_action(action: str) -> dict:
    if action not in _ACTIONS:
        return {"ok": False, "message": "Action is not allow-listed."}
    
    try:
        if action == "screenshot":
            msg = system_actions.take_screenshot()
        else:
            msg = system_actions.launch_app(_ACTIONS[action])
        
        # Announce with Suvi cloned voice
        speaker.speak(msg, block=False)
        return {"ok": True, "message": msg}
    except Exception as e:
        return {"ok": False, "message": f"Could not perform {action}: {e}"}
