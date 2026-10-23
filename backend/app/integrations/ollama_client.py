import os
import requests
from dotenv import load_dotenv

load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

def ask_model(message: str) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are SUVI (Smart Unified Voice Intelligence), a helpful "
                    "assistant. Be clear and concise. Never claim an action succeeded "
                    "unless a trusted action handler confirms it. Do not request or "
                    "reveal passwords, API keys, or other secrets."
                ),
            },
            {"role": "user", "content": message},
        ],
        "stream": False,
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
    except requests.RequestException:
        return (
            "My local AI service is unavailable. Start Ollama and check the "
            "model name, or try a built-in command."
        )
