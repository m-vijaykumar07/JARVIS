"""
JARVIS Voice Assistant - Main System Orchestrator
Launches the background acoustic surveillance listener and the desktop Arc Reactor HUD.
"""
import sys
import threading
import time
from engine.listener import listener
from engine.speaker import speaker
from engine.sound_effects import sound_fx
from engine.system_actions import system_actions
from ui.hud import JarvisHUD
import config

def startup_greeting():
    """Initializes systems with audio chime and status announcement."""
    time.sleep(0.5)
    sound_fx.play_wake()
    battery = system_actions.get_battery_status()
    greeting = f"JARVIS online and fully operational. All core systems nominal, {config.USER_NAME}."
    speaker.speak(greeting, block=False)

def main():
    print("=" * 60)
    print("      J.A.R.V.I.S. VOICE ASSISTANT SYSTEM - MK-85      ")
    print(f"      Status: Online | Target: {config.USER_NAME}     ")
    print(f"      Wake Words: {', '.join(config.WAKE_WORDS)}     ")
    print("=" * 60)

    # 1. Initialize Desktop HUD
    app = JarvisHUD()

    # 2. Start Background Speech Recognition Listener
    listener.start()

    # 3. Trigger startup announcement
    threading.Thread(target=startup_greeting, daemon=True).start()

    # 4. Handle Window Close
    def on_closing():
        print("[JARVIS] Commencing shutdown sequence...")
        sound_fx.play_sleep()
        listener.stop()
        speaker.stop()
        app.destroy()
        sys.exit(0)

    app.protocol("WM_DELETE_WINDOW", on_closing)

    # 5. Start UI Event Loop
    try:
        app.mainloop()
    except KeyboardInterrupt:
        on_closing()

if __name__ == "__main__":
    main()
