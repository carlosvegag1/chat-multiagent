import os
import aiohttp
import asyncio
from app.utils.structured_logger import log

def _running_in_docker() -> bool:
    # Heurística estándar
    return os.path.exists("/.dockerenv") or os.getenv("RUNNING_IN_DOCKER") == "1"

class DestinationAgent:
    """📍 Agente MCP de destinos turísticos (Cliente)."""

    def __init__(self):
        # Default según entorno
        default_url = "http://destinations:8773" if _running_in_docker() else "http://127.0.0.1:8773"
        base_url = os.getenv("MCP_DESTINATION_URL", default_url)

        # Si corre en Docker y alguien dejó localhost/127.0.0.1, lo corregimos
        if _running_in_docker() and ("127.0.0.1" in base_url or "localhost" in base_url):
            base_url = "http://destinations:8773"

        self.base_url = base_url

        # Timeout propio del agente
        dest_to = int(os.getenv("MCP_DESTINATION_TIMEOUT_SECONDS", "45"))
        global_to = os.getenv("MCP_TIMEOUT_SECONDS")
        if global_to:
            try:
                dest_to = max(dest_to, int(global_to))
            except ValueError:
                pass
        self.timeout = max(dest_to, 30)  # nunca menos de 30s

        log.info(
            f"DestinationAgent conectado a: {self.base_url}",
            extra={"summary": "INIT_OK"}
        )
        log.info(
            f"DestinationAgent timeout (s): {self.timeout}",
            extra={"summary": "DEST_TIMEOUT"}
        )

    async def query(self, city: str, max_results: int = 6, days: int = 3, interests: str = "") -> dict:
        """Llama al MCP Destination y devuelve summary/pois/plan_sugerido."""
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "destination.get_summary",
                "arguments": {"city": city, "days": days, "interests": interests, "max_results": max_results}
            },
            "id": os.urandom(4).hex()
        }

        client_timeout = aiohttp.ClientTimeout(
            total=self.timeout,
            connect=min(self.timeout - 5, 20) if self.timeout > 10 else self.timeout
        )

        try:
            async with aiohttp.ClientSession(timeout=client_timeout) as session:
                async with session.post(f"{self.base_url}/messages", json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return self._fallback(city, f"Error HTTP {response.status}: {error_text}")

                    data = await response.json()

                    if "error" in data and data["error"]:
                        msg = data["error"].get("message", "Error desconocido del servidor de destinos")
                        return self._fallback(city, msg)

                    result = data.get("result", {})
                    if not result:
                        return self._fallback(city, "La respuesta del servidor de destinos estaba vacía.")

                    return {
                        "summary": result.get("summary", f"Resumen no disponible para {city}."),
                        "pois": result.get("pois", []),
                        "plan_sugerido": result.get("plan_sugerido", [])
                    }

        except asyncio.TimeoutError:
            return self._fallback(city, f"La solicitud al servidor de destinos tardó más de {self.timeout} segundos (Timeout).")
        except Exception as e:
            return self._fallback(city, str(e))

    def _fallback(self, city: str, reason: str) -> dict:
        log.warning(
            f"DestinationAgent activó fallback para '{city}'. Razón: {reason}",
            extra={"summary": "DEST_AGENT_FALLBACK"}
        )
        return {
            "error": f"No se pudo obtener la información del destino '{city}'. Razón: {reason}",
            "summary": f"No se pudo obtener la información del destino '{city}'.",
            "pois": [],
            "plan_sugerido": []
        }
