"""
JARVIS Desktop Command Center & Holographic Arc-Reactor HUD (Version 2.0)
Multi-tab workspace: Conversation / In-App Search Cards, System Control, Tasks, and Settings.
Full voice visualization, real-time status telemetry, and responsive modern styling.
"""
import math
import time
import datetime
import tkinter as tk
import customtkinter as ctk
import webbrowser

from engine.listener import listener
from engine.speaker import speaker
from engine.sound_effects import sound_fx
from engine.task_manager import task_manager, TaskState
from engine.conversation_manager import conv_manager
from engine.system_actions import system_actions
import config

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class JarvisHUD(ctk.CTk):
    def __init__(self, start_hidden: bool = False):
        super().__init__()

        self.title("J.A.R.V.I.S. Core Interface // MK-85 Advanced")
        self.geometry("960x780")
        self.minsize(820, 680)
        self.configure(fg_color=config.COLOR_BG_DARK)

        # State management
        self.current_state = "STANDBY"
        self.angle = 0
        self.pulse = 0
        self.pulse_dir = 1
        self.is_visible = not start_hidden

        # Wire callbacks
        listener.set_callbacks(
            state_callback=self.on_state_change,
            transcript_callback=self.on_transcript_event,
            wake_callback=self.on_wake_event,
            rich_callback=self.on_rich_event
        )
        speaker.status_callback = self.on_speaker_status
        task_manager.set_callback(self.on_task_state_change)

        self._build_ui()
        self._start_animation()

        if start_hidden:
            self.withdraw()
            self.is_visible = False

    def _build_ui(self):
        # ---------------- TOP NAVIGATION & TELEMETRY BAR ----------------
        self.top_bar = ctk.CTkFrame(self, fg_color=config.COLOR_BG_CARD, height=50, corner_radius=12)
        self.top_bar.pack(fill="x", padx=16, pady=(12, 6))

        self.lbl_brand = ctk.CTkLabel(
            self.top_bar,
            text="⚡ J.A.R.V.I.S. // AI DESKTOP OPERATING SYSTEM",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color=config.COLOR_ACCENT_CYAN
        )
        self.lbl_brand.pack(side="left", padx=16, pady=10)

        # Window Controls (Close to tray, Minimize)
        self.btn_close = ctk.CTkButton(
            self.top_bar, text="✕", width=32, height=28,
            fg_color="#3a1a23", hover_color="#5e2838", text_color="#ff4d6d",
            command=self.hide_to_background
        )
        self.btn_close.pack(side="right", padx=(2, 12), pady=10)

        self.btn_min = ctk.CTkButton(
            self.top_bar, text="—", width=32, height=28,
            fg_color="#1a233a", hover_color="#28385e", text_color=config.COLOR_ACCENT_CYAN,
            command=self.hide_to_background
        )
        self.btn_min.pack(side="right", padx=(2, 4), pady=10)

        self.lbl_telemetry = ctk.CTkLabel(
            self.top_bar,
            text=f"🎙️ {listener.active_mic_name[:22]}",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#00b4d8"
        )
        self.lbl_telemetry.pack(side="right", padx=14)

        # ---------------- MAIN CONTENT SPLIT LAYOUT ----------------
        self.main_split = ctk.CTkFrame(self, fg_color="transparent")
        self.main_split.pack(fill="both", expand=True, padx=16, pady=4)

        # LEFT SIDEBAR: Arc-Reactor Core + Assistant Status + Quick Actions
        self.left_pane = ctk.CTkFrame(self.main_split, fg_color=config.COLOR_BG_CARD, width=280, corner_radius=12)
        self.left_pane.pack(side="left", fill="y", padx=(0, 8), pady=0)
        self.left_pane.pack_propagate(False)

        # Arc Reactor Animation Canvas
        self.canvas_size = 180
        self.canvas = tk.Canvas(
            self.left_pane,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=config.COLOR_BG_CARD,
            highlightthickness=0
        )
        self.canvas.pack(pady=(16, 6))

        # Status Label
        self.lbl_status = ctk.CTkLabel(
            self.left_pane,
            text='STANDBY // SAY "HEY JARVIS"',
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color=config.COLOR_ACCENT_GLOW,
            wraplength=240
        )
        self.lbl_status.pack(pady=(0, 10))

        # Big Push-to-Talk / Wake Button
        self.btn_wake = ctk.CTkButton(
            self.left_pane,
            text="🎙️ WAKE JARVIS",
            height=40,
            fg_color="#006699",
            hover_color=config.COLOR_ACCENT_CYAN,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8,
            command=self.manual_wake
        )
        self.btn_wake.pack(fill="x", padx=16, pady=(0, 8))

        # Emergency Stop / Interrupt Button
        self.btn_stop_speaking = ctk.CTkButton(
            self.left_pane,
            text="⏹ STOP SPEECH / CANCEL",
            height=32,
            fg_color="#441a22",
            hover_color="#77202e",
            text_color="#ff7b90",
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=8,
            command=self.stop_current_operation
        )
        self.btn_stop_speaking.pack(fill="x", padx=16, pady=(0, 12))

        # Quick Control Grid
        self.lbl_quick_title = ctk.CTkLabel(
            self.left_pane, text="QUICK HARDWARE ACTIONS",
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            text_color="#6c82a3"
        )
        self.lbl_quick_title.pack(anchor="w", padx=16, pady=(4, 4))

        quick_btns = [
            ("⚡ System Diagnostic", lambda: self._quick_cmd("system report")),
            ("📸 Screen Capture", lambda: self._quick_cmd("take screenshot")),
            ("🔋 Battery Status", lambda: self._quick_cmd("battery status")),
            ("🖥️ Show Desktop", lambda: self._quick_cmd("show desktop")),
            ("🔇 Toggle Mute", lambda: self._quick_cmd("mute audio"))
        ]

        for label, cmd_fn in quick_btns:
            b = ctk.CTkButton(
                self.left_pane, text=label, height=28,
                fg_color="#162035", hover_color="#223152", text_color="#a0c4e2",
                font=ctk.CTkFont(size=11), corner_radius=6, command=cmd_fn
            )
            b.pack(fill="x", padx=16, pady=2)

        # RIGHT WORKSPACE: Multi-tab Views
        self.tabview = ctk.CTkTabview(
            self.main_split,
            fg_color=config.COLOR_BG_CARD,
            segmented_button_selected_color="#006699",
            segmented_button_selected_hover_color=config.COLOR_ACCENT_CYAN,
            corner_radius=12
        )
        self.tabview.pack(side="right", fill="both", expand=True)

        self.tab_conversation = self.tabview.add("💬 Conversation & Search")
        self.tab_system = self.tabview.add("🖥️ System Center")
        self.tab_tasks = self.tabview.add("⚙ Tasks & Notes")
        self.tab_settings = self.tabview.add("🔧 Settings")

        self._build_conversation_tab()
        self._build_system_tab()
        self._build_tasks_tab()
        self._build_settings_tab()

        # ---------------- BOTTOM TEXT & VOICE INPUT BAR ----------------
        self.bottom_bar = ctk.CTkFrame(self, fg_color=config.COLOR_BG_CARD, height=54, corner_radius=12)
        self.bottom_bar.pack(fill="x", padx=16, pady=(6, 14))

        self.entry_cmd = ctk.CTkEntry(
            self.bottom_bar,
            placeholder_text="Enter spoken command, search inquiry, or question (e.g. 'search for cybersecurity news', 'set volume 60')...",
            fg_color="#151d2f",
            border_color="#223150",
            text_color=config.COLOR_TEXT_MAIN,
            font=ctk.CTkFont(size=12),
            height=38,
            corner_radius=8
        )
        self.entry_cmd.pack(side="left", fill="x", expand=True, padx=(12, 6), pady=8)
        self.entry_cmd.bind("<Return>", lambda e: self.send_typed_cmd())

        self.btn_send = ctk.CTkButton(
            self.bottom_bar,
            text="EXECUTE ▶",
            width=100,
            height=38,
            fg_color="#1d2a45",
            hover_color=config.COLOR_ACCENT_CYAN,
            text_color="#ffffff",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
            command=self.send_typed_cmd
        )
        self.btn_send.pack(side="right", padx=(6, 12), pady=8)

    # ---------------- TAB 1: CONVERSATION & IN-APP SEARCH ----------------
    def _build_conversation_tab(self):
        tab = self.tab_conversation

        # Transcript Display
        self.transcript_box = ctk.CTkTextbox(
            tab,
            fg_color="#0c121e",
            text_color=config.COLOR_TEXT_MAIN,
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=8,
            wrap="word",
            height=260
        )
        self.transcript_box.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        self._add_terminal_log("JARVIS", "System active. In-app search & conversational reference resolution online.")

        # In-App Search Cards Container
        self.cards_frame = ctk.CTkScrollableFrame(tab, fg_color="#0a0f1a", height=180, corner_radius=8)
        self.cards_frame.pack(fill="x", padx=8, pady=(4, 8))

        self.lbl_cards_header = ctk.CTkLabel(
            self.cards_frame,
            text="🔍 Integrated Search Results (Cards appear here):",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color="#5ea8d6"
        )
        self.lbl_cards_header.pack(anchor="w", padx=6, pady=4)

    def display_search_cards(self, results: list):
        # Clear previous cards
        for widget in self.cards_frame.winfo_children():
            if widget != self.lbl_cards_header:
                widget.destroy()

        if not results:
            return

        for i, r in enumerate(results):
            card = ctk.CTkFrame(self.cards_frame, fg_color="#131d2e", corner_radius=8)
            card.pack(fill="x", padx=4, pady=4)

            title_row = ctk.CTkFrame(card, fg_color="transparent")
            title_row.pack(fill="x", padx=8, pady=(6, 2))

            lbl_t = ctk.CTkLabel(
                title_row,
                text=f"{i+1}. {r.get('title', 'No Title')}",
                font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                text_color=config.COLOR_ACCENT_CYAN,
                anchor="w"
            )
            lbl_t.pack(side="left", fill="x", expand=True)

            btn_open = ctk.CTkButton(
                title_row,
                text="Open in Browser ↗",
                width=110,
                height=24,
                font=ctk.CTkFont(size=10),
                fg_color="#1e2c45",
                hover_color="#006699",
                command=lambda url=r.get('url', ''): webbrowser.open(url) if url else None
            )
            btn_open.pack(side="right")

            snippet_text = r.get('snippet', '')[:160]
            lbl_s = ctk.CTkLabel(
                card,
                text=snippet_text,
                font=ctk.CTkFont(size=11),
                text_color="#a8b5c9",
                anchor="w",
                justify="left",
                wraplength=560
            )
            lbl_s.pack(fill="x", padx=8, pady=(0, 6))

    # ---------------- TAB 2: SYSTEM CENTER ----------------
    def _build_system_tab(self):
        tab = self.tab_system

        self.sys_info_box = ctk.CTkTextbox(tab, fg_color="#0c121e", font=ctk.CTkFont(family="Consolas", size=12), corner_radius=8, height=180)
        self.sys_info_box.pack(fill="both", expand=True, padx=8, pady=8)
        self._refresh_sys_info()

        btn_refresh = ctk.CTkButton(tab, text="🔄 Refresh Hardware Diagnostic", command=self._refresh_sys_info, height=32)
        btn_refresh.pack(padx=8, pady=4)

    def _refresh_sys_info(self):
        report = system_actions.get_system_report()
        batt = system_actions.get_battery_status()
        vol = system_actions.get_volume()
        bright = system_actions.get_brightness()

        text = (
            f"=== REAL-TIME TELEMETRY ===\n\n"
            f"{report}\n\n"
            f"Battery Level: {batt}\n"
            f"Master Volume: {vol}%\n"
            f"Display Brightness: {bright}%\n"
            f"Active Audio Input: {listener.active_mic_name}\n"
        )
        self.sys_info_box.configure(state="normal")
        self.sys_info_box.delete("1.0", "end")
        self.sys_info_box.insert("end", text)
        self.sys_info_box.configure(state="disabled")

    # ---------------- TAB 3: TASKS & NOTES ----------------
    def _build_tasks_tab(self):
        tab = self.tab_tasks

        self.tasks_box = ctk.CTkTextbox(tab, fg_color="#0c121e", font=ctk.CTkFont(family="Consolas", size=12), corner_radius=8)
        self.tasks_box.pack(fill="both", expand=True, padx=8, pady=8)
        self._refresh_tasks_view()

    def _refresh_tasks_view(self):
        notes = conv_manager.get_notes()
        history = task_manager.task_history[-10:]

        content = "=== SAVED NOTES ===\n"
        if notes:
            for n in notes:
                content += f"[{n['created_at']}] Note #{n['id']}: {n['content']}\n"
        else:
            content += "(No saved notes yet. Say 'Take a note [text]' to create one.)\n"

        content += "\n=== RECENT COMPLETED TASKS ===\n"
        if history:
            for t in history:
                dur = round(t.end_time - t.start_time, 2) if t.end_time else 0
                content += f"[{t.status}] {t.description} ({dur}s)\n"
        else:
            content += "(No recent tasks.)\n"

        self.tasks_box.configure(state="normal")
        self.tasks_box.delete("1.0", "end")
        self.tasks_box.insert("end", content)
        self.tasks_box.configure(state="disabled")

    # ---------------- TAB 4: SETTINGS ----------------
    def _build_settings_tab(self):
        tab = self.tab_settings

        lbl_set = ctk.CTkLabel(tab, text="CONFIGURATION & PREFERENCES", font=ctk.CTkFont(family="Consolas", size=14, weight="bold"), text_color=config.COLOR_ACCENT_CYAN)
        lbl_set.pack(anchor="w", padx=12, pady=(12, 8))

        # Microphone dropdown
        lbl_m = ctk.CTkLabel(tab, text=f"Active Microphone Device: {listener.active_mic_name}", font=ctk.CTkFont(size=12))
        lbl_m.pack(anchor="w", padx=12, pady=4)

        # Voice preference
        lbl_v = ctk.CTkLabel(tab, text=f"Voice Engine: {config.EDGE_TTS_VOICE} (British Neural)", font=ctk.CTkFont(size=12))
        lbl_v.pack(anchor="w", padx=12, pady=4)

        # Wake words list
        lbl_w = ctk.CTkLabel(tab, text=f"Recognized Wake Words: {', '.join(config.WAKE_WORDS)}", font=ctk.CTkFont(size=12))
        lbl_w.pack(anchor="w", padx=12, pady=4)

        btn_clear = ctk.CTkButton(tab, text="🗑 Clear Conversation Memory", fg_color="#3a1a23", hover_color="#5e2838", command=lambda: self._quick_cmd("clear conversation"))
        btn_clear.pack(anchor="w", padx=12, pady=(16, 4))

    # ---------------- COMMAND DISPATCH & INTERACTIONS ----------------
    def _quick_cmd(self, cmd_text: str):
        self.entry_cmd.delete(0, "end")
        self.entry_cmd.insert(0, cmd_text)
        self.send_typed_cmd()

    def send_typed_cmd(self):
        text = self.entry_cmd.get().strip()
        if text:
            self.entry_cmd.delete(0, "end")
            import threading
            threading.Thread(target=listener.process_typed_command, args=(text,), daemon=True).start()

    def stop_current_operation(self):
        speaker.stop()
        task_manager.cancel_active_tasks()
        sound_fx.play_alert()
        self._add_terminal_log("SYSTEM", "User interrupted speech playback and active tasks.")

    def manual_wake(self):
        self.wake_on_desktop()
        listener.trigger_wake_manually()

    def hide_to_background(self):
        self.withdraw()
        self.is_visible = False

    def wake_on_desktop(self):
        self.after(0, self._bring_to_front)

    def _bring_to_front(self):
        try:
            self.deiconify()
            self.lift()
            self.attributes('-topmost', True)
            self.focus_force()
            self.is_visible = True
            self.after(2500, lambda: self.attributes('-topmost', False))
        except Exception:
            pass

    def _add_terminal_log(self, sender: str, message: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.transcript_box.configure(state="normal")
        if sender.upper() == "USER":
            tag = f"\n[{timestamp}] YOU > {message}\n"
        else:
            tag = f"[{timestamp}] JARVIS > {message}\n"
        self.transcript_box.insert("end", tag)
        self.transcript_box.see("end")
        self.transcript_box.configure(state="disabled")

    # ---------------- EVENT CALLBACKS ----------------
    def on_state_change(self, state: str, detail: str = ""):
        self.current_state = state
        self.after(0, lambda: self._update_status_label(state, detail))

    def on_task_state_change(self, state: TaskState, detail: str = ""):
        self.current_state = state.value
        self.after(0, lambda: self._update_status_label(state.value, detail))

    def _update_status_label(self, state: str, detail: str):
        if hasattr(self, 'lbl_telemetry'):
            self.lbl_telemetry.configure(text=f"🎙️ {listener.active_mic_name[:22]}")

        if state == "IDLE" or state == "STANDBY":
            self.lbl_status.configure(text='STANDBY // SAY "HEY JARVIS"', text_color=config.COLOR_ACCENT_GLOW)
            self.btn_wake.configure(fg_color="#006699")
        elif state == "LISTENING":
            self.lbl_status.configure(text="● ACTIVE LISTENING // SPEAK NOW", text_color=config.COLOR_ACCENT_GREEN)
            self.btn_wake.configure(fg_color="#00b4d8")
        elif state == "THINKING" or state == "PROCESSING":
            self.lbl_status.configure(text=f"⚙ {detail or 'ANALYZING...'}", text_color=config.COLOR_ACCENT_AMBER)
        elif state == "SPEAKING":
            self.lbl_status.configure(text="🔊 JARVIS TRANSMITTING...", text_color=config.COLOR_ACCENT_CYAN)
        elif state == "WAITING_FOR_CONFIRMATION":
            self.lbl_status.configure(text=f"⚠️ {detail}", text_color="#ff4d6d")

    def on_transcript_event(self, sender: str, text: str):
        self.after(0, lambda: self._add_terminal_log(sender, text))
        self.after(0, self._refresh_tasks_view)

    def on_wake_event(self):
        self.wake_on_desktop()

    def on_rich_event(self, structured_res: dict):
        if structured_res.get("type") == "search_results":
            results = structured_res.get("data", [])
            self.after(0, lambda: self.display_search_cards(results))

    def on_speaker_status(self, state: str, text: str):
        if state == "SPEAKING":
            self.on_state_change("SPEAKING", text)
        else:
            self.on_state_change("IDLE", "")

    # ---------------- ARC REACTOR CANVAS DRAWING ----------------
    def _start_animation(self):
        self._animate_arc_reactor()

    def _animate_arc_reactor(self):
        self.angle = (self.angle + 4) % 360
        self.pulse += 0.08 * self.pulse_dir
        if self.pulse >= 1.0:
            self.pulse = 1.0
            self.pulse_dir = -1
        elif self.pulse <= 0.0:
            self.pulse = 0.0
            self.pulse_dir = 1

        self.canvas.delete("all")
        cx = self.canvas_size / 2
        cy = self.canvas_size / 2

        if self.current_state == "LISTENING":
            core_color = "#00f5d4"
            ring_color = "#00e5ff"
            glow_radius = 52 + int(self.pulse * 12)
        elif self.current_state in ["THINKING", "PROCESSING", "EXECUTING"]:
            core_color = "#ffb703"
            ring_color = "#fb8500"
            glow_radius = 48 + int(self.pulse * 8)
        elif self.current_state == "SPEAKING":
            core_color = "#00e5ff"
            ring_color = "#7b2cbf"
            glow_radius = 54 + int(self.pulse * 10)
        elif self.current_state == "WAITING_FOR_CONFIRMATION":
            core_color = "#ff4d6d"
            ring_color = "#c9184a"
            glow_radius = 50 + int(self.pulse * 8)
        else:  # STANDBY / IDLE
            core_color = "#0077b6"
            ring_color = "#0096c7"
            glow_radius = 44 + int(self.pulse * 4)

        # Outer tech ring with ticks
        outer_r = 80
        self.canvas.create_oval(cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r, outline="#16223b", width=2)

        num_ticks = 12
        for i in range(num_ticks):
            deg = self.angle + (i * (360 / num_ticks))
            rad = math.radians(deg)
            x1 = cx + (outer_r - 8) * math.cos(rad)
            y1 = cy + (outer_r - 8) * math.sin(rad)
            x2 = cx + outer_r * math.cos(rad)
            y2 = cy + outer_r * math.sin(rad)
            self.canvas.create_line(x1, y1, x2, y2, fill=ring_color, width=2)

        # Middle energy ring
        mid_r = 58
        self.canvas.create_oval(cx - mid_r, cy - mid_r, cx + mid_r, cy + mid_r, outline=ring_color, width=2)

        # Inner pulsing core
        self.canvas.create_oval(cx - glow_radius, cy - glow_radius, cx + glow_radius, cy + glow_radius, fill="#0d1f3d", outline=ring_color, width=3)
        core_r = 25 + int(self.pulse * 4)
        self.canvas.create_oval(cx - core_r, cy - core_r, cx + core_r, cy + core_r, fill=core_color, outline="#ffffff", width=2)

        # Center bright pinpoint
        self.canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="#ffffff", outline="")

        self.after(50, self._animate_arc_reactor)


def start_hud(hidden: bool = False):
    app = JarvisHUD(start_hidden=hidden)
    app.mainloop()

if __name__ == "__main__":
    start_hud(hidden=False)
