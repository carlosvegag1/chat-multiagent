from typing import Dict, Any
from .base_agent import BaseAgent

class DestinationAgent(BaseAgent):
    def _mock_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        destino = payload.get("destino", "Londres")
        return {
            "agent": "destination_agent",
            "mock": True,
            "data": {
                "descripcion": f"{destino} es una ciudad con gran historia, arquitectura icónica y museos reconocidos.",
                "curiosidades": [
                    "El metro de Londres es el más antiguo del mundo.",
                    "Big Ben en realidad es el nombre de la campana, no de la torre.",
                ],
            },
        }
