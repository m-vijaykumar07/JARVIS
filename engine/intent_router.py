"""
JARVIS Advanced Intent Classifier & Natural Language Router
Parses natural language requests into structured intents, extracts entities,
resolves contextual references, enforces security, and triggers tools.
"""
import re
from typing import Dict, Any, Optional

from engine.task_manager import task_manager, TaskState
from engine.conversation_manager import conv_manager
from engine.system_actions import system_actions
from engine.web_actions import web_actions
from engine.web_engine import web_engine
from engine.ai_brain import ai_brain
from engine.sound_effects import sound_fx
from engine.speaker import speaker
from engine.security import SecurityPolicy
import config

class IntentRouter:
    def __init__(self, ui_callback: Optional[Any] = None):
        self.ui_callback = ui_callback

    def route_and_execute(self, text: str) -> Dict[str, Any]:
        """
        Main entry point for user requests. Returns a structured result:
        {
            "spoken": str,
            "display": str,
            "type": str ("text", "search_results", "system", "status"),
            "data": Any
        }
        """
        if not text or not text.strip():
            return {"spoken": "", "display": "", "type": "empty", "data": None}

        raw = SecurityPolicy.sanitize_input(text)
        cmd = raw.lower()

        # Check wake words and strip them
        for wake in config.WAKE_WORDS:
            if cmd.startswith(wake):
                cmd = cmd[len(wake):].strip()
                break

        # -------------------------------------------------------------
        # 1. IMMEDIATE INTERRUPTION / LIFECYCLE CONTROLS
        # -------------------------------------------------------------
        if any(term in cmd for term in ["stop speaking", "be quiet", "shut up", "silence", "stop talking", "mute voice"]):
            speaker.stop()
            task_manager.set_state(TaskState.IDLE, "Speech Stopped")
            return {"spoken": "", "display": "Speech interrupted.", "type": "status", "data": None}

        if any(term in cmd for term in ["cancel this task", "cancel task", "stop task", "exit this task", "abort operation"]):
            speaker.stop()
            cancelled = task_manager.cancel_active_tasks()
            sound_fx.play_alert()
            resp = f"Cancelled {cancelled} active task(s), sir." if cancelled else "No cancellable tasks active, sir."
            return {"spoken": resp, "display": resp, "type": "status", "data": None}

        if any(term in cmd for term in ["clear conversation", "clear history", "reset memory"]):
            conv_manager.clear_history()
            sound_fx.play_success()
            msg = "Conversation memory cleared, sir."
            return {"spoken": msg, "display": msg, "type": "status", "data": None}

        # Handle pending confirmation (e.g. "yes", "confirm", "no", "cancel")
        if task_manager.has_pending_confirmation():
            if any(yes in cmd for yes in ["yes", "confirm", "proceed", "do it", "sure"]):
                res = task_manager.resolve_confirmation(True)
                sound_fx.play_success()
                return {"spoken": res, "display": res, "type": "system", "data": None}
            elif any(no in cmd for no in ["no", "cancel", "stop", "abort", "don't"]):
                res = task_manager.resolve_confirmation(False)
                sound_fx.play_alert()
                return {"spoken": res, "display": res, "type": "system", "data": None}

        # -------------------------------------------------------------
        # 2. CONTEXTUAL REFERENCE RESOLUTION ('first result', 'that website', 'explain it')
        # -------------------------------------------------------------
        # User says: "explain the first result", "explain it", "tell me more about the second one"
        if any(phrase in cmd for phrase in ["explain the", "explain it", "tell me about the", "what is the first", "what about the second"]):
            ref = conv_manager.resolve_reference(cmd)
            if ref:
                task = task_manager.create_task(f"Explaining {ref['title']}")
                task_manager.set_state(TaskState.THINKING, f"Analyzing {ref['title']}...")
                snippet = ref.get("snippet", "")
                ans = ai_brain.generate_response(f"Explain this search result to me: {ref['title']}", context=snippet)
                task_manager.complete_task(task.task_id)
                task_manager.set_state(TaskState.IDLE)
                conv_manager.add_turn("user", raw)
                conv_manager.add_turn("assistant", ans)
                return {"spoken": ans, "display": f"**{ref['title']}**\n\n{ans}", "type": "ai_response", "data": ref}

        # User says: "open that website", "open the first result", "open this page"
        if any(phrase in cmd for phrase in ["open that website", "open this website", "open that page", "open the first result", "open the second result", "open it in chrome", "open this link"]):
            ref = conv_manager.resolve_reference(cmd)
            if ref and ref.get("url"):
                web_actions.open_bookmark_or_url(ref["url"])
                msg = f"Opening {ref['title']} in your browser, sir."
                return {"spoken": msg, "display": f"Opened: [{ref['title']}]({ref['url']})", "type": "system", "data": ref}

        # User says: "summarize this page", "summarize the first result", "summarize that website"
        if any(phrase in cmd for phrase in ["summarize this page", "summarize the page", "summarize that website", "summarize this website", "summarize the first result"]):
            ref = conv_manager.resolve_reference(cmd)
            if ref and ref.get("url"):
                task = task_manager.create_task(f"Summarizing {ref['title']}")
                task_manager.set_state(TaskState.THINKING, f"Extracting {ref['url']}...")
                page_text = web_engine.extract_page_text(ref["url"])
                summary = ai_brain.generate_response(f"Summarize this web page concisely for voice output: {ref['title']}", context=page_text)
                task_manager.complete_task(task.task_id)
                task_manager.set_state(TaskState.IDLE)
                conv_manager.add_turn("user", raw)
                conv_manager.add_turn("assistant", summary)
                return {
                    "spoken": summary,
                    "display": f"### Summary: {ref['title']}\n\n{summary}\n\n*Source: {ref['url']}*",
                    "type": "summary",
                    "data": ref
                }

        # -------------------------------------------------------------
        # 3. IN-APP WEB SEARCH (DO NOT REDIRECT TO CHROME UNLESS REQUESTED)
        # -------------------------------------------------------------
        search_match = re.search(r'^(?:search\s+for|search\s+the\s+web\s+for|find\s+information\s+on|look\s+up|search)\s+(.+)', cmd)
        if search_match and not any(ext in cmd for ext in ["in chrome", "in browser", "youtube"]):
            query = search_match.group(1).strip()
            task = task_manager.create_task(f"Searching web for: {query}")
            task_manager.set_state(TaskState.THINKING, f"Searching for '{query}'...")

            results = web_engine.search_in_app(query, max_results=4)
            conv_manager.set_search_results(results)

            if results:
                # Synthesize a smart summary of top results
                context = "\n".join([f"{i+1}. {r['title']}: {r['snippet']}" for i, r in enumerate(results)])
                spoken_ans = ai_brain.generate_response(f"Summarize these search results for query '{query}' in two natural sentences.", context=context)
                task_manager.complete_task(task.task_id)
                task_manager.set_state(TaskState.IDLE)
                conv_manager.add_turn("user", raw)
                conv_manager.add_turn("assistant", spoken_ans, metadata={"results": results})

                return {
                    "spoken": spoken_ans,
                    "display": f"### Search Results: *{query}*\n\n{spoken_ans}",
                    "type": "search_results",
                    "data": results
                }
            else:
                task_manager.complete_task(task.task_id, status="ERROR")
                task_manager.set_state(TaskState.IDLE)
                msg = f"I was unable to retrieve search results for {query} at this moment, sir."
                return {"spoken": msg, "display": msg, "type": "error", "data": None}

        # -------------------------------------------------------------
        # 4. EXPLICIT BROWSER LAUNCHES & SEARCH IN CHROME
        # -------------------------------------------------------------
        if any(term in cmd for term in ["open chrome", "launch chrome", "open browser", "open google chrome"]):
            sound_fx.play_success()
            resp = system_actions.launch_app("chrome")
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        if "search in chrome" in cmd or "search on google" in cmd:
            q = re.sub(r'.*?(?:search\s+in\s+chrome\s+for|search\s+on\s+google\s+for|search\s+google\s+for)\s+', '', cmd).strip()
            resp = web_actions.search_google(q)
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        # -------------------------------------------------------------
        # 5. WINDOWS HARDWARE & SYSTEM CONTROLS
        # -------------------------------------------------------------
        # Audio Volume
        if any(w in cmd for w in ["mute audio", "mute sound", "mute volume", "mute"]):
            sound_fx.play_success()
            resp = system_actions.mute_volume()
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        if any(w in cmd for w in ["unmute audio", "unmute sound", "unmute volume", "unmute"]):
            sound_fx.play_success()
            resp = system_actions.unmute_volume()
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        vol_match = re.search(r'(?:set\s+)?volume\s+(?:to\s+)?(\d{1,3})', cmd)
        if vol_match:
            level = int(vol_match.group(1))
            sound_fx.play_success()
            resp = system_actions.set_volume(level)
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        if any(w in cmd for w in ["volume up", "increase volume", "raise volume", "louder", "make it louder"]):
            sound_fx.play_success()
            resp = system_actions.change_volume(+15)
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        if any(w in cmd for w in ["volume down", "decrease volume", "lower volume", "quieter", "make it quieter", "make the sound quieter"]):
            sound_fx.play_success()
            resp = system_actions.change_volume(-15)
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        # Brightness
        bright_match = re.search(r'(?:set\s+)?brightness\s+(?:to\s+)?(\d{1,3})', cmd)
        if bright_match:
            level = int(bright_match.group(1))
            sound_fx.play_success()
            resp = system_actions.set_brightness(level)
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        if any(w in cmd for w in ["brightness up", "increase brightness", "brighter"]):
            sound_fx.play_success()
            resp = system_actions.change_brightness(+15)
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        if any(w in cmd for w in ["brightness down", "decrease brightness", "dim screen", "dim display"]):
            sound_fx.play_success()
            resp = system_actions.change_brightness(-15)
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        # Battery & System Diagnostics
        if any(w in cmd for w in ["battery", "battery level", "power status", "how much battery"]):
            sound_fx.play_success()
            resp = system_actions.get_battery_status()
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        if any(w in cmd for w in ["system report", "system status", "diagnostic", "cpu usage", "ram usage", "pc performance"]):
            sound_fx.play_success()
            resp = system_actions.get_system_report()
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        # Screenshot
        if any(w in cmd for w in ["take screenshot", "capture screen", "screenshot"]):
            sound_fx.play_success()
            resp = system_actions.take_screenshot()
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        # Recycle Bin (Requires Confirmation)
        if any(w in cmd for w in ["empty recycle bin", "clean recycle bin", "clear recycle bin"]):
            task_manager.set_pending_confirmation(
                "Empty Recycle Bin",
                lambda: system_actions.empty_recycle_bin(),
                "Are you sure you want to permanently empty the Recycle Bin, sir?"
            )
            return {
                "spoken": "Are you sure you want to permanently empty the Recycle Bin, sir?",
                "display": "⚠️ **Confirmation Required:** Empty Recycle Bin? (Say 'Yes' or 'Confirm')",
                "type": "confirmation",
                "data": None
            }

        # Lock Workstation
        if any(w in cmd for w in ["lock laptop", "lock pc", "lock computer", "lock screen", "lock workstation"]):
            sound_fx.play_alert()
            resp = system_actions.lock_workstation()
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        # Shutdown / Restart (Requires Confirmation)
        if any(w in cmd for w in ["shutdown laptop", "shutdown pc", "turn off laptop", "turn off pc"]):
            task_manager.set_pending_confirmation(
                "Shutdown System",
                lambda: system_actions.shutdown_laptop(),
                "Confirming system shutdown. Shall I proceed, sir?"
            )
            return {
                "spoken": "Confirming system shutdown. Shall I proceed, sir?",
                "display": "⚠️ **Confirmation Required:** Shutdown Laptop? (Say 'Yes' to confirm)",
                "type": "confirmation",
                "data": None
            }

        # Window Controls
        if any(w in cmd for w in ["show desktop", "minimize all", "go to desktop"]):
            sound_fx.play_success()
            resp = system_actions.show_desktop()
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        if any(w in cmd for w in ["switch window", "next window", "alt tab"]):
            sound_fx.play_success()
            resp = system_actions.switch_window()
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        if any(w in cmd for w in ["maximize window", "maximize"]):
            sound_fx.play_success()
            resp = system_actions.maximize_window()
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        if any(w in cmd for w in ["minimize window", "minimize this"]):
            sound_fx.play_success()
            resp = system_actions.minimize_window()
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        # -------------------------------------------------------------
        # 6. PRODUCTIVITY, NOTES, REMINDERS
        # -------------------------------------------------------------
        note_match = re.search(r'(?:take\s+a\s+note|save\s+note|note\s+that|write\s+down)\s+(.+)', cmd)
        if note_match:
            note_text = note_match.group(1).strip()
            resp = conv_manager.add_note(note_text)
            sound_fx.play_success()
            return {"spoken": resp, "display": f"📝 **Saved Note:** {note_text}", "type": "note", "data": note_text}

        if any(w in cmd for w in ["read notes", "show notes", "what are my notes", "get notes"]):
            notes = conv_manager.get_notes()
            if notes:
                text_list = "\n".join([f"{n['id']}. {n['content']} ({n['created_at']})" for n in notes[-5:]])
                spoken = f"You have {len(notes)} notes. The most recent is: {notes[-1]['content']}."
                return {"spoken": spoken, "display": f"### Your Saved Notes:\n\n{text_list}", "type": "notes_list", "data": notes}
            else:
                return {"spoken": "You have no saved notes, sir.", "display": "No notes saved yet.", "type": "status", "data": None}

        # Clipboard
        if any(w in cmd for w in ["read clipboard", "what is on my clipboard", "check clipboard"]):
            resp = system_actions.read_clipboard()
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        # Time & Date
        if any(w in cmd for w in ["what time", "current time", "the time"]):
            resp = web_actions.get_current_time()
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        if any(w in cmd for w in ["what date", "today's date", "todays date"]):
            resp = web_actions.get_current_date()
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        # Weather
        if "weather" in cmd or "temperature" in cmd:
            w_match = re.search(r'weather(?:\s+in\s+([a-zA-Z\s]+))?', cmd)
            loc = w_match.group(1) if w_match and w_match.group(1) else ""
            resp = web_actions.get_weather(loc)
            return {"spoken": resp, "display": resp, "type": "system", "data": None}

        # -------------------------------------------------------------
        # 7. APPS LAUNCH & TERMINATION
        # -------------------------------------------------------------
        close_match = re.search(r'(?:close|terminate|kill|quit)\s+([a-zA-Z\s0-9]+)', cmd)
        if close_match:
            app = close_match.group(1).strip()
            if SecurityPolicy.validate_app_name(app):
                sound_fx.play_success()
                resp = system_actions.close_app(app)
                return {"spoken": resp, "display": resp, "type": "system", "data": None}

        open_match = re.search(r'(?:open|launch|start|bring\s+up)\s+([a-zA-Z\s0-9\.]+)', cmd)
        if open_match:
            target = open_match.group(1).strip()
            if SecurityPolicy.validate_app_name(target):
                sound_fx.play_success()
                if target in config.WEB_BOOKMARKS or ".com" in target or ".org" in target:
                    resp = web_actions.open_bookmark_or_url(target)
                else:
                    resp = system_actions.launch_app(target)
                return {"spoken": resp, "display": resp, "type": "system", "data": None}

        # -------------------------------------------------------------
        # 8. ASSISTANT IDENTITY & CONVERSATIONAL COURTESY
        # -------------------------------------------------------------
        if any(w in cmd for w in ["who are you", "what are you", "introduce yourself", "what can you do"]):
            intro = (
                f"I am {config.ASSISTANT_NAME}, your personal neural desktop assistant. "
                "I have direct telemetry and control over your laptop's hardware, applications, volume, display, "
                "power, in-app web search, and notes. Simply speak my name or say 'Hey Jarvis' at any time."
            )
            return {"spoken": intro, "display": intro, "type": "ai_response", "data": None}

        if any(w in cmd for w in ["how are you", "how are you doing", "status check"]):
            stat = f"All core systems are nominal, {config.USER_NAME}. Ready for your directives."
            return {"spoken": stat, "display": stat, "type": "ai_response", "data": None}

        if any(w in cmd for w in ["thank you", "thanks jarvis", "thanks"]):
            thx = f"Always at your service, {config.USER_NAME}."
            return {"spoken": thx, "display": thx, "type": "ai_response", "data": None}

        # -------------------------------------------------------------
        # 8b. VOICE SWITCH COMMAND
        # -------------------------------------------------------------
        if any(w in cmd for w in ["switch to suvi voice", "use suvi voice", "enable suvi voice", "suvi voice on"]):
            config.USE_CLONED_VOICE = True
            msg = "Switched to Suvi cloned voice mode."
            return {"spoken": msg, "display": msg, "type": "system", "data": None}

        if any(w in cmd for w in ["switch to jarvis voice", "use jarvis voice", "use neural voice", "disable suvi voice", "suvi voice off"]):
            config.USE_CLONED_VOICE = False
            msg = "Switched to Edge-TTS neural voice mode."
            return {"spoken": msg, "display": msg, "type": "system", "data": None}

        # -------------------------------------------------------------
        # 9. GENERAL CONVERSATIONAL AI INTELLIGENCE (Contextual Multi-turn)
        # -------------------------------------------------------------
        task_manager.set_state(TaskState.THINKING, "Formulating response...")
        conv_manager.add_turn("user", raw)
        
        # Build multi-turn context
        history_snippet = "\n".join([f"{t['role'].capitalize()}: {t['content']}" for t in conv_manager.history[-6:]])
        ans = ai_brain.generate_response(raw, context=history_snippet)
        
        task_manager.set_state(TaskState.IDLE)
        conv_manager.add_turn("assistant", ans)

        return {
            "spoken": ans,
            "display": ans,
            "type": "ai_response",
            "data": None
        }

# Global intent router
intent_router = IntentRouter()
