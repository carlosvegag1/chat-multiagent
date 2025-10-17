# server.py — MCP Hotel Server
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import os
from datetime import date, timedelta

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)
from tools.toolhandler import list_tools, call_tool

app = FastAPI(title="MCP Hotel Server", version="1.0.0")

@app.get("/")
async def root():
    return {
        "status": "running ✅",
        "cwd": os.getcwd(),
        "routes": [str(r.path) for r in app.routes],
        "env_file": os.path.exists(".env"),
        "base_url": os.getenv("AMADEUS_BASE_URL"),
    }

@app.post("/messages")
async def handle_message(request: Request):
    payload = await request.json()
    method = payload.get("method")
    print(f"[DEBUG] MCP request recibido: {method}")

    if method == "tools/list":
        tools = list_tools()
        return {"jsonrpc": "2.0", "id": payload.get("id"), "result": tools}

    elif method == "tools/call":
        params = payload.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})

        # 🛟 Fallback automático de fechas
        if not args.get("checkin") or not args.get("checkout"):
            today = date.today()
            args["checkin"] = today.isoformat()
            args["checkout"] = (today + timedelta(days=3)).isoformat()

        print(f"[MCP] Ejecutando tool: {name} con args: {args}")
        try:
            result = call_tool(name, args)
            return {"jsonrpc": "2.0", "id": payload.get("id"), "result": result}
        except Exception as e:
            print(f"[ERROR] MCP tool {name} → {str(e)}")
            return {"jsonrpc": "2.0", "id": payload.get("id"), "error": str(e)}

    return {"jsonrpc": "2.0", "id": payload.get("id"), "error": f"Unknown method: {method}"}
