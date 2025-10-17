import os, json
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from tools import toolhandler

load_dotenv()
app = FastAPI(title="MCP Calc Server (Presupuesto de viaje)")

@app.post("/messages")
async def handle_message(request: Request):
    body = await request.json()
    method = body.get("method")
    params = body.get("params", {})
    name = params.get("name")
    args = params.get("arguments", {}) or {}

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": body.get("id", 1),
            "result": [
                {
                    "name": "calc.estimate_budget",
                    "description": "Calcula el presupuesto total de un viaje (vuelos + hoteles).",
                    "parameters": {
                        "flights": "lista de vuelos",
                        "hotels": "lista de hoteles",
                        "checkin": "YYYY-MM-DD (opcional)",
                        "checkout": "YYYY-MM-DD (opcional)",
                    },
                }
            ],
        }

    elif method == "tools/call" and name == "calc.estimate_budget":
        result = toolhandler.estimate_budget(**args)
        return {"jsonrpc": "2.0", "id": body.get("id", 1), "result": result}

    return {
        "jsonrpc": "2.0",
        "id": body.get("id", 1),
        "error": {"code": -32601, "message": "Unknown method"},
    }
