# app/agents/base_agent.py
from __future__ import annotations
import os
import json
import httpx
from typing import Any, Dict, Optional

class BaseAgent:
    """
    Base para agentes MCP vÃ­a HTTP JSON-RPC 2.0.
    ConvenciÃ³n: el endpoint expone POST /messages que recibe el payload JSON-RPC.
    """

    def __init__(self, name: str, endpoint: str, timeout: Optional[float] = None) -> None:
        self.name = name
        self.endpoint = endpoint.rstrip("/")
        # usa MCP_TIMEOUT_SECONDS por defecto si no pasas timeout
        self.timeout = timeout or float(os.getenv("MCP_TIMEOUT_SECONDS", "10"))

    def _build_payload(self, **kwargs) -> Dict[str, Any]:
        """
        Cada agente debe implementar esto para devolver:
        {
          "jsonrpc": "2.0",
          "id": 1,
          "method": "tools/call",
          "params": {"name": "<tool>", "arguments": {...}}
        }
        """
        raise NotImplementedError

    async def query(self, **kwargs) -> Dict[str, Any]:
        """
        Llama al MCP (POST /messages) con el payload que genera _build_payload.
        Devuelve el JSON del servidor o {"error": "..."}.
        """
        payload = self._build_payload(**kwargs)
        url = f"{self.endpoint}/messages"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code not in (200, 202):
                    return {"error": f"HTTP {resp.status_code}: {resp.text}"}
                # el servidor MCP puede devolver JSON-RPC o un JSON plano de datos
                data = resp.json()
                # Si viene envuelto tipo JSON-RPC con "result", intenta destapar
                if isinstance(data, dict) and "result" in data and isinstance(data["result"], dict):
                    return data["result"]
                return data
        except Exception as e:
            return {"error": f"{self.name} call failed: {e}"}

