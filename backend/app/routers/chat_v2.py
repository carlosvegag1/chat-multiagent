import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv

from app.core.schemas import ChatRequest, ChatResponse
from app.core.context_manager import ContextManager

# Cargar .env aquí también por si el router se inicializa antes que main
load_dotenv(override=True)

router = APIRouter()

# BASE_DIR = backend/
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_ROOT = BASE_DIR / "data" / "v2"
DATA_ROOT.mkdir(parents=True, exist_ok=True)

context = ContextManager(data_root=DATA_ROOT)

@router.get("/health")
def v2_health():
    return {
        "status": "ok",
        "data_root": str(DATA_ROOT),
        "openai_key_loaded": bool(os.getenv("OPENAI_API_KEY"))
    }

@router.post("/chat", response_model=ChatResponse)
def v2_chat(req: ChatRequest):
    # 1) asegurar conversation_id
    if not req.conversation_id or not context.conversation_exists(req.user_id, req.conversation_id):
        conversation_id = context.new_conversation(req.user_id)
    else:
        conversation_id = req.conversation_id

    # 2) guardar mensaje user
    context.append_message(req.user_id, conversation_id, role="user", text=req.message)

    # 3) respuesta mínima (eco). En FASE 3 se sustituirá por el orquestador
    reply_text = (
        "✅ (v2) Mensaje recibido y guardado.\n\n"
        "En próximas fases recuperaré automáticamente fechas/destino/presupuesto de tu historial."
        f"\nÚltimo mensaje: «{req.message}»"
    )

    # 4) guardar respuesta bot
    context.append_message(req.user_id, conversation_id, role="bot", text=reply_text)

    # 5) snapshot (últimos 10)
    snapshot = context.get_history(req.user_id, conversation_id, last_n=10)

    return ChatResponse(
        conversation_id=conversation_id,
        reply=reply_text,
        context_snapshot=snapshot
    )
