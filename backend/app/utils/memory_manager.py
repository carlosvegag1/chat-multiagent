# backend/app/utils/memory_manager.py
import json
import os
from typing import Dict, Any
import aiofiles
import aiofiles.os

class MemoryManager:
    """Gestor de memoria persistente y asÃ­ncrono por usuario."""

    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def _get_user_path(self, user_id: str) -> str:
        user_folder = os.path.join(self.base_path, user_id)
        os.makedirs(user_folder, exist_ok=True)
        return os.path.join(user_folder, "last_context.json")

    async def load_context(self, user_id: str) -> Dict[str, Any]:
        """Carga el contexto del usuario de forma asÃ­ncrona."""
        path = self._get_user_path(user_id)
        if not await aiofiles.os.path.exists(path):
            return {}
        try:
            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                content = await f.read()
                return json.loads(content) if content else {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    async def save_context(self, user_id: str, context: Dict[str, Any]) -> None:
        """Guarda el contexto completo del usuario de forma asÃ­ncrona."""
        path = self._get_user_path(user_id)
        try:
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(context, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"[ERROR] No se pudo guardar el contexto para {user_id}: {e}")

    async def clear_context(self, user_id: str):
        """Elimina el contexto de un usuario de forma asÃ­ncrona."""
        path = self._get_user_path(user_id)
        try:
            if await aiofiles.os.path.exists(path):
                await aiofiles.os.remove(path)
        except Exception as e:
            print(f"[ERROR] No se pudo eliminar el contexto para {user_id}: {e}")


