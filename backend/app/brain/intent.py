def detect_intent(message: str) -> str:
    text = message.casefold().strip()
    if text in {"hi", "hello", "hey", "hey suvi", "hello suvi"}:
        return "greeting"
    if any(x in text for x in ("what time", "current time", "tell me the time")):
        return "time"
    if "open calculator" in text or "launch calculator" in text:
        return "open_calculator"
    if "open notepad" in text or "launch notepad" in text:
        return "open_notepad"
    if any(x in text for x in ("open file explorer", "open explorer", "open downloads")):
        return "open_explorer"
    return "chat"
