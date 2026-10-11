# ⚡ J.A.R.V.I.S. // Voice-First Desktop AI Assistant (Version 2.0)

A production-grade, voice-first personal AI assistant and desktop command center for Windows. Integrates continuous conversational dialogue, in-app web search with card presentations, multi-turn reference resolution ("first result", "that website", "explain it"), robust Windows system automation, and a sci-fi Arc-Reactor command center interface.

---

## 🌟 What's New in Version 2.0

1. **Continuous Voice Dialogue & Multi-Turn Context**:
   - JARVIS remembers active conversations, search results, and references.
   - Example: *"Search for cybersecurity news"* ➔ *"Explain the first result"* ➔ *"Open that website"*.
   - Never terminates on commands like "stop", "cancel", or "exit this task".

2. **In-App Search & Intelligence Layer**:
   - Performs web searches inside JARVIS with interactive result cards (titles, snippets, direct links, and spoken summaries).
   - **Does NOT automatically redirect every search to Chrome**. Chrome is launched only when explicitly instructed.
   - Extracts and summarizes accessible web page articles inside the interface.

3. **Task Lifecycle & Cancellation Manager**:
   - States: `IDLE`, `LISTENING`, `THINKING`, `EXECUTING`, `SPEAKING`, `WAITING_FOR_CONFIRMATION`, `CANCELLED`.
   - Interrupt speech anytime: *"Stop speaking"* or click the emergency mute control.
   - Cancel active tasks: *"Cancel this task"*.

4. **Safety & Confirmation Layer**:
   - Explicit allowlist of permissible system actions.
   - Voice and UI confirmation for destructive actions (e.g. system shutdown, emptying recycle bin).

5. **Upgraded Desktop Command Center UI**:
   - Multi-tab command center:
     - 💬 **Conversation & Search**: Live transcript, Arc Reactor voice visualization, in-app search cards.
     - 🖥️ **System Center**: Live telemetry, battery, volume, brightness, CPU & RAM diagnostics.
     - ⚙ **Tasks & Notes**: Saved voice notes, task histories, and active operations.
     - 🔧 **Settings**: Audio input selector, voice settings, and memory controls.

---

## 🚀 Quick Start

### Run with Python
```powershell
cd "C:\Users\M Vijay kumar\.gemini\antigravity\scratch\jarvis-assistant"
python main.py
```

### Run in Background Silently
```powershell
.\start_background_service.bat
```

### Run Automated Test Suite
```powershell
python test_upgrade.py
```

---

## 🎙️ Spoken Voice Commands

| Category | Example Voice Commands |
| :--- | :--- |
| **Wake & Continuous** | *"Hey Jarvis"*, *"Yes, continue"*, *"Hello Jarvis"* |
| **In-App Search** | *"Search for latest AI developments"*, *"Search ethical hacking tools"* |
| **Contextual References** | *"Explain the first result"*, *"Open that website"*, *"Summarize this page"* |
| **Interruptions** | *"Stop speaking"*, *"Cancel this task"*, *"Clear conversation"* |
| **Hardware & Audio** | *"Make the sound quieter"*, *"Set volume to 50%"*, *"Mute audio"*, *"Dim screen"* |
| **Applications** | *"Launch VS Code"*, *"Open Chrome"*, *"Close Notepad"*, *"Show desktop"* |
| **Productivity** | *"Take a note review audit tomorrow"*, *"Read my notes"*, *"Take screenshot"* |
| **System Diagnostics** | *"Run system diagnostic"*, *"What's my battery status?"*, *"Lock workstation"* |
| **Security Confirmations** | *"Shutdown laptop"* ➔ *"Confirm"* / *"Cancel"* |
