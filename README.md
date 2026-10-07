# ⚡ J.A.R.V.I.S. Voice Assistant (MK-85)

An autonomous, full-featured AI voice assistant built for Windows laptops. Runs continuously in the background, wakes up on desktop whenever you say **"Hey Jarvis"**, speaks with a realistic British neural AI voice, and gives you total voice control over your laptop's hardware, applications, windows, media, and web browsing.

---

## 🌟 Key Architecture & Always-On Background Mode

1. **Always-On Background Listener (`jarvis_background_service.pyw`)**:
   - Runs silently in the background with `pythonw.exe` (no black terminal window, zero screen clutter).
   - Automatically registered to **Windows Startup** (`shell:startup`) — starts every time your laptop powers on!
   - You **do not need to open any app manually**. Just say **"Hey Jarvis"** anytime!

2. **Instant Zero-Latency Wake Word (Vosk Local Neural Stream)**:
   - Processes microphone audio in real time with an offline speech model (`vosk-model-small-en-us-0.15`).
   - Wakes up the exact millisecond you finish saying **"Hey Jarvis"** (or *"Jarvis"*, *"Wake up Jarvis"*, etc.).

3. **Automatic Desktop Wake Surfacing**:
   - Whenever you say **"Hey Jarvis"**, the Holographic Arc-Reactor HUD pops up directly in front of you on your Windows desktop.
   - Plays an ascending Arc-Reactor chime and says: *"At your service, Sir."*
   - Listens to your voice command, executes it on your laptop, and gives spoken confirmation.
   - When you click `✕` or `—`, it simply hides back into the background while remaining 100% active.

4. **Realistic British Neural Voice (Edge-TTS)**:
   - British AI tone: `en-GB-RyanNeural` (exact natural intonation of Paul Bettany's JARVIS).
   - Offline fallback to Windows SAPI5 (`Microsoft David`) if disconnected from the web.

---

## 🚀 Controls & Scripts

| Script | Purpose |
| :--- | :--- |
| **`start_background_service.bat`** | Starts JARVIS silently in the background right now. |
| **`stop_jarvis.bat`** | Completely shuts down JARVIS background processes. |
| **`run_jarvis.bat`** | Launches JARVIS with a visible console window (useful for debugging). |
| **`JARVIS` (Desktop Shortcut)** | One-click desktop launcher icon. |
| **Windows Startup Shortcut** | Automatically boots JARVIS every time Windows starts. |

---

## 🎙️ Spoken Voice Commands Cheatsheet

### 🔹 Wake & Combined Commands
- *"Hey Jarvis"* *(plays wake chime, pops up HUD on desktop, and awaits command)*
- *"Hey Jarvis, what time is it?"*
- *"Jarvis, open Chrome"*
- *"Wake up Jarvis"*

### 🔹 Volume & Screen Brightness
- *"Set volume to 50 percent"* / *"Volume up"* / *"Volume down"* / *"Mute audio"* / *"Unmute"*
- *"Set brightness to 80 percent"* / *"Brightness up"* / *"Dim screen"* / *"Max brightness"*

### 🔹 Battery, Diagnostics & Power
- *"What's my battery status?"* / *"How much battery is left?"*
- *"System report"* / *"Run diagnostic"* *(reports live CPU %, RAM %, and Free Disk GB)*
- *"Lock laptop"* / *"Lock workstation"*
- *"Put laptop to sleep"* / *"Sleep laptop"*
- *"Shutdown laptop"* (10s timer; say *"Cancel shutdown"* to abort)

### 🔹 Application Launching & Closing
- *"Open Chrome"* / *"Open Google Chrome"*
- *"Launch Spotify"*
- *"Open VS Code"* / *"Open Notepad"* / *"Open Calculator"* / *"Open File Explorer"* / *"Open Terminal"*
- *"Close Chrome"* / *"Kill Notepad"* / *"Close Spotify"*

### 🔹 Desktop & Window Navigation
- *"Show desktop"* *(Minimizes all active windows)*
- *"Switch window"* *(Alt + Tab)*
- *"Maximize window"* / *"Minimize window"*
- *"Scroll down"* / *"Scroll up"*

### 🔹 Productivity & Screen Capture
- *"Take screenshot"* *(Saves to `Pictures\JARVIS_Screenshots` and previews it)*
- *"Empty recycle bin"*
- *"Read clipboard"* *(Reads aloud what you copied)*
- *"Type [words]"* *(Types text directly into active window)*
- *"Press enter"* / *"Press space"* / *"Press escape"*

### 🔹 Web, Media & Knowledge
- *"Play [song name] on YouTube"*
- *"Search YouTube for [query]"*
- *"Search Google for [query]"*
- *"Open GitHub"* / *"Open Gmail"* / *"Open Reddit"* / *"Open ChatGPT"*
- *"Who is Elon Musk?"* (Summarizes via Wikipedia)
- *"What is Quantum Computing?"*
- *"What's the weather in Bangalore?"* / *"Weather"*
- *"What time is it?"* / *"What is today's date?"*
- *"Pause music"* / *"Resume music"* / *"Next song"* / *"Previous song"*

### 🔹 Assistant Identity & Standby
- *"Who are you?"*
- *"Status check"*
- *"Go to sleep"* / *"Stand down"* (Returns to background standby)

---

## ⚙️ Configuration (`config.py`)

Open [config.py](file:///C:/Users/M%20Vijay%20kumar/.gemini/antigravity/scratch/jarvis-assistant/config.py) to customize:
- `USER_NAME = "Sir"`: Set your custom name (e.g. `"Vijay"`).
- `APP_COMMANDS`: Add custom applications or games.
- `WAKE_WORDS`: Add custom wake triggers.
