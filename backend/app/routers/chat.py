from fastapi import APIRouter, Query
from fastapi import Form
from pydantic import BaseModel
from app.core.orchestrator.orchestrator import Orchestrator
from dotenv import load_dotenv
import os
import json

# Cargar la API Key desde el .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

router = APIRouter(prefix="/chat", tags=["Chat"])

# ---------- MODELO DE ENTRADA ----------
class ChatRequest(BaseModel):
    user_id: str
    conversation_id: str
    message: str

# ---------- ENDPOINT PRINCIPAL ----------
@router.post("/")
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint principal de conversación:
    - Recibe mensaje desde el frontend.
    - Llama al orquestador.
    - Devuelve respuesta, contexto y conversation_id.
    """
    orchestrator = Orchestrator(openai_api_key=OPENAI_API_KEY)

    # Llamar al orquestador
    result = await orchestrator.handle(
        user_id=request.user_id,
        conversation_id=request.conversation_id,
        message=request.message
    )

    # Estructura final para el frontend
    response = {
        "reply": result["reply"],
        "intent": result["intent"],
        "agents_called": result["agents_called"],
        "conversation_id": request.conversation_id,
        "context": result["results"]
    }

    return response

@router.get("/convos")
async def get_convos(user: str):
    """Devuelve todas las conversaciones de un usuario."""
    from app.core.context_manager import ContextManager
    cm = ContextManager("data/v2")
    convos = cm.list_conversations(user)
    return [{"convo_id": c, "created_at": "2025-10-06T00:00:00Z"} for c in convos]

@router.post("/new_convo")
async def new_convo(user: str = Form(...)):
    """Crea una nueva conversación."""
    from app.core.context_manager import ContextManager
    cm = ContextManager("data/v2")
    convo_id = cm.new_conversation(user)
    return {"convo_id": convo_id, "created_at": "2025-10-06T00:00:00Z"}
