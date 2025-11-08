from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, TypedDict

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PREFERENCES_PATH = DATA_DIR / "preferences.json"


class StoredMessage(TypedDict):
    type: str
    content: str


class PersistentMemory:
    """Wraps chat history and traveller preferences with JSON persistence."""

    def __init__(self, path: Path = PREFERENCES_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

        stored = self._load_from_disk()
        self.preferences: Dict[str, str] = stored.get("preferences", {})
        self.chat_history = self._history_from_messages(stored.get("history", []))

    def save(self) -> None:
        payload = {
            "preferences": self.preferences,
            "history": self._messages_from_history(self.chat_history),
        }
        with self.path.open("w", encoding="utf-8") as fp:
            json.dump(payload, fp, indent=2)

    def reset(self) -> None:
        self.preferences = {}
        self.chat_history = ChatMessageHistory()
        self.save()

    def _load_from_disk(self) -> Dict[str, object]:
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as fp:
                return json.load(fp)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _history_from_messages(messages: List[StoredMessage]) -> ChatMessageHistory:
        history = ChatMessageHistory()
        for message in messages:
            msg_type = message.get("type")
            content = message.get("content", "")
            if msg_type == "human":
                history.add_user_message(content)
            elif msg_type == "ai":
                history.add_ai_message(content)
        return history

    @staticmethod
    def _messages_from_history(history: ChatMessageHistory) -> List[StoredMessage]:
        serialised: List[StoredMessage] = []
        for message in history.messages:
            if isinstance(message, HumanMessage):
                serialised.append({"type": "human", "content": message.content})
            elif isinstance(message, AIMessage):
                serialised.append({"type": "ai", "content": message.content})
        return serialised

