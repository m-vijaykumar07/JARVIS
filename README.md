# ⚡ SUVI / J.A.R.V.I.S. Voice-First AI Desktop Assistant & Web Dashboard

A unified personal AI assistant for Windows PC featuring an authentic cloned voice that responds to **every command**, continuous voice dialogue, in-app web search, Windows system automation, an Arc-Reactor desktop command center HUD, and an integrated FastAPI backend with a React + Vite dashboard.

---

## 🎙️ Cloned Voice for Every Command
SUVI is equipped with the user's authentic cloned voice clips (`assets/voice_samples/`) and responds to **100% of commands**:
- **Wake Words & Prompts**: *"I'm listening. Please tell me what you need."* (`listening.wav`)
- **Launching Apps & Files**: *"Opening your files."* (`opening_files.wav`) for Chrome, Notepad, Calculator, Explorer, etc.
- **Web Search & Lookups**: *"Searching for the information."* (`searching_info.wav`) followed by spoken summary.
- **System Actions & Tasks**: *"Task has been completed."* (`task_completed.wav`) for volume, brightness, screenshots, notes, window actions, muting.
- **Directives & Data Queries**: *"I am on your command."* (`on_your_command.wav`) for status, battery, time, diagnostics.
- **Courtesy & Thanks**: *"Thank you, always open to your heart."* (`thank_you.wav`).
- **Startup Greeting**: *"Good morning. All systems are ready."* (`good_morning.wav`).
- **Help & Standby**: *"I am ready to help, if you need anything else."* (`ready_to_help.wav`).

*(Dynamic payloads like live clock time, battery percentage, or AI explanations are spoken smoothly in Suvi's neural Indian voice right after the authentic cloned voice acknowledgment!)*

---

## 🌟 Architecture & Scaffold Connection

The **SUVI Upgrade Scaffold** is directly connected to the unified engine:
- **FastAPI Backend (`backend/app/main.py`)**: Exposes REST endpoints (`/chat`, `/health`, `/actions`, `/actions/run`) wired directly to `commander.process_structured()` and `speaker.speak()`.
- **Local Ollama LLM (`engine/ai_brain.py`)**: Integrated local LLM support via Ollama (`qwen2.5-coder:7b` at `http://127.0.0.1:11434/api/chat`).
- **React + Vite Dashboard (`frontend/`)**: Futuristic web chat dashboard with live status and orb animation, communicating directly with the FastAPI server.
- **Desktop HUD (`main.py`)**: Multi-tab CustomTkinter command center with Arc-Reactor visualization and system telemetry.

---

## 🚀 How to Run

### 1. Run the Desktop Voice Assistant (Voice + Arc-Reactor HUD)
```powershell
python main.py
```
Or double-click `run_jarvis.bat`.

### 2. Run the FastAPI Server (Port 8000)
```powershell
python run_api.py
```
- Health Check: `http://127.0.0.1:8000/health`
- Interactive API Docs: `http://127.0.0.1:8000/docs`

### 3. Run the React + Vite Web Dashboard
```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser. Any message typed into the dashboard is executed and spoken aloud by SUVI using the cloned voice!

### 4. Run Automated Test Suites
```powershell
python test_upgrade.py
python test_system.py
```

---

## 🗣️ Voice Commands Quick Reference

| Category | Example Spoken Command | Cloned Voice Response |
| :--- | :--- | :--- |
| **Wake** | *"Hey Jarvis"*, *"Hey Suvi"*, *"Suvi"* | *"I'm listening. Please tell me what you need."* |
| **Apps** | *"Open Notepad"*, *"Launch Chrome"*, *"Open Calculator"* | *"Opening your files."* |
| **Search** | *"Search for cybersecurity news"*, *"Search Python tutorials"* | *"Searching for the information."* + summary |
| **Context** | *"Explain the first result"*, *"Open that website"* | *"Searching for the information."* / *"Opening your files."* |
| **Volume** | *"Volume up"*, *"Set volume to 50"*, *"Mute audio"* | *"Task has been completed."* |
| **Brightness** | *"Brightness up"*, *"Dim screen"* | *"Task has been completed."* |
| **Screenshots** | *"Take screenshot"*, *"Capture screen"* | *"Task has been completed."* |
| **Notes** | *"Take a note buy groceries"*, *"Read notes"* | *"Task has been completed."* |
| **Time & Battery**| *"What time is it?"*, *"Check battery"* | *"I am on your command."* + details |
| **Gratitude** | *"Thank you"*, *"Thanks"* | *"Thank you, always open to your heart."* |
| **Voice Toggle** | *"Switch to Jarvis voice"*, *"Switch to Suvi voice"* | Toggles between cloned voice and neural TTS |
