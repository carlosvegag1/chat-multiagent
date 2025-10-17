import os
import aiohttp
import asyncio
from app.utils.structured_logger import log
import os.path

def _running_in_docker() -> bool:
    return os.path.exists("/.dockerenv") or os.getenv("RUNNING_IN_DOCKER") == "1"

class FlightAgent:
    def __init__(self):
        default_url = "http://flights:8771" if _running_in_docker() else "http://127.0.0.1:8771"
        base_url = os.getenv("MCP_FLIGHT_URL", default_url)

        # Corrige localhost/127.0.0.1 cuando corre en Docker
        if _running_in_docker() and ("127.0.0.1" in base_url or "localhost" in base_url):
            base_url = "http://flights:8771"

        self.base_url = base_url
        self.timeout = int(os.getenv("MCP_TIMEOUT_SECONDS", "15"))

        log.info(f"FlightAgent conectado a: {self.base_url}", extra={"summary": "INIT_OK"})

    async def query(self, origin: str, destination: str, date: str, adults: int = 1, max_results: int = 5) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "flight.search_flights",
                "arguments": {
                    "origin": origin,
                    "destination": destination,
                    "date": date,
                    "adults": adults,
                    "max_results": max_results
                }
            },
            "id": os.urandom(4).hex()
        }

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(f"{self.base_url}/messages", json=payload) as response:
                    if response.status != 200:
                        err_text = await response.text()
                        return self._fallback(f"Servidor MCP respondió con {response.status}: {err_text}")

                    data = await response.json()
                    result = data.get("result", {})
                    flights = result.get("flights", [])
                    log.info(f"{len(flights)} vuelos recibidos desde {origin} a {destination}", extra={"tool": "FlightAgent"})
                    return result

        except aiohttp.ClientConnectorError:
            return self._fallback(f"No se pudo conectar al servidor de vuelos en {self.base_url}. ¿Está en ejecución?")
        except asyncio.TimeoutError:
            return self._fallback(f"La solicitud al servidor de vuelos tardó más de {self.timeout} segundos.")
        except Exception as e:
            return self._fallback(f"Fallo inesperado en la llamada: {e}")

    def _fallback(self, reason: str) -> dict:
        log.error(f"FlightAgent activó fallback. Razón: {reason}", extra={"summary": "FLIGHT_AGENT_FALLBACK"})
        return {"flights": [], "error": reason}
