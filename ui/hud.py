"""
JARVIS Desktop Arc-Reactor HUD
Futuristic Sci-Fi holographic interface with dynamic arc reactor animations,
real-time transcript feeds, quick controls, and automatic desktop wake surfacing.
"""
import math
import time
import datetime
import tkinter as tk
import customtkinter as ctk
from engine.listener import listener
from engine.speaker import speaker
from engine.sound_effects import sound_fx
import config

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class JarvisHUD(ctk.CTk):
    def __init__(self, start_hidden: bool = False):
        super().__init__()

        self.title("J.A.R.V.I.S. Core Interface")
        self.geometry("500x740")
        self.minsize(440, 620)
        self.configure(fg_color=config.COLOR_BG_DARK)

        # State management
        self.current_state = "STANDBY"
        self.angle = 0
        self.pulse = 0
        self.pulse_dir = 1
        self.is_visible = not start_hidden

        # Register callbacks with listener and speaker
        listener.set_callbacks(
            state_callback=self.on_state_change,
            transcript_callback=self.on_transcript_event,
            wake_callback=self.on_wake_event
        )
        speaker.status_callback = self.on_speaker_status

        self._build_ui()
        self._start_animation()

        if start_hidden:
            self.withdraw()
            self.is_visible = False

    def _build_ui(self):
        # ---------------- Top Header Bar ----------------
        self.header_frame = ctk.CTkFrame(self, fg_color=config.COLOR_BG_CARD, height=45, corner_radius=12)
        self.header_frame.pack(fill="x", padx=14, pady=(12, 4))

        self.lbl_title = ctk.CTkLabel(
            self.header_frame,
            text="⚡ J.A.R.V.I.S. // MK-85",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color=config.COLOR_ACCENT_CYAN
        )
        self.lbl_title.pack(side="left", padx=16, pady=8)

        # Close/Hide to background button
        self.btn_close = ctk.CTkButton(
            self.header_frame,
            text="✕",
            width=32,
            height=28,
            fg_color="#3a1a23",
            hover_color="#5e2838",
            text_color="#ff4d6d",
            command=self.hide_to_background
        )
        self.btn_close.pack(side="right", padx=(2, 10), pady=6)

        # Minimize button
        self.btn_min = ctk.CTkButton(
            self.header_frame,
            text="—",
            width=32,
            height=28,
            fg_color="#1a233a",
            hover_color="#28385e",
            text_color=config.COLOR_ACCENT_CYAN,
            command=self.hide_to_background
        )
        self.btn_min.pack(side="right", padx=(2, 4), pady=6)

        # ---------------- Active Microphone Indicator ----------------
        self.mic_info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mic_info_frame.pack(fill="x", padx=16, pady=(2, 2))

        self.lbl_mic = ctk.CTkLabel(
            self.mic_info_frame,
            text=f"🎙️ Mic: {listener.active_mic_name[:32]}",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#00b4d8"
        )
        self.lbl_mic.pack(side="left")

        # ---------------- Arc Reactor Canvas ----------------
        self.canvas_size = 170
        self.canvas = tk.Canvas(
            self,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=config.COLOR_BG_DARK,
            highlightthickness=0
        )
        self.canvas.pack(pady=(4, 2))

        # ---------------- Status Indicator Banner ----------------
        self.lbl_status = ctk.CTkLabel(
            self,
            text='STANDBY // SAY "HEY JARVIS"',
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color=config.COLOR_ACCENT_GLOW
        )
        self.lbl_status.pack(pady=(0, 6))

        # ---------------- Quick Action Buttons ----------------
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.pack(fill="x", padx=14, pady=4)

        btn_style = {
            "height": 28,
            "corner_radius": 8,
            "font": ctk.CTkFont(size=11, weight="bold"),
            "fg_color": "#162035",
            "hover_color": "#223152",
            "text_color": "#a0c4e2"
        }

        self.btn_action1 = ctk.CTkButton(self.actions_frame, text="⚡ Diagnostic", command=lambda: self._quick_cmd("system report"), **btn_style)
        self.btn_action1.pack(side="left", expand=True, fill="x", padx=3)

        self.btn_action2 = ctk.CTkButton(self.actions_frame, text="📸 Capture", command=lambda: self._quick_cmd("take screenshot"), **btn_style)
        self.btn_action2.pack(side="left", expand=True, fill="x", padx=3)

        self.btn_action3 = ctk.CTkButton(self.actions_frame, text="🔋 Battery", command=lambda: self._quick_cmd("battery status"), **btn_style)
        self.btn_action3.pack(side="left", expand=True, fill="x", padx=3)

        self.btn_action4 = ctk.CTkButton(self.actions_frame, text="🖥️ Desktop", command=lambda: self._quick_cmd("show desktop"), **btn_style)
        self.btn_action4.pack(side="left", expand=True, fill="x", padx=3)

        # ---------------- Transcript Terminal Display ----------------
        self.transcript_box = ctk.CTkTextbox(
            self,
            fg_color=config.COLOR_BG_CARD,
            text_color=config.COLOR_TEXT_MAIN,
            font=ctk.CTkFont(family="Consolas", size=12),
            corner_radius=12,
            wrap="word"
        )
        self.transcript_box.pack(fill="both", expand=True, padx=14, pady=8)
        self._add_terminal_log("JARVIS", "Core online. Acoustic surveillance engaged. Say 'Hey Jarvis' to wake.")

        # ---------------- Bottom Command Bar ----------------
        self.bottom_frame = ctk.CTkFrame(self, fg_color=config.COLOR_BG_CARD, height=52, corner_radius=12)
        self.bottom_frame.pack(fill="x", padx=14, pady=(2, 14))

        # Wake Mic Button
        self.btn_mic = ctk.CTkButton(
            self.bottom_frame,
            text="🎙️ WAKE",
            width=80,
            height=36,
            fg_color="#006699",
            hover_color=config.COLOR_ACCENT_CYAN,
            text_color="#ffffff",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
            command=self.manual_wake
        )
        self.btn_mic.pack(side="left", padx=(10, 6), pady=8)

        # Text input field
        self.entry_cmd = ctk.CTkEntry(
            self.bottom_frame,
            placeholder_text="Voice or text command (e.g. open chrome, volume 70)...",
            fg_color="#151d2f",
            border_color="#223150",
            text_color=config.COLOR_TEXT_MAIN,
            font=ctk.CTkFont(size=12),
            height=36,
            corner_radius=8
        )
        self.entry_cmd.pack(side="left", fill="x", expand=True, padx=4, pady=8)
        self.entry_cmd.bind("<Return>", lambda e: self.send_typed_cmd())

        # Send Button
        self.btn_send = ctk.CTkButton(
            self.bottom_frame,
            text="▶",
            width=42,
            height=36,
            fg_color="#1d2a45",
            hover_color=config.COLOR_ACCENT_CYAN,
            text_color="#ffffff",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8,
            command=self.send_typed_cmd
        )
        self.btn_send.pack(side="right", padx=(6, 10), pady=8)

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

    def manual_wake(self):
        """Manually trigger wake state."""
        self.wake_on_desktop()
        listener.trigger_wake_manually()

    def hide_to_background(self):
        """Hides window completely into background; listener stays 100% active."""
        self.withdraw()
        self.is_visible = False
        print("[JARVIS] UI hidden to background. Continuous acoustic listening active.")

    def wake_on_desktop(self):
        """Surfaces HUD on desktop when wake word 'Hey Jarvis' is spoken."""
        self.after(0, self._bring_to_front)

    def _bring_to_front(self):
        try:
            self.deiconify()
            self.lift()
            self.attributes('-topmost', True)
            self.focus_force()
            self.is_visible = True
            # Keep topmost briefly so it pops above all other windows
            self.after(3000, lambda: self.attributes('-topmost', False))
        except Exception as e:
            print(f"[HUD] Bring to front error: {e}")

    def _add_terminal_log(self, sender: str, message: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.transcript_box.configure(state="normal")
        if sender.upper() == "USER":
            tag = f"[{timestamp}] YOU > {message}\n"
        else:
            tag = f"[{timestamp}] JARVIS > {message}\n"
        self.transcript_box.insert("end", tag)
        self.transcript_box.see("end")
        self.transcript_box.configure(state="disabled")

    # ---------------- Callbacks from Engine ----------------
    def on_state_change(self, state: str, detail: str = ""):
        self.current_state = state
        self.after(0, lambda: self._update_status_label(state, detail))

    def _update_status_label(self, state: str, detail: str):
        if hasattr(self, 'lbl_mic'):
            self.lbl_mic.configure(text=f"🎙️ Mic: {listener.active_mic_name[:32]}")

        if state == "STANDBY":
            self.lbl_status.configure(text='STANDBY // SAY "HEY JARVIS"', text_color=config.COLOR_ACCENT_GLOW)
            self.btn_mic.configure(fg_color="#006699")
        elif state == "LISTENING":
            self.lbl_status.configure(text="● ACTIVE LISTENING // SPEAK NOW", text_color=config.COLOR_ACCENT_GREEN)
            self.btn_mic.configure(fg_color="#00b4d8")
        elif state == "PROCESSING":
            self.lbl_status.configure(text="⚙ ANALYZING COMMAND...", text_color=config.COLOR_ACCENT_AMBER)
        elif state == "SPEAKING":
            self.lbl_status.configure(text="🔊 JARVIS TRANSMITTING...", text_color=config.COLOR_ACCENT_CYAN)

    def on_transcript_event(self, sender: str, text: str):
        self.after(0, lambda: self._add_terminal_log(sender, text))

    def on_wake_event(self):
        self.wake_on_desktop()

    def on_speaker_status(self, state: str, text: str):
        if state == "SPEAKING":
            self.on_state_change("SPEAKING", text)
        else:
            self.on_state_change("STANDBY", "")

    # ---------------- Arc Reactor Drawing & Animation ----------------
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
            glow_radius = 50 + int(self.pulse * 12)
        elif self.current_state == "PROCESSING":
            core_color = "#ffb703"
            ring_color = "#fb8500"
            glow_radius = 45 + int(self.pulse * 8)
        elif self.current_state == "SPEAKING":
            core_color = "#00e5ff"
            ring_color = "#7b2cbf"
            glow_radius = 52 + int(self.pulse * 10)
        else:  # STANDBY
            core_color = "#0077b6"
            ring_color = "#0096c7"
            glow_radius = 42 + int(self.pulse * 4)

        # Outer tech ring with rotating ticks
        outer_r = 75
        self.canvas.create_oval(cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r, outline="#1a2744", width=2)

        num_ticks = 12
        for i in range(num_ticks):
            deg = self.angle + (i * (360 / num_ticks))
            rad = math.radians(deg)
            x1 = cx + (outer_r - 8) * math.cos(rad)
            y1 = cy + (outer_r - 8) * math.sin(rad)
            x2 = cx + (outer_r) * math.cos(rad)
            y2 = cy + (outer_r) * math.sin(rad)
            self.canvas.create_line(x1, y1, x2, y2, fill=ring_color, width=2)

        # Middle energy ring
        mid_r = 56
        self.canvas.create_oval(cx - mid_r, cy - mid_r, cx + mid_r, cy + mid_r, outline=ring_color, width=2)

        # Inner pulsing core
        self.canvas.create_oval(cx - glow_radius, cy - glow_radius, cx + glow_radius, cy + glow_radius, fill="#0d1f3d", outline=ring_color, width=3)
        core_r = 24 + int(self.pulse * 4)
        self.canvas.create_oval(cx - core_r, cy - core_r, cx + core_r, cy + core_r, fill=core_color, outline="#ffffff", width=2)

        # Center pinpoint
        self.canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="#ffffff", outline="")

        self.after(50, self._animate_arc_reactor)


def start_hud(hidden: bool = False):
    app = JarvisHUD(start_hidden=hidden)
    app.mainloop()

if __name__ == "__main__":
    start_hud(hidden=False)
