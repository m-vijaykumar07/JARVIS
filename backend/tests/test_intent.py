from app.brain.intent import detect_intent

def test_greeting():
    assert detect_intent("hello SUVI") == "greeting"

def test_calculator():
    assert detect_intent("open calculator") == "open_calculator"

def test_fallback():
    assert detect_intent("explain zero trust") == "chat"
