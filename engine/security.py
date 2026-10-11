"""
JARVIS Security & Tool Authorization Layer
Validates arguments, maintains an explicit allowlist of authorized operations,
and enforces risk-based confirmations for destructive or sensitive actions.
"""
from typing import Callable, Dict, Any, List, Optional
import os

class SecurityPolicy:
    # Explicit allowlist of permissible system actions
    ALLOWED_ACTIONS = {
        # Audio
        "set_volume", "change_volume", "mute_volume", "unmute_volume", "get_volume",
        # Display
        "set_brightness", "change_brightness", "get_brightness",
        # Apps & Windows
        "launch_app", "close_app", "show_desktop", "switch_window", "maximize_window", "minimize_window",
        "scroll_down", "scroll_up",
        # Productivity & System
        "take_screenshot", "read_clipboard", "type_text", "press_key", "empty_recycle_bin",
        "get_battery_status", "get_system_report", "lock_workstation",
        # Power (Requires confirmation)
        "sleep_laptop", "shutdown_laptop", "restart_laptop", "cancel_shutdown",
        # Web & Media
        "search_in_app", "extract_page", "open_url_in_browser", "media_control",
        # Notes & Context
        "save_note", "get_notes", "clear_conversation"
    }

    # High-risk actions that require voice or UI confirmation
    CONFIRMATION_REQUIRED_ACTIONS = {
        "shutdown_laptop",
        "restart_laptop",
        "empty_recycle_bin"
    }

    @staticmethod
    def is_action_allowed(action_name: str) -> bool:
        return action_name in SecurityPolicy.ALLOWED_ACTIONS

    @staticmethod
    def requires_confirmation(action_name: str) -> bool:
        return action_name in SecurityPolicy.CONFIRMATION_REQUIRED_ACTIONS

    @staticmethod
    def sanitize_input(text: str) -> str:
        # Strip potential dangerous control characters
        return "".join(ch for ch in text if ch.isprintable()).strip()

    @staticmethod
    def validate_app_name(app_name: str) -> bool:
        clean = app_name.lower().strip()
        # Disallow malicious injection tokens
        forbidden = [";", "&&", "||", "`", "$", "|", ">", "<", "\n"]
        return not any(token in clean for token in forbidden)
