# backend/main.py

from dotenv import load_dotenv
load_dotenv(override=True)

import os, tempfile, json, time, uuid, asyncio
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from openai import OpenAI

# 🔹 Importamos el orquestador real
from app.core.orchestrator.orchestrator import Orchestrator

# ---------------------------
# CONFIG
# ---------------------------
ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
CONVOS_DIR = os.path.join(DATA_DIR, "convos")
USERS_DIR = os.path.join(DATA_DIR, "users")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(CONVOS_DIR, exist_ok=True)
os.makedirs(USERS_DIR, exist_ok=True)

openai_key = os.getenv("OPENAI_API_KEY", "")
client = OpenAI(api_key=openai_key)
orchestrator = Orchestrator(openai_api_key=openai_key, data_path="data/v2")

app = FastAPI(title="Chat Multiagente - Backend Persistente")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Helpers
# ---------------------------
def convo_path(convo_id: str): return os.path.join(CONVOS_DIR, f"{convo_id}.json")
def user_path(user: str): return os.path.join(USERS_DIR, f"{user.lower()}.json")

def save_message(convo_id: str, role: str, text: str, user: str = "anon"):
    path = convo_path(convo_id)
    entry = {"ts": time.time(), "role": role, "text": text}
    if os.path.exists(path):
        with open(path, "r+", encoding="utf-8") as f:
            convo = json.load(f)
            convo["messages"].append(entry)
            f.seek(0)
            json.dump(convo, f, ensure_ascii=False, indent=2)
            f.truncate()
    else:
        convo = {
            "convo_id": convo_id,
            "user": user,
            "created_at": datetime.utcnow().isoformat(),
            "messages": [entry],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(convo, f, ensure_ascii=False, indent=2)

    # índice de usuario
    u_path = user_path(user)
    if os.path.exists(u_path):
        with open(u_path, "r+", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"user": user, "convos": []}
    if not any(c["convo_id"] == convo_id for c in data["convos"]):
        data["convos"].append({
            "convo_id": convo_id,
            "created_at": datetime.utcnow().isoformat(),
        })
    with open(u_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------
# Endpoints
# ---------------------------

@app.post("/new_convo")
def new_convo(user: str = Form(...)):
    convo_id = f"{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{uuid.uuid4().hex[:6]}"
    convo = {
        "convo_id": convo_id,
        "user": user.lower(),
        "created_at": datetime.utcnow().isoformat(),
        "messages": [],
    }
    with open(convo_path(convo_id), "w", encoding="utf-8") as f:
        json.dump(convo, f, ensure_ascii=False, indent=2)
    u_path = user_path(user)
    if os.path.exists(u_path):
        with open(u_path, "r+", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"user": user.lower(), "convos": []}
    data["convos"].append({
        "convo_id": convo_id,
        "created_at": convo["created_at"]
    })
    with open(u_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return convo


@app.get("/convos")
def list_convos(user: str):
    u_path = user_path(user)
    if not os.path.exists(u_path):
        return []
    with open(u_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return sorted(data["convos"], key=lambda x: x["created_at"], reverse=True)


@app.get("/convo/{convo_id}")
def get_convo(convo_id: str):
    path = convo_path(convo_id)
    if not os.path.exists(path):
        return {"messages": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/chat/")
async def chat_text(request: Request):
    """
    Conecta el chat con el orquestador real (fase 3).
    """
    try:
        if request.headers.get("content-type", "").startswith("application/json"):
            data = await request.json()
            message = data.get("message", "")
            convo_id = data.get("convo_id", "default")
            user = data.get("user", "anon")
        else:
            form = await request.form()
            message = form.get("message")
            convo_id = form.get("convo_id", "default")
            user = form.get("user", "anon")
    except Exception as e:
        return {"error": f"Error leyendo entrada: {e}"}

    # Guardar mensaje del usuario en log simple
    save_message(convo_id, "user", message, user)

    # 🔹 Llamada al orquestador real
    result = await orchestrator.handle(user, convo_id, message)
    reply = result.get("reply", "[Sin respuesta del orquestador]")

    # Guardar respuesta del bot
    save_message(convo_id, "bot", reply, user)

    return {
        "reply": reply,
        "intent": result.get("intent"),
        "agents_called": result.get("agents_called"),
        "conversation_id": convo_id
    }


@app.post("/chat/audio")
async def chat_audio(file: UploadFile = File(...), convo_id: str = Form("default"), user: str = Form("anon")):
    suffix = os.path.splitext(file.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    saved_path = os.path.join(UPLOADS_DIR, os.path.basename(tmp_path))
    os.replace(tmp_path, saved_path)
    transcription = f"(transcripción simulada de {file.filename})"
    save_message(convo_id, "user_audio", transcription, user)
    result = await orchestrator.handle(user, convo_id, transcription)
    reply = result.get("reply", "[Sin respuesta del orquestador]")
    save_message(convo_id, "bot", reply, user)
    return {"transcription": transcription, "reply": reply, "conversation_id": convo_id}
