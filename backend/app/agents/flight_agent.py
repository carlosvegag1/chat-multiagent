from typing import Dict, Any
from .base_agent import BaseAgent

class FlightAgent(BaseAgent):
    def _mock_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        destino = payload.get("destino", "Londres")
        fechas = payload.get("fechas", "10-15 diciembre")
        return {
            "agent": "flight_agent",
            "mock": True,
            "data": [
                {"vuelo": "IB1234", "destino": destino, "precio": 120, "fecha": fechas},
                {"vuelo": "BA4321", "destino": destino, "precio": 135, "fecha": fechas},
            ],
        }
