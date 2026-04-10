"""Agent memory management."""
from typing import Any, Dict, List, Optional
from collections import deque
import time
from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ConversationMemory:
    """In-memory conversation history management."""

    def __init__(self, session_id: str, max_items: Optional[int] = None):
        self.session_id = session_id
        self.max_items = max_items or settings.MAX_MEMORY_ITEMS
        self._history: deque = deque(maxlen=self.max_items)

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to conversation history."""
        entry = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {},
        }
        self._history.append(entry)
        logger.debug("Added message to memory", session_id=self.session_id, role=role)

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history."""
        history = list(self._history)
        if limit:
            history = history[-limit:]
        return history

    def get_formatted_history(self, limit: int = 10) -> str:
        """Get formatted conversation history for LLM context."""
        history = self.get_history(limit)
        formatted = []
        for entry in history:
            formatted.append(f"{entry['role'].upper()}: {entry['content']}")
        return "\n".join(formatted)

    def clear(self) -> None:
        """Clear conversation history."""
        self._history.clear()
        logger.info("Memory cleared", session_id=self.session_id)

    def __len__(self) -> int:
        return len(self._history)


class MemoryManager:
    """Manages memory across multiple sessions."""

    _instance: Optional["MemoryManager"] = None
    _sessions: Dict[str, ConversationMemory] = {}

    def __new__(cls) -> "MemoryManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_session_memory(self, session_id: str) -> ConversationMemory:
        """Get or create memory for a session."""
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationMemory(session_id)
            logger.info("Created new memory session", session_id=session_id)
        return self._sessions[session_id]

    def delete_session(self, session_id: str) -> None:
        """Delete a session's memory."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info("Deleted memory session", session_id=session_id)

    def list_sessions(self) -> List[str]:
        """List all active sessions."""
        return list(self._sessions.keys())

    def cleanup_old_sessions(self, max_age_seconds: int = 3600) -> int:
        """Remove sessions older than max_age_seconds."""
        current_time = time.time()
        to_delete = []
        for session_id, memory in self._sessions.items():
            history = memory.get_history(limit=1)
            if history:
                last_activity = history[-1].get("timestamp", 0)
                if current_time - last_activity > max_age_seconds:
                    to_delete.append(session_id)
            elif len(memory) == 0:
                to_delete.append(session_id)

        for session_id in to_delete:
            self.delete_session(session_id)

        return len(to_delete)
