from typing import Dict, Any
from .base_agent import BaseAgent

class HotelAgent(BaseAgent):
    def _mock_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        destino = payload.get("destino", "Londres")
        presupuesto = payload.get("presupuesto", 800)
        return {
            "agent": "hotel_agent",
            "mock": True,
            "data": [
                {"nombre": "The Strand Palace", "precio": 740, "destino": destino},
                {"nombre": "Royal London", "precio": 690, "destino": destino},
            ],
            "presupuesto": presupuesto,
        }
