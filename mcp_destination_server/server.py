# mcp_destination_server/server.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
import os, json, traceback
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="MCP Destination Server (Bulletproof & Adaptive)", version="3.2.0")

# --- CONFIGURACIÓN DEL CLIENTE LLM ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("[DestinationServer] ADVERTENCIA: La variable de entorno OPENAI_API_KEY no está configurada.")
    client = None
else:
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

LLM_MODEL = "gpt-4o-mini"

# --- ✅ PROMPT MAESTRO ESTANDARIZADO Y MÁS PRECISO ---
SYSTEM_PROMPT_TEMPLATE = """
Eres un agente de viajes experto y un asistente de planificación de itinerarios. Tu misión es generar un plan de viaje completo y atractivo para un usuario, basado en una ciudad y una duración en días.

Tu respuesta DEBE ser un único objeto JSON válido, sin ningún texto adicional. El JSON debe seguir estrictamente la siguiente estructura y formato. No omitas NINGUNA clave, incluso si las listas están vacías.
{
  "summary": "Un resumen conciso y atractivo del destino (2-3 frases).",
  "pois": [
    {"name": "Nombre del Punto de Interés 1", "description": "Descripción breve y útil (1 frase)."},
    {"name": "Nombre del Punto de Interés 2", "description": "Descripción breve y útil (1 frase)."}
  ],
  "plan_sugerido": [
    {"day": 1, "activities": ["Actividad 1 del Día 1", "Actividad 2 del Día 1"]},
    {"day": 2, "activities": ["Actividad 1 del Día 2", "Actividad 2 del Día 2"]}
  ]
}

## REGLAS CRÍTICAS E INQUEBRANTABLES:
1.  **FORMATO JSON ESTRICTO**: Tu salida debe ser exclusivamente el objeto JSON especificado. Las tres claves principales (`summary`, `pois`, `plan_sugerido`) son OBLIGATORIAS.
2.  **PLAN 100% ADAPTATIVO**: La lista "plan_sugerido" DEBE contener exactamente el número de objetos de día que se especifique en la variable `{{days}}`. Si `{{days}}` es 5, la lista "plan_sugerido" debe tener 5 elementos.
3.  **CONTENIDO REAL Y RELEVANTE**: Toda la información (resumen, POIs, actividades) debe ser verídica y pertinente para la ciudad `{{city}}`.
"""

async def _generate_dynamic_travel_plan(city: str, days: int, max_pois: int = 6) -> Dict[str, Any]:
    if not client:
        raise ValueError("Cliente OpenAI no configurado. Falta la variable de entorno OPENAI_API_KEY.")

    prompt = SYSTEM_PROMPT_TEMPLATE.replace("{{city}}", city).replace("{{days}}", str(days))

    try:
        print(f"[DestinationAgent] Generando plan de {days} día(s) para {city} con LLM (versión robusta).")
        completion = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Por favor, genera el plan de viaje JSON para {city} durante {days} días."}
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        response_content = completion.choices[0].message.content
        plan_data = json.loads(response_content)

        # ✅ Validación más estricta de la respuesta del LLM
        if "summary" not in plan_data or "pois" not in plan_data or "plan_sugerido" not in plan_data:
            raise ValueError("La respuesta del LLM no contiene la estructura esperada (faltan claves obligatorias).")

        plan_data["pois"] = plan_data.get("pois", [])[:max_pois]
        
        print(f"[DestinationAgent] Plan para {city} generado y validado con éxito.")
        return plan_data

    except Exception as e:
        # ✅ Lanza la excepción para que sea capturada por el manejador principal
        print(f"[DestinationAgent] ERROR generando plan con LLM para '{city}': {e}\n{traceback.format_exc()}")
        raise ValueError(f"Error en la llamada al LLM para generar el plan: {str(e)}")


@app.post("/messages")
async def handle_message(req: Request):
    rpc_id = None
    try:
        payload = await req.json()
        rpc_id = payload.get("id")
        params = payload.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {}) or {}

        if name != "destination.get_summary":
            return JSONResponse({"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32601, "message": "Method not found"}}, status_code=400)

        city = (args.get("city") or "Destino").title()
        days = int(args.get("days", 3))
        max_results = int(args.get("max_results", 6))

        plan_data = await _generate_dynamic_travel_plan(city, days, max_results)
        
        # ✅ ESTANDARIZADO: La clave de respuesta ahora es "plan_sugerido".
        result = {
            "city": city,
            "summary": plan_data.get("summary", ""),
            "pois": plan_data.get("pois", []),
            "plan_sugerido": plan_data.get("plan_sugerido", [])
        }

        return JSONResponse({"jsonrpc": "2.0", "id": rpc_id, "result": result})

    except Exception as e:
        # ✅ MANEJO DE ERRORES EXPLÍCITO: Devuelve un error JSON-RPC detallado.
        error_message = f"Error crítico en DestinationServer: {str(e)}"
        print(error_message)
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32000, "message": error_message}
            }
        )