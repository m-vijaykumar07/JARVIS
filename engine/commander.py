"""
JARVIS Commander (NLP & Intent Dispatcher)
Interprets natural language voice commands and executes system, web, and hardware operations.
"""
import re
import datetime
from engine.system_actions import system_actions
from engine.web_actions import web_actions
from engine.sound_effects import sound_fx
from engine.speaker import speaker
import config

class Commander:
    def __init__(self):
        pass

    def process(self, text: str) -> str:
        """
        Parses text input from voice or text bar, performs the action,
        and returns the spoken response.
        """
        if not text or not text.strip():
            return ""

        raw = text.strip()
        cmd = raw.lower()

        # Clean common wake prefixes if present in command
        for wake in config.WAKE_WORDS:
            if cmd.startswith(wake):
                cmd = cmd[len(wake):].strip()
                break

        if not cmd:
            sound_fx.play_wake()
            return f"At your service, {config.USER_NAME}. What shall I do?"

        # -------------------------------------------------------------
        # 1. SYSTEM AUDIO VOLUME
        # -------------------------------------------------------------
        if any(w in cmd for w in ["mute audio", "mute sound", "mute volume", "mute"]):
            sound_fx.play_success()
            return system_actions.mute_volume()

        if any(w in cmd for w in ["unmute audio", "unmute sound", "unmute volume", "unmute"]):
            sound_fx.play_success()
            return system_actions.unmute_volume()

        # "set volume to 80" / "volume 50 percent"
        vol_match = re.search(r'(?:set\s+)?volume\s+(?:to\s+)?(\d{1,3})', cmd)
        if vol_match:
            level = int(vol_match.group(1))
            sound_fx.play_success()
            return system_actions.set_volume(level)

        if any(w in cmd for w in ["volume up", "increase volume", "raise volume", "turn up the volume", "sound up"]):
            sound_fx.play_success()
            return system_actions.change_volume(+15)

        if any(w in cmd for w in ["volume down", "decrease volume", "lower volume", "turn down the volume", "sound down"]):
            sound_fx.play_success()
            return system_actions.change_volume(-15)

        # -------------------------------------------------------------
        # 2. SCREEN BRIGHTNESS
        # -------------------------------------------------------------
        bright_match = re.search(r'(?:set\s+)?brightness\s+(?:to\s+)?(\d{1,3})', cmd)
        if bright_match:
            level = int(bright_match.group(1))
            sound_fx.play_success()
            return system_actions.set_brightness(level)

        if "max brightness" in cmd or "maximum brightness" in cmd or "full brightness" in cmd:
            sound_fx.play_success()
            return system_actions.set_brightness(100)

        if any(w in cmd for w in ["brightness up", "increase brightness", "more brightness"]):
            sound_fx.play_success()
            return system_actions.change_brightness(+15)

        if any(w in cmd for w in ["brightness down", "decrease brightness", "dim screen", "less brightness"]):
            sound_fx.play_success()
            return system_actions.change_brightness(-15)

        # -------------------------------------------------------------
        # 3. BATTERY & SYSTEM DIAGNOSTICS
        # -------------------------------------------------------------
        if any(w in cmd for w in ["battery", "battery level", "battery status", "how much charge", "power status"]):
            sound_fx.play_success()
            return system_actions.get_battery_status()

        if any(w in cmd for w in ["system report", "system status", "diagnostic", "cpu usage", "ram usage", "pc performance"]):
            sound_fx.play_success()
            return system_actions.get_system_report()

        # -------------------------------------------------------------
        # 4. POWER & SECURITY CONTROLS
        # -------------------------------------------------------------
        if any(w in cmd for w in ["lock laptop", "lock pc", "lock computer", "lock screen", "lock workstation"]):
            sound_fx.play_alert()
            return system_actions.lock_workstation()

        if any(w in cmd for w in ["sleep laptop", "sleep pc", "put laptop to sleep", "sleep computer"]):
            sound_fx.play_sleep()
            return system_actions.sleep_laptop()

        if any(w in cmd for w in ["shutdown laptop", "shutdown computer", "turn off laptop", "turn off pc"]):
            sound_fx.play_alert()
            return system_actions.shutdown_laptop()

        if any(w in cmd for w in ["restart laptop", "reboot laptop", "restart pc", "reboot pc"]):
            sound_fx.play_alert()
            return system_actions.restart_laptop()

        if any(w in cmd for w in ["cancel shutdown", "abort shutdown"]):
            sound_fx.play_success()
            return system_actions.cancel_shutdown()

        # -------------------------------------------------------------
        # 5. DESKTOP & WINDOW NAVIGATION
        # -------------------------------------------------------------
        if any(w in cmd for w in ["show desktop", "minimize all", "go to desktop", "clear screen"]):
            sound_fx.play_success()
            return system_actions.show_desktop()

        if any(w in cmd for w in ["switch window", "next window", "alt tab"]):
            sound_fx.play_success()
            return system_actions.switch_window()

        if any(w in cmd for w in ["maximize window", "maximize"]):
            sound_fx.play_success()
            return system_actions.maximize_window()

        if any(w in cmd for w in ["minimize window", "minimize this"]):
            sound_fx.play_success()
            return system_actions.minimize_window()

        if "scroll down" in cmd:
            return system_actions.scroll_down()

        if "scroll up" in cmd:
            return system_actions.scroll_up()

        # -------------------------------------------------------------
        # 6. PRODUCTIVITY & UTILITIES
        # -------------------------------------------------------------
        if any(w in cmd for w in ["take screenshot", "capture screen", "take a screenshot", "screenshot"]):
            sound_fx.play_success()
            return system_actions.take_screenshot()

        if any(w in cmd for w in ["empty recycle bin", "clean recycle bin", "clear recycle bin"]):
            sound_fx.play_success()
            return system_actions.empty_recycle_bin()

        if any(w in cmd for w in ["read clipboard", "what did i copy", "check clipboard", "paste clipboard"]):
            sound_fx.play_success()
            return system_actions.read_clipboard()

        type_match = re.search(r'type\s+(.+)', cmd)
        if type_match:
            text_to_type = type_match.group(1)
            sound_fx.play_success()
            return system_actions.type_text(text_to_type)

        press_match = re.search(r'press\s+(enter|space|escape|esc|backspace|tab)', cmd)
        if press_match:
            return system_actions.press_key(press_match.group(1))

        # -------------------------------------------------------------
        # 7. TIME, DATE & WEATHER
        # -------------------------------------------------------------
        if any(w in cmd for w in ["what time", "current time", "the time", "tell me the time"]):
            sound_fx.play_success()
            return web_actions.get_current_time()

        if any(w in cmd for w in ["what date", "today's date", "todays date", "current date", "what day"]):
            sound_fx.play_success()
            return web_actions.get_current_date()

        weather_match = re.search(r'weather(?:\s+in\s+([a-zA-Z\s]+))?', cmd)
        if "weather" in cmd or "temperature" in cmd:
            loc = weather_match.group(1) if weather_match and weather_match.group(1) else ""
            sound_fx.play_success()
            return web_actions.get_weather(loc)

        # -------------------------------------------------------------
        # 8. YOUTUBE & MUSIC PLAYBACK
        # -------------------------------------------------------------
        if any(w in cmd for w in ["pause music", "pause song", "pause video", "pause playback"]):
            sound_fx.play_success()
            return web_actions.media_control("pause")

        if any(w in cmd for w in ["resume music", "play music", "resume playback"]):
            sound_fx.play_success()
            return web_actions.media_control("play")

        if any(w in cmd for w in ["next song", "next track", "skip track", "skip song"]):
            sound_fx.play_success()
            return web_actions.media_control("next")

        if any(w in cmd for w in ["previous song", "previous track"]):
            sound_fx.play_success()
            return web_actions.media_control("previous")

        yt_play_match = re.search(r'play\s+(.+?)(?:\s+on\s+youtube)?$', cmd)
        if yt_play_match and not any(w in cmd for w in ["game", "with"]):
            song_query = yt_play_match.group(1).replace("on youtube", "").strip()
            sound_fx.play_success()
            return web_actions.play_youtube(song_query)

        yt_search_match = re.search(r'search\s+youtube\s+(?:for\s+)?(.+)', cmd)
        if yt_search_match:
            query = yt_search_match.group(1)
            sound_fx.play_success()
            return web_actions.search_youtube(query)

        # -------------------------------------------------------------
        # 9. GOOGLE SEARCH & WIKIPEDIA
        # -------------------------------------------------------------
        wiki_match = re.search(r'(?:who\s+is|what\s+is|summarize|tell\s+me\s+about)\s+(.+)', cmd)
        if wiki_match and not any(w in cmd for w in ["the time", "my battery", "my volume", "the weather", "temperature"]):
            subject = wiki_match.group(1).replace("on wikipedia", "").strip()
            sound_fx.play_success()
            return web_actions.get_wikipedia_summary(subject)

        google_search_match = re.search(r'(?:search\s+google\s+(?:for\s+)?|google\s+|search\s+for\s+)(.+)', cmd)
        if google_search_match:
            query = google_search_match.group(1)
            sound_fx.play_success()
            return web_actions.search_google(query)

        # -------------------------------------------------------------
        # 10. APPLICATION LAUNCHING & CLOSING
        # -------------------------------------------------------------
        close_match = re.search(r'(?:close|terminate|kill|quit)\s+([a-zA-Z\s0-9]+)', cmd)
        if close_match:
            app = close_match.group(1).strip()
            sound_fx.play_success()
            return system_actions.close_app(app)

        open_match = re.search(r'(?:open|launch|start)\s+([a-zA-Z\s0-9\.]+)', cmd)
        if open_match:
            target = open_match.group(1).strip()
            sound_fx.play_success()
            # Check if it's a website or app
            if target in config.WEB_BOOKMARKS or ".com" in target or ".org" in target:
                return web_actions.open_bookmark_or_url(target)
            return system_actions.launch_app(target)

        # -------------------------------------------------------------
        # 11. CONVERSATIONAL & STATUS
        # -------------------------------------------------------------
        if any(w in cmd for w in ["who are you", "what are you", "introduce yourself", "what can you do"]):
            return (
                f"I am {config.ASSISTANT_NAME}, your personal neural desktop assistant. "
                "I have direct telemetry and control over your laptop's hardware, applications, volume, display, "
                "power, and web functions. Simply speak my name or say 'Hey Jarvis' at any time."
            )

        if any(w in cmd for w in ["how are you", "how are you doing", "status check"]):
            return f"All core systems are nominal, {config.USER_NAME}. Ready for your directives."

        if any(w in cmd for w in ["thank you", "thanks jarvis", "thanks"]):
            return f"Always at your service, {config.USER_NAME}."

        if any(w in cmd for w in ["go to sleep", "stand down", "sleep jarvis", "be quiet", "stop listening"]):
            sound_fx.play_sleep()
            return f"Standing by in the background, {config.USER_NAME}. Say 'Hey Jarvis' whenever you need me."

        # -------------------------------------------------------------
        # 12. GENERAL FALLBACK (Google Search)
        # -------------------------------------------------------------
        # For general queries, perform a web search so the user's intent is answered
        sound_fx.play_success()
        return web_actions.search_google(cmd)


# Global singleton instance
commander = Commander()
