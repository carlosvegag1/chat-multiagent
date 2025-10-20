# backend/main.py

from dotenv import load_dotenv
load_dotenv(override=True)

import os, tempfile, json, uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from pathlib import Path
import openai  # 👈 Ahora usamos la API de OpenAI para Whisper remoto

from app.core.orchestrator.orchestrator import Orchestrator
from app.core.schemas import StructuredChatResponse, Message, Conversation, StructuredReply

# ---------------------------
# CONFIG
# ---------------------------
ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

DATA_BASE_DIR = os.path.join(os.path.dirname(__file__), "data", "v2")
CONVOS_DIR = os.path.join(DATA_BASE_DIR, "convos")
USERS_DIR = os.path.join(DATA_BASE_DIR, "users")
UPLOADS_DIR = os.path.join(DATA_BASE_DIR, "uploads")

os.makedirs(CONVOS_DIR, exist_ok=True)
os.makedirs(USERS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Clave API
openai.api_key = os.getenv("OPENAI_API_KEY", "")
orchestrator = Orchestrator(openai_api_key=openai.api_key, data_path=DATA_BASE_DIR)

# ---------------------------
# APP
# ---------------------------
app = FastAPI(title="Chat Multiagente - Backend con Whisper API (Cloud)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Helpers de persistencia
# ---------------------------
def convo_path(convo_id: str) -> str:
    return os.path.join(CONVOS_DIR, f"{convo_id}.json")

def user_convos_list_path(user: str) -> str:
    user_dir = os.path.join(USERS_DIR, user.lower())
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, "user_convos_list.json")

def save_structured_message(convo_id: str, message_obj: Message, user: str):
    path = convo_path(convo_id)
    try:
        if os.path.exists(path):
            with open(path, "r+", encoding="utf-8") as f:
                convo_data = json.load(f)
                convo = Conversation(**convo_data)
                convo.messages.append(message_obj)
                f.seek(0)
                f.write(convo.model_dump_json(indent=2))
                f.truncate()
        else:
            convo = Conversation(convo_id=convo_id, user=user.lower(), messages=[message_obj])
            with open(path, "w", encoding="utf-8") as f:
                f.write(convo.model_dump_json(indent=2))
    except Exception as e:
        print(f"Error al guardar mensaje estructurado en {convo_id}: {e}")

# ---------------------------
# ENDPOINTS DE CONVERSACIÓN
# ---------------------------
@app.post("/new_convo", response_model=Conversation)
def new_convo(user: str = Form(...)):
    convo_id = f"{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{uuid.uuid4().hex[:6]}"
    new_convo_obj = Conversation(convo_id=convo_id, user=user.lower())

    with open(convo_path(convo_id), "w", encoding="utf-8") as f:
        f.write(new_convo_obj.model_dump_json(indent=2))

    u_path = user_convos_list_path(user)
    user_convos = []
    if os.path.exists(u_path):
        with open(u_path, "r", encoding="utf-8") as f:
            user_convos = json.load(f)

    user_convos.append({"convo_id": convo_id, "created_at": new_convo_obj.created_at})
    user_convos.sort(key=lambda x: x["created_at"], reverse=True)

    with open(u_path, "w", encoding="utf-8") as f:
        json.dump(user_convos, f, indent=2)

    return new_convo_obj


@app.get("/convos", response_model=List[Dict[str, str]])
def list_convos(user: str):
    u_path = user_convos_list_path(user)
    if not os.path.exists(u_path):
        return []
    with open(u_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/convo/{convo_id}", response_model=Conversation)
def get_convo(convo_id: str):
    path = convo_path(convo_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ---------------------------
# ENDPOINT DE CHAT (TEXTO)
# ---------------------------
@app.post("/chat/", response_model=StructuredChatResponse)
async def chat_text(message: str = Form(...), convo_id: str = Form(...), user: str = Form(...)):
    user_message = Message(role="user", text=message)
    save_structured_message(convo_id, user_message, user)

    result = await orchestrator.handle(user, convo_id, message)
    structured_data_obj = StructuredReply(**result.get("structured_data", {})) if result.get("structured_data") else None

    bot_message = Message(role="bot", text=str(result.get("reply_text", "")), structured_data=structured_data_obj)
    save_structured_message(convo_id, bot_message, user)

    return StructuredChatResponse(
        conversation_id=convo_id,
        intent=result.get("intent"),
        reply_text=bot_message.text,
        structured_data=bot_message.structured_data,
        agents_called=result.get("agents_called", []),
    )

# ---------------------------
# ENDPOINT DE AUDIO (WHISPER API)
# ---------------------------
@app.post("/chat/audio")
async def chat_audio(file: UploadFile = File(...), convo_id: str = Form(...), user: str = Form(...)):
    # Guardar temporalmente el audio
    suffix = Path(file.filename).suffix or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        print(f"🗣️ Enviando audio a Whisper API (OpenAI)...")
        with open(tmp_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="es"
            )
        transcription = transcript.text.strip()
        print(f"✅ Transcripción obtenida: {transcription[:80]}...")
    except Exception as e:
        transcription = f"(Error en transcripción remota: {e})"
    finally:
        os.remove(tmp_path)

    # Guardar mensaje de usuario
    user_message = Message(role="user", text=transcription)
    save_structured_message(convo_id, user_message, user)

    # Llamar al orquestador
    result = await orchestrator.handle(user, convo_id, transcription)
    structured_data_obj = StructuredReply(**result.get("structured_data", {})) if result.get("structured_data") else None

    bot_message = Message(
        role="bot",
        text=str(result.get("reply_text", "")),
        structured_data=structured_data_obj,
    )
    save_structured_message(convo_id, bot_message, user)

    return {
        "conversation_id": convo_id,
        "intent": result.get("intent"),
        "reply_text": bot_message.text,
        "structured_data": bot_message.structured_data,
        "agents_called": result.get("agents_called", []),
        "transcription": transcription,
    }

# ---------------------------
@app.get("/")
def root():
    return {"message": "🚀 Backend del Chat Multiagente operativo con Whisper API (OpenAI Cloud)"}
