import json
import os
import uuid
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .schemas import Message, Conversation, UserIndex


class ContextManager:
    """
    Gestión de contexto y almacenamiento en disco:
    - Índice por usuario: data/v2/users/{user_id}/index.json
    - Conversaciones: data/v2/users/{user_id}/conversations/{conversation_id}.json
    """

    def __init__(self, data_root: Path):
        self.data_root = Path(data_root)
        self.users_root = self.data_root / "users"
        self.users_root.mkdir(parents=True, exist_ok=True)

    # ---------- Helpers de ruta ----------
    def _user_dir(self, user_id: str) -> Path:
        d = self.users_root / user_id
        d.mkdir(parents=True, exist_ok=True)
        (d / "conversations").mkdir(parents=True, exist_ok=True)
        return d

    def _user_index_path(self, user_id: str) -> Path:
        return self._user_dir(user_id) / "index.json"

    def _conv_path(self, user_id: str, conversation_id: str) -> Path:
        return self._user_dir(user_id) / "conversations" / f"{conversation_id}.json"

    # ---------- IO seguro ----------
    def _safe_write(self, path: Path, data: dict):
        tmp = Path(str(path) + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)

    def _read_json(self, path: Path) -> Optional[dict]:
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    # ---------- Índice de usuario ----------
    def _load_user_index(self, user_id: str) -> UserIndex:
        p = self._user_index_path(user_id)
        data = self._read_json(p)
        if data is None:
            idx = UserIndex(user_id=user_id)
            self._safe_write(p, idx.model_dump())
            return idx
        return UserIndex(**data)

    def _save_user_index(self, user_id: str, idx: UserIndex):
        idx.last_updated = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        self._safe_write(self._user_index_path(user_id), idx.model_dump())

    # ---------- Conversaciones ----------
    def new_conversation(self, user_id: str) -> str:
        conversation_id = uuid.uuid4().hex
        timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"

        conv = Conversation(
            conversation_id=conversation_id,
            history=[],
            created_at=timestamp,
            updated_at=timestamp,
        )

        self._safe_write(self._conv_path(user_id, conversation_id), conv.model_dump())

        idx = self._load_user_index(user_id)
        if conversation_id not in idx.conversations:
            idx.conversations.append(conversation_id)
            self._save_user_index(user_id, idx)

        return conversation_id

    def conversation_exists(self, user_id: str, conversation_id: str) -> bool:
        return self._conv_path(user_id, conversation_id).exists()

    def load_conversation(self, user_id: str, conversation_id: str) -> Conversation:
        data = self._read_json(self._conv_path(user_id, conversation_id))
        if data is None:
            timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
            return Conversation(
                conversation_id=conversation_id,
                history=[],
                created_at=timestamp,
                updated_at=timestamp,
            )
        return Conversation(**data)

    def save_conversation(self, user_id: str, conv: Conversation):
        conv.updated_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        self._safe_write(self._conv_path(user_id, conv.conversation_id), conv.model_dump())

    def append_message(self, user_id: str, conversation_id: str, role: str, text: str) -> Conversation:
        """Añade un mensaje al historial con timestamp automático."""
        conv = self.load_conversation(user_id, conversation_id)
        msg = Message(
            role=role,
            message=text,
            timestamp=datetime.utcnow().isoformat(timespec="seconds") + "Z",
        )
        conv.history.append(msg)
        self.save_conversation(user_id, conv)
        return conv

    def get_history(self, user_id: str, conversation_id: str, last_n: Optional[int] = None) -> List[Message]:
        conv = self.load_conversation(user_id, conversation_id)
        if last_n is None or last_n >= len(conv.history):
            return conv.history
        return conv.history[-last_n:]

    def list_conversations(self, user_id: str) -> List[str]:
        idx = self._load_user_index(user_id)
        return idx.conversations

    def get_recent_context(self, user_id: str, n: int = 5):
        """Devuelve los últimos 'n' mensajes de la conversación más reciente."""
        user_dir = self._user_dir(user_id)
        conv_dir = user_dir / "conversations"

        if not conv_dir.exists():
            return []

        conv_files = sorted(
            list(conv_dir.glob("*.json")),
            key=os.path.getmtime,
            reverse=True,
        )

        if not conv_files:
            return []

        latest_conv = conv_files[0]

        try:
            with latest_conv.open("r", encoding="utf-8") as f:
                data = json.load(f)
                history = data.get("history", [])
                return history[-n:] if len(history) > n else history
        except Exception as e:
            print(f"[WARN] Error leyendo contexto reciente de {user_id}: {e}")
            return []
