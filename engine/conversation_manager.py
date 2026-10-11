"""
JARVIS Conversation & Context Memory Manager
Handles short-term dialogue history, entity resolution (e.g., 'it', 'first result', 'that website'),
search reference resolution, and configurable memory persistence.
"""
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

class ConversationManager:
    def __init__(self, persistence_file: Optional[Path] = None):
        self.history: List[Dict[str, Any]] = []
        self.last_search_results: List[Dict[str, Any]] = []
        self.last_selected_result: Optional[Dict[str, Any]] = None
        self.last_entity: Optional[str] = None
        self.last_action: Optional[str] = None
        self.notes: List[Dict[str, str]] = []
        self.reminders: List[Dict[str, Any]] = []
        self.persistence_file = persistence_file

        self._load_state()

    def _load_state(self):
        if self.persistence_file and self.persistence_file.exists():
            try:
                with open(self.persistence_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.notes = data.get("notes", [])
                    self.reminders = data.get("reminders", [])
            except Exception:
                pass

    def save_state(self):
        if self.persistence_file:
            try:
                with open(self.persistence_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "notes": self.notes,
                        "reminders": self.reminders
                    }, f, indent=2)
            except Exception:
                pass

    def add_turn(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        turn = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self.history.append(turn)
        if len(self.history) > 40:
            self.history.pop(0)

    def set_search_results(self, results: List[Dict[str, Any]]):
        self.last_search_results = results
        if results:
            self.last_selected_result = results[0]

    def resolve_reference(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Resolves linguistic references like 'first result', 'second one',
        'that website', 'it', 'the third link'.
        """
        lower = text.lower()
        if not self.last_search_results:
            return None

        ordinals = {
            "first": 0, "1st": 0, "one": 0,
            "second": 1, "2nd": 1, "two": 1,
            "third": 2, "3rd": 2, "three": 2,
            "fourth": 3, "4th": 3, "four": 3,
            "fifth": 4, "5th": 4, "five": 4
        }

        for word, idx in ordinals.items():
            if f"the {word}" in lower or f"{word} result" in lower or f"{word} one" in lower:
                if idx < len(self.last_search_results):
                    self.last_selected_result = self.last_search_results[idx]
                    return self.last_selected_result

        if any(term in lower for term in ["that result", "that website", "that page", "this link", "it"]):
            return self.last_selected_result or self.last_search_results[0]

        return None

    def add_note(self, content: str) -> str:
        note = {
            "id": len(self.notes) + 1,
            "content": content,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.notes.append(note)
        self.save_state()
        return f"Note #{note['id']} saved, sir."

    def get_notes(self) -> List[Dict[str, str]]:
        return self.notes

    def clear_history(self):
        self.history.clear()
        self.last_search_results.clear()
        self.last_selected_result = None
        self.last_entity = None
        self.last_action = None

# Global conversation manager
import config
conv_manager = ConversationManager(persistence_file=config.BASE_DIR / "conversation_memory.json")
