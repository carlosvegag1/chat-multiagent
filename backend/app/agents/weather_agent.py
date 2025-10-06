from typing import Dict, Any
from .base_agent import BaseAgent

class WeatherAgent(BaseAgent):
    def _mock_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        destino = payload.get("destino", "Londres")
        return {
            "agent": "weather_agent",
            "mock": True,
            "data": [
                {"fecha": "2025-12-10", "temperatura": "12°C", "estado": "nublado"},
                {"fecha": "2025-12-11", "temperatura": "13°C", "estado": "soleado"},
            ],
            "destino": destino,
        }
