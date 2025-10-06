import asyncio
import json
from typing import Any, Dict
import httpx


class BaseAgent:
    """
    Plantilla base para agentes MCP.
    Cada agente define su endpoint y puede llamar a un servidor MCP real o usar datos mock.
    """

    def __init__(self, name: str, mcp_endpoint: str):
        self.name = name
        self.endpoint = mcp_endpoint

    async def query(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta la llamada MCP o devuelve datos mock."""
        # Si el endpoint empieza con "mock://", devolvemos datos simulados
        if self.endpoint.startswith("mock://"):
            return self._mock_response(payload)

        # Si es un endpoint real, hacemos una llamada HTTP
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(self.endpoint, json=payload)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                # En caso de error, devolvemos un mock de respaldo
                return {"error": str(e), "mock_fallback": self._mock_response(payload)}

    def _mock_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Debe ser implementado por cada subclase para simular sus datos."""
        raise NotImplementedError("Implementar en subclase concreta")
