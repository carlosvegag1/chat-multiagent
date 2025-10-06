# backend/whisper_api_test.py
"""
Prueba mínima y segura de la API de Whisper (OpenAI).
Ejecuta: python backend/whisper_api_test.py
Asegúrate de tener backend/.env con OPENAI_API_KEY=sk-...
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Falta OPENAI_API_KEY en backend/.env")

OpenAI.api_key = OPENAI_API_KEY

client = OpenAI()

def transcribe_local_file(file_path: str):
    with open(file_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    return transcript.text

if __name__ == "__main__":
    # Usa un fichero corto para la prueba, p.ej. test.wav (<= 15s), para minimizar coste.
    test_file = "test.wav"
    if not os.path.exists(test_file):
        print(f"Falta {test_file}. Genera o copia un WAV corto en la raíz (<= 25MB recomendado).")
    else:
        print("Transcribiendo", test_file)
        txt = transcribe_local_file(test_file)
        print("Transcripción resultante:")
        print(txt)
