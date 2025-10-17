from __future__ import annotations
import json
import os
import subprocess
import sys
from typing import Any, Dict, Optional, Tuple

import requests

class MCPClientError(Exception):
    pass

class MCPClient:
    """
    Cliente genérico para invocar herramientas MCP desde el backend.
    Soporta tres transportes:
      - HTTP:    endpoint REST/bridge que expone tools.invoke
      - WS:      (pendiente de ampliar) – placeholder
      - STDIO:   proceso local `server --stdio` (JSON-RPC)
    """
    def __init__(self, transport: str = "HTTP", timeout: int = 30):
        self.transport = transport.upper()
        self.timeout = timeout

    # =======================
    # Transporte: HTTP (bridge)
    # =======================
    def _invoke_http(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            resp = requests.post(endpoint, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise MCPClientError(f"[MCP HTTP] Error al invocar {endpoint}: {e}")

    # =======================
    # Transporte: STDIO (JSON-RPC simplificado)
    # =======================
    def _invoke_stdio(self, command: str, args: Optional[list[str]] = None, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Lanza un binario MCP con --stdio y le envía un request JSON-RPC.
        NOTA: Esto es un shell mínimo. Para producción, usa un cliente MCP completo.
        """
        if args is None:
            args = []
        proc = subprocess.Popen(
            [command] + args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Mensaje JSON-RPC (simplificado); ajusta a tu server
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools.invoke",
            "params": payload or {}
        }
        try:
            proc.stdin.write(json.dumps(request) + "\n")
            proc.stdin.flush()
            stdout, stderr = proc.communicate(timeout=self.timeout)
            if stderr:
                # Muchos servidores sacan logs por stderr; solo levantamos si hay "error"
                if "error" in stderr.lower():
                    raise MCPClientError(stderr.strip())
            # El server suele devolver múltiples líneas; tomamos la última JSON válida
            last_line = None
            for line in stdout.splitlines():
                line = line.strip()
                if line.startswith("{") and line.endswith("}"):
                    last_line = line
            if not last_line:
                raise MCPClientError("Respuesta STDIO vacía o no JSON.")
            return json.loads(last_line)
        except Exception as e:
            proc.kill()
            raise MCPClientError(f"[MCP STDIO] Error: {e}")

    # =======================
    # API pública
    # =======================
    def invoke_tool(self, *, endpoint: str | None = None, payload: Dict[str, Any], stdio_cmd: str | None = None, stdio_args: Optional[list[str]] = None) -> Dict[str, Any]:
        if self.transport == "HTTP":
            if not endpoint:
                raise MCPClientError("Falta endpoint HTTP MCP.")
            return self._invoke_http(endpoint, payload)
        elif self.transport == "STDIO":
            if not stdio_cmd:
                raise MCPClientError("Falta comando STDIO MCP.")
            return self._invoke_stdio(stdio_cmd, stdio_args or [], payload)
        else:
            raise MCPClientError(f"Transporte MCP no soportado: {self.transport}")
