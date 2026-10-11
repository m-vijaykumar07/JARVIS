"""
JARVIS Task State & Lifecycle Manager
Manages system states, background task cancellation tokens, and task histories.
"""
import enum
import time
import threading
import uuid
from typing import Callable, Optional, Dict, Any

class TaskState(enum.Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    EXECUTING = "EXECUTING"
    SPEAKING = "SPEAKING"
    WAITING_FOR_CONFIRMATION = "WAITING_FOR_CONFIRMATION"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"
    SHUTTING_DOWN = "SHUTTING_DOWN"

class CancellationToken:
    def __init__(self):
        self._is_cancelled = threading.Event()

    def cancel(self):
        self._is_cancelled.set()

    @property
    def is_cancelled(self) -> bool:
        return self._is_cancelled.is_set()

    def check(self):
        if self._is_cancelled.is_set():
            raise InterruptedError("Operation was cancelled by user.")

class TaskItem:
    def __init__(self, task_id: str, description: str, cancellable: bool = True):
        self.task_id = task_id
        self.description = description
        self.cancellable = cancellable
        self.token = CancellationToken()
        self.start_time = time.time()
        self.end_time = None
        self.status = "RUNNING"
        self.error = None

    def finish(self, status: str = "COMPLETED", error: str = None):
        self.end_time = time.time()
        self.status = status
        self.error = error

class TaskManager:
    def __init__(self, state_change_callback: Optional[Callable[[TaskState, str], None]] = None):
        self._state = TaskState.IDLE
        self._detail = "System Ready"
        self._callback = state_change_callback
        self._lock = threading.Lock()
        
        self.active_tasks: Dict[str, TaskItem] = {}
        self.task_history = []
        self._pending_confirmation: Optional[Dict[str, Any]] = None

    def set_callback(self, callback: Callable[[TaskState, str], None]):
        self._callback = callback

    @property
    def current_state(self) -> TaskState:
        with self._lock:
            return self._state

    @property
    def current_detail(self) -> str:
        with self._lock:
            return self._detail

    def set_state(self, state: TaskState, detail: str = ""):
        with self._lock:
            self._state = state
            self._detail = detail
        if self._callback:
            try:
                self._callback(state, detail)
            except Exception:
                pass

    def create_task(self, description: str, cancellable: bool = True) -> TaskItem:
        task_id = str(uuid.uuid4())[:8]
        item = TaskItem(task_id, description, cancellable)
        with self._lock:
            self.active_tasks[task_id] = item
        return item

    def complete_task(self, task_id: str, status: str = "COMPLETED", error: str = None):
        with self._lock:
            if task_id in self.active_tasks:
                item = self.active_tasks.pop(task_id)
                item.finish(status, error)
                self.task_history.append(item)
                if len(self.task_history) > 50:
                    self.task_history.pop(0)

    def cancel_active_tasks(self) -> int:
        """Cancels all cancellable active operations."""
        count = 0
        with self._lock:
            for task_id, item in list(self.active_tasks.items()):
                if item.cancellable:
                    item.token.cancel()
                    item.finish("CANCELLED")
                    self.task_history.append(item)
                    del self.active_tasks[task_id]
                    count += 1
        if count > 0:
            self.set_state(TaskState.CANCELLED, f"Cancelled {count} active task(s).")
        return count

    def set_pending_confirmation(self, action_name: str, callback: Callable[[], str], prompt: str):
        with self._lock:
            self._pending_confirmation = {
                "action": action_name,
                "callback": callback,
                "prompt": prompt,
                "created_at": time.time()
            }
        self.set_state(TaskState.WAITING_FOR_CONFIRMATION, prompt)

    def resolve_confirmation(self, confirmed: bool) -> Optional[str]:
        with self._lock:
            pending = self._pending_confirmation
            self._pending_confirmation = None

        if not pending:
            return None

        if confirmed:
            try:
                return pending["callback"]()
            except Exception as e:
                return f"Operation failed: {e}"
        else:
            return f"Action '{pending['action']}' cancelled."

    def has_pending_confirmation(self) -> bool:
        with self._lock:
            return self._pending_confirmation is not None

# Global singleton
task_manager = TaskManager()
