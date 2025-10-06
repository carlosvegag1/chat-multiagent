from typing import Dict, Any
from .base_agent import BaseAgent

class CalcAgent(BaseAgent):
    def _mock_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        vuelos = payload.get("vuelos", [120, 135])
        hoteles = payload.get("hoteles", [740, 690])
        total_medio = (sum(vuelos) / len(vuelos)) + (sum(hoteles) / len(hoteles)) / len(hoteles)
        return {
            "agent": "calc_agent",
            "mock": True,
            "data": {"presupuesto_estimado": round(total_medio, 2)},
        }
