# server.py — MCP Server (Flight / Hotel)
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import os

# 🔧 Cargar .env ANTES de importar toolhandler
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

from tools.toolhandler import list_tools, call_tool  # <-- ahora después

app = FastAPI(title="MCP Server", version="1.0.0")

@app.get("/")
async def root():
    return {
        "status": "running ✅",
        "cwd": os.getcwd(),
        "env_file": os.path.exists(".env"),
        "routes": [str(r.path) for r in app.routes],
        "base_url": os.getenv("AMADEUS_BASE_URL"),
        "has_key": bool(os.getenv("AMADEUS_API_KEY")),
    }

@app.post("/messages")
async def handle_message(request: Request):
    payload = await request.json()
    method = payload.get("method")
    print(f"[DEBUG] MCP request recibido: {method}")

    if method == "tools/list":
        tools = list_tools()
        return {"jsonrpc": "2.0", "id": payload.get("id"), "result": {"tools": tools}}

    elif method == "tools/call":
        params = payload.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})
        print(f"[MCP] Ejecutando tool: {name} con args: {args}")
        try:
            result = call_tool(name, args)
            return {"jsonrpc": "2.0", "id": payload.get("id"), "result": result}
        except Exception as e:
            print(f"[ERROR] MCP tool {name} → {str(e)}")
            return {"jsonrpc": "2.0", "id": payload.get("id"), "error": str(e)}

    return {"jsonrpc": "2.0", "id": payload.get("id"), "error": f"Unknown method: {method}"}
