"""
JARVIS System Actions Engine
Deep hardware, operating system, and application controls for Windows laptops.
"""
import os
import sys
import subprocess
import time
import datetime
import shutil
import ctypes
from pathlib import Path
import psutil
import pyautogui
import pyperclip
import config

try:
    import screen_brightness_control as sbc
except ImportError:
    sbc = None

try:
    from pycaw.pycaw import AudioUtilities
except ImportError:
    AudioUtilities = None


class SystemActions:
    def __init__(self):
        # Configure PyAutoGUI safety settings
        pyautogui.FAILSAFE = False

    # -------------------------------------------------------------
    # VOLUME CONTROLS (PyCaw)
    # -------------------------------------------------------------
    def _get_volume_endpoint(self):
        if not AudioUtilities:
            return None
        try:
            speakers = AudioUtilities.GetSpeakers()
            return speakers.EndpointVolume
        except Exception as e:
            print(f"[SystemActions] Volume endpoint error: {e}")
            return None

    def get_volume(self) -> int:
        """Returns master volume percentage (0 - 100)."""
        ep = self._get_volume_endpoint()
        if ep:
            try:
                return round(ep.GetMasterVolumeLevelScalar() * 100)
            except Exception:
                pass
        return 50

    def set_volume(self, level: int) -> str:
        """Sets master volume percentage (0 - 100)."""
        level = max(0, min(100, int(level)))
        ep = self._get_volume_endpoint()
        if ep:
            try:
                ep.SetMute(0, None)
                ep.SetMasterVolumeLevelScalar(level / 100.0, None)
                return f"Volume set to {level} percent, sir."
            except Exception as e:
                return f"Unable to adjust volume: {e}"
        return "Audio endpoint not accessible."

    def change_volume(self, delta: int) -> str:
        """Increases or decreases volume by delta."""
        current = self.get_volume()
        new_level = max(0, min(100, current + delta))
        return self.set_volume(new_level)

    def mute_volume(self) -> str:
        """Mutes audio output."""
        ep = self._get_volume_endpoint()
        if ep:
            try:
                ep.SetMute(1, None)
                return "Audio muted, sir."
            except Exception as e:
                return f"Mute failed: {e}"
        return "Audio endpoint not accessible."

    def unmute_volume(self) -> str:
        """Unmutes audio output."""
        ep = self._get_volume_endpoint()
        if ep:
            try:
                ep.SetMute(0, None)
                return "Audio unmuted, sir."
            except Exception as e:
                return f"Unmute failed: {e}"
        return "Audio endpoint not accessible."

    # -------------------------------------------------------------
    # SCREEN BRIGHTNESS CONTROLS
    # -------------------------------------------------------------
    def get_brightness(self) -> int:
        """Returns display brightness percentage."""
        if sbc:
            try:
                b = sbc.get_brightness()
                if isinstance(b, list) and len(b) > 0:
                    return int(b[0])
                elif isinstance(b, (int, float)):
                    return int(b)
            except Exception:
                pass
        return 50

    def set_brightness(self, level: int) -> str:
        """Sets display brightness (0 - 100)."""
        level = max(0, min(100, int(level)))
        if sbc:
            try:
                sbc.set_brightness(level)
                return f"Display brightness set to {level} percent, sir."
            except Exception as e:
                return f"Brightness adjustment failed: {e}"
        return "Brightness controller not available."

    def change_brightness(self, delta: int) -> str:
        """Increases or decreases display brightness by delta."""
        current = self.get_brightness()
        new_level = max(0, min(100, current + delta))
        return self.set_brightness(new_level)

    # -------------------------------------------------------------
    # POWER, BATTERY & SYSTEM DIAGNOSTICS
    # -------------------------------------------------------------
    def get_battery_status(self) -> str:
        """Checks battery percentage and charging state."""
        battery = psutil.sensors_battery()
        if not battery:
            return "This system appears to be running on direct AC power with no battery detected."

        percent = battery.percent
        is_plugged = battery.power_plugged
        charging_str = "charging" if is_plugged else "running on battery"

        if battery.secsleft and battery.secsleft > 0 and not is_plugged:
            hours = battery.secsleft // 3600
            mins = (battery.secsleft % 3600) // 60
            time_str = f"with approximately {hours} hours and {mins} minutes remaining"
        else:
            time_str = ""

        return f"Battery is at {percent} percent, currently {charging_str} {time_str}."

    def get_system_report(self) -> str:
        """Diagnostic overview of CPU, RAM, and Disk."""
        cpu = psutil.cpu_percent(interval=0.4)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('C:\\')
        battery = psutil.sensors_battery()

        batt_str = f"{battery.percent}%" if battery else "AC"

        return (
            f"System Diagnostic: CPU load is at {cpu}%. "
            f"RAM usage is at {ram.percent}% of {round(ram.total / (1024**3), 1)} gigabytes. "
            f"Drive C has {round(disk.free / (1024**3), 1)} gigabytes free. "
            f"Power level is {batt_str}."
        )

    def lock_workstation(self) -> str:
        """Locks the Windows user session."""
        try:
            ctypes.windll.user32.LockWorkStation()
            return "Locking workstation now, sir."
        except Exception as e:
            return f"Failed to lock workstation: {e}"

    def sleep_laptop(self) -> str:
        """Puts Windows PC to sleep."""
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Suspending system into sleep mode."
        except Exception as e:
            return f"Sleep command failed: {e}"

    def shutdown_laptop(self) -> str:
        """Initiates safe system shutdown."""
        try:
            os.system("shutdown /s /t 10")
            return "Shutting down the laptop in 10 seconds. Goodnight, sir."
        except Exception as e:
            return f"Shutdown failed: {e}"

    def restart_laptop(self) -> str:
        """Initiates system restart."""
        try:
            os.system("shutdown /r /t 10")
            return "Rebooting the laptop in 10 seconds, sir."
        except Exception as e:
            return f"Restart failed: {e}"

    def cancel_shutdown(self) -> str:
        """Aborts scheduled shutdown or restart."""
        try:
            os.system("shutdown /a")
            return "Shutdown sequence aborted, sir."
        except Exception as e:
            return f"Could not cancel shutdown: {e}"

    # -------------------------------------------------------------
    # APPLICATION MANAGEMENT
    # -------------------------------------------------------------
    def launch_app(self, app_name: str) -> str:
        """Launches an application by common name or custom command."""
        app_name_clean = app_name.lower().strip()

        # Check known mappings
        for key, cmd in config.APP_COMMANDS.items():
            if key in app_name_clean:
                try:
                    subprocess.Popen(cmd, shell=True)
                    return f"Opening {key.title()}, sir."
                except Exception as e:
                    return f"Error launching {key}: {e}"

        # Fallback to direct shell execution
        try:
            subprocess.Popen(f"start {app_name_clean}", shell=True)
            return f"Attempting to launch {app_name}, sir."
        except Exception as e:
            return f"Could not launch {app_name}: {e}"

    def close_app(self, app_name: str) -> str:
        """Closes or terminates application process."""
        app_name_clean = app_name.lower().strip()
        exe_map = {
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "notepad": "notepad.exe",
            "calc": "CalculatorApp.exe",
            "calculator": "CalculatorApp.exe",
            "code": "Code.exe",
            "vs code": "Code.exe",
            "spotify": "Spotify.exe",
            "word": "WINWORD.EXE",
            "excel": "EXCEL.EXE",
            "powerpoint": "POWERPNT.EXE",
            "terminal": "WindowsTerminal.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe"
        }

        exe_target = exe_map.get(app_name_clean, f"{app_name_clean}.exe")
        try:
            res = subprocess.run(f"taskkill /f /im {exe_target}", shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                return f"Closed {app_name}, sir."
            else:
                # Try generic taskkill without extension
                subprocess.run(f"taskkill /f /im {app_name_clean}*", shell=True, capture_output=True)
                return f"Sent termination signal to {app_name}."
        except Exception as e:
            return f"Failed to close {app_name}: {e}"

    # -------------------------------------------------------------
    # WINDOW CONTROLS & DESKTOP NAVIGATION
    # -------------------------------------------------------------
    def show_desktop(self) -> str:
        """Minimizes all windows to show desktop."""
        pyautogui.hotkey('win', 'd')
        return "Displaying desktop, sir."

    def switch_window(self) -> str:
        """Switches to previous active window (Alt+Tab)."""
        pyautogui.hotkey('alt', 'tab')
        return "Switched window."

    def maximize_window(self) -> str:
        """Maximizes current window (Win+Up)."""
        pyautogui.hotkey('win', 'up')
        return "Window maximized."

    def minimize_window(self) -> str:
        """Minimizes current window (Win+Down)."""
        pyautogui.hotkey('win', 'down')
        return "Window minimized."

    def scroll_down(self) -> str:
        pyautogui.scroll(-500)
        return "Scrolling down."

    def scroll_up(self) -> str:
        pyautogui.scroll(500)
        return "Scrolling up."

    # -------------------------------------------------------------
    # PRODUCTIVITY & SHORTCUTS
    # -------------------------------------------------------------
    def take_screenshot(self) -> str:
        """Captures full screen and saves to screenshots folder with multi-tier fallback."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = config.SCREENSHOTS_DIR / f"JARVIS_Capture_{timestamp}.png"
            captured = False

            # Method 1: PyAutoGUI screenshot
            try:
                import pyautogui
                img = pyautogui.screenshot()
                if img:
                    img.save(str(filename))
                    captured = True
            except Exception:
                pass

            # Method 2: Direct PIL ImageGrab
            if not captured:
                try:
                    from PIL import ImageGrab
                    img = ImageGrab.grab(all_screens=True)
                    if img:
                        img.save(str(filename))
                        captured = True
                except Exception:
                    pass

            # Method 3: Windows Native Win + PrtScn OS-level trigger
            if not captured:
                try:
                    import ctypes
                    user32 = ctypes.windll.user32
                    VK_LWIN = 0x5B
                    VK_SNAPSHOT = 0x2C
                    user32.keybd_event(VK_LWIN, 0, 0, 0)
                    user32.keybd_event(VK_SNAPSHOT, 0, 0, 0)
                    time.sleep(0.05)
                    user32.keybd_event(VK_SNAPSHOT, 0, 2, 0)
                    user32.keybd_event(VK_LWIN, 0, 2, 0)
                    return "Screenshot captured via Windows system shortcut and saved to your Pictures folder, sir."
                except Exception:
                    pass

            if captured and filename.exists():
                try:
                    os.startfile(str(filename))
                except Exception:
                    pass
                return "Screenshot captured and saved to your Pictures folder, sir."
            else:
                return "Unable to capture screen display at this moment, sir."
        except Exception as e:
            return f"Screenshot capture failed: {e}"

    def empty_recycle_bin(self) -> str:
        """Empties Windows Recycle Bin."""
        try:
            # PowerShell Clear-RecycleBin
            subprocess.run(["powershell", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"], check=False)
            return "Recycle Bin has been emptied, sir."
        except Exception as e:
            return f"Failed to clear recycle bin: {e}"

    def read_clipboard(self) -> str:
        """Reads and speaks clipboard content."""
        try:
            text = pyperclip.paste()
            if text and text.strip():
                sample = text.strip()[:150]
                return f"Clipboard contains: {sample}"
            return "Your clipboard is currently empty, sir."
        except Exception as e:
            return f"Clipboard access failed: {e}"

    def type_text(self, text_to_type: str) -> str:
        """Types requested text into active cursor position."""
        try:
            time.sleep(0.3)
            pyautogui.write(text_to_type, interval=0.02)
            return "Text entered, sir."
        except Exception as e:
            return f"Typing failed: {e}"

    def press_key(self, key_name: str) -> str:
        """Presses keyboard key like enter, esc, space, backspace."""
        try:
            key_clean = key_name.lower().strip()
            pyautogui.press(key_clean)
            return f"Pressed {key_name}."
        except Exception as e:
            return f"Key press failed: {e}"


# Global singleton instance
system_actions = SystemActions()
