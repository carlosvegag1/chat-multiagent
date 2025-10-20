# -*- coding: utf-8 -*-
import os, aiohttp, json

class HotelAgent:
    """🏨 Agente MCP de hoteles que conecta con el servidor MCP real de Amadeus."""

    def __init__(self):
        self.base_url = os.getenv("MCP_HOTEL_URL", "http://127.0.0.1:8772")
        self.timeout = int(os.getenv("MCP_TIMEOUT_SECONDS", "10"))
        print(f"[HotelAgent] Conectado a servidor MCP de hoteles: {self.base_url}")

    async def query(
        self,
        city: str,
        checkin: str,
        checkout: str,
        adults: int = 2,
        rooms: int = 1,
        max_results: int = 5
    ) -> dict:
        """Envía una petición JSON-RPC al servidor MCP de hoteles y devuelve los resultados estructurados."""
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "hotel.search_hotels",
                "arguments": {
                    "city": city,
                    "checkin": checkin,
                    "checkout": checkout,
                    "adults": adults,
                    "rooms": rooms,
                    "max_results": max_results
                }
            },
            "id": 1
        }

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(f"{self.base_url}/messages", json=payload) as response:
                    if response.status != 200:
                        return {"error": f"Servidor MCP respondió con {response.status}"}

                    data = await response.json()
                    hotels = data.get("result", {}).get("hotels", [])

                    formatted = []
                    for h in hotels:
                        formatted.append({
                            "name": h.get("name", "Hotel sin nombre"),
                            "stars": h.get("stars"),
                            "price": h.get("price"),
                            "currency": h.get("currency", "EUR"),
                            "address": h.get("address", ""),
                            "rating": h.get("rating"),
                            "url": h.get("url")
                        })

                    print(f"[HotelAgent] {len(formatted)} hoteles recibidos en {city}")
                    return {"hotels": formatted}

        except Exception as e:
            print(f"[HotelAgent][ERROR] {e}")
            return {"error": f"HotelAgent call failed: {str(e)}"}
