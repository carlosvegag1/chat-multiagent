# backend/main.py
"""
FastAPI backend minimal para el MVP.
- Endpoints: /chat/text , /chat/audio
- Guarda conversaciones en backend/data/{convo_id}.json
- Opcional: transcripción local con Whisper (si está instalado)
"""

import os
import tempfile
import json
import time
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------
# CONFIG (SUSTITUIR si quieres)
# ---------------------------
# Orígenes permitidos (cambia si tu frontend corre en otra URL)
ALLOWED_ORIGINS = ["http://localhost:3000"]

# Nombre del modelo Whisper a cargar en modo local (si usas Whisper). 
# Opciones típicas: "tiny", "base", "small", "medium", "large"
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME", "tiny")

# Si no quieres usar transcripción local, pon TRANSCRIBE_LOCAL = False
# TRANSCRIBE_LOCAL = os.getenv("TRANSCRIBE_LOCAL", "1") == "1"
TRANSCRIBE_LOCAL = False
# ---------------------------

app = FastAPI(title="Chat Multiagente - Backend MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# ---------------------------
# Intentional: carga optional de Whisper
# ---------------------------
whisper_model = None
if TRANSCRIBE_LOCAL:
    try:
        import whisper  # type: ignore
        print(f"[INFO] Cargando modelo Whisper '{WHISPER_MODEL_NAME}' ... (puede tardar)")
        whisper_model = whisper.load_model(WHISPER_MODEL_NAME)
        print("[INFO] Modelo Whisper cargado.")
    except Exception as e:
        print("[WARN] No se pudo cargar whisper. Transcripción local desactivada.")
        print("Error:", e)
        whisper_model = None

# ---------------------------
# Helper: guardar mensajes (persistencia simple JSON)
# ---------------------------
def save_message(convo_id: str, role: str, text: str):
    path = os.path.join(DATA_DIR, f"{convo_id}.json")
    entry = {"ts": time.time(), "role": role, "text": text}
    if os.path.exists(path):
        with open(path, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"convo_id": convo_id, "messages": []}
            data["messages"].append(entry)
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()
    else:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"convo_id": convo_id, "messages": [entry]}, f, ensure_ascii=False, indent=2)

# ---------------------------
# Stub del "sistema multiagente"
# ---------------------------
def process_with_agents(user_text: str) -> str:
    """
    REEMPLAZA esta función por tu orquestador/multiagente.
    Por ahora devuelve una respuesta demostrativa.
    """
    # Ejemplo simple de combinación de "agentes"
    a1 = f"[Resumidor] {user_text[:200]}"
    a2 = f"[Planificador] Acción sugerida: genera respuesta clara y concisa."
    final = f"{a1}\n{a2}\n\nRespuesta final (demo): {user_text}"
    return final

# ---------------------------
# Endpoints
# ---------------------------

@app.post("/chat/text")
async def chat_text(message: str = Form(...), convo_id: str = Form("default")):
    """Enviar texto al sistema."""
    save_message(convo_id, "user", message)
    response = process_with_agents(message)
    save_message(convo_id, "bot", response)
    return {"response": response}

@app.post("/chat/audio")
async def chat_audio(file: UploadFile = File(...), convo_id: str = Form("default")):
    """
    Subir un archivo de audio. Si Whisper local está activo, intentará transcribir.
    Devuelve {"transcription": str, "response": str}
    """
    # Guardar archivo temporal en uploads
    suffix = os.path.splitext(file.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    saved_path = os.path.join(UPLOADS_DIR, os.path.basename(tmp_path))
    os.replace(tmp_path, saved_path)

    transcription = ""
    if whisper_model is not None:
        try:
            # Nota: whisper.load_model devuelve un objeto con método transcribe
            result = whisper_model.transcribe(saved_path, language="es")
            transcription = result.get("text", "").strip()
        except Exception as e:
            transcription = ""
            print("[WARN] Error transcribiendo con Whisper:", e)

    # Si no se pudo transcribir, registramos que llegó audio bruto
    if transcription:
        save_message(convo_id, "user_audio", transcription)
    else:
        save_message(convo_id, "user_audio", f"[audio recibido: {os.path.basename(saved_path)}]")

    response = process_with_agents(transcription or f"(audio:{os.path.basename(saved_path)})")
    save_message(convo_id, "bot", response)

    return {"transcription": transcription, "response": response, "saved_file": os.path.basename(saved_path)}
