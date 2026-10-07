"""
JARVIS Background Daemon (Runs silently with pythonw.exe)
Listens continuously in the background without any visible terminal window.
When "Hey Jarvis" is spoken, automatically wakes up the HUD on the Windows desktop!
"""
import os
import sys
import threading
import time

# Ensure project directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from engine.listener import listener
from engine.speaker import speaker
from engine.sound_effects import sound_fx
from ui.hud import JarvisHUD
import config

def main():
    # 1. Initialize HUD in hidden background mode
    app = JarvisHUD(start_hidden=True)

    # 2. Start continuous background listener
    listener.start()

    # 3. Soft audio alert that JARVIS background surveillance is engaged
    def _notify_startup():
        time.sleep(0.5)
        sound_fx.play_wake()

    threading.Thread(target=_notify_startup, daemon=True).start()

    # 4. Handle Window Close: instead of exiting, hide back to background!
    def on_window_close():
        app.hide_to_background()

    app.protocol("WM_DELETE_WINDOW", on_window_close)

    # 5. Run UI event loop
    try:
        app.mainloop()
    except Exception as e:
        print(f"[JARVIS Daemon Error]: {e}")

if __name__ == "__main__":
    main()
