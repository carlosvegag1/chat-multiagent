import asyncio
import re
from typing import Dict, Any, List
from app.core.context_manager import ContextManager
from app.config.settings import MCP_ENDPOINTS
from app.agents.flight_agent import FlightAgent
from app.agents.hotel_agent import HotelAgent
from app.agents.weather_agent import WeatherAgent
from app.agents.destination_agent import DestinationAgent
from app.agents.calc_agent import CalcAgent
from openai import AsyncOpenAI


class Orchestrator:
    """Orquesta la comunicación A2A entre agentes, basándose en el contexto del usuario."""

    def __init__(self, openai_api_key: str, data_path: str = "data/v2"):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.context_manager = ContextManager(data_path)

    async def handle(self, user_id: str, conversation_id: str, message: str) -> Dict[str, Any]:
        """Flujo principal: interpretar intención, ejecutar agentes y fusionar resultados."""

        # 1️⃣ Obtener contexto del usuario
        context = self.context_manager.get_recent_context(user_id, n=5)

        # 2️⃣ Analizar intención con OpenAI
        intent = await self._detect_intent(message, context)

        # 3️⃣ Determinar qué agentes activar
        agents_to_call = self._select_agents(intent)

        # 4️⃣ Ejecutar los agentes seleccionados (A2A con asyncio.gather)
        results = await self._call_agents_parallel(agents_to_call, message, context)

        # 5️⃣ Generar respuesta natural combinada
        summary = await self._summarize_results(intent, results)

        # 6️⃣ Actualizar contexto persistente
        try:
            # Añadimos el mensaje del usuario
            self.context_manager.append_message(user_id, conversation_id, role="user", text=message)
            # Añadimos la respuesta del asistente
            self.context_manager.append_message(user_id, conversation_id, role="bot", text=summary)
        except Exception as e:
            print(f"[WARN] Error guardando contexto: {e}")

        return {
            "intent": intent,
            "agents_called": [a.name for a in agents_to_call],
            "results": results,
            "reply": summary
        }

    # ------------------ Funciones internas ------------------ #

    async def _detect_intent(self, message: str, context: List[Dict[str, Any]]) -> str:
        """Usa OpenAI para interpretar la intención del mensaje."""
        context_text = " ".join([c["message"] for c in context if c["role"] == "user"])
        prompt = f"""
        Contexto previo: {context_text}
        Nuevo mensaje: {message}

        Indica brevemente cuál es la intención principal (por ejemplo: buscar_vuelos, buscar_hoteles, obtener_clima, planificar_viaje, calcular_presupuesto).
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20
            )
            intent = response.choices[0].message.content.strip().lower()
            intent = re.sub(r"[^a-z_]", "", intent)
            return intent or "planificar_viaje"
        except Exception as e:
            print(f"[WARN] Error detectando intención: {e}")
            return "planificar_viaje"

    def _select_agents(self, intent: str):
        """Determina qué agentes usar según la intención."""
        mapping = {
            "buscar_vuelos": ["flight"],
            "buscar_hoteles": ["hotel"],
            "obtener_clima": ["weather"],
            "info_destino": ["destination"],
            "planificar_viaje": ["flight", "hotel", "weather", "destination", "calc"],
            "calcular_presupuesto": ["calc"]
        }
        selected = mapping.get(intent, ["flight", "hotel", "weather", "destination"])
        agents = []

        for name in selected:
            if name == "flight":
                agents.append(FlightAgent("flight", MCP_ENDPOINTS["flight"]))
            elif name == "hotel":
                agents.append(HotelAgent("hotel", MCP_ENDPOINTS["hotel"]))
            elif name == "weather":
                agents.append(WeatherAgent("weather", MCP_ENDPOINTS["weather"]))
            elif name == "destination":
                agents.append(DestinationAgent("destination", MCP_ENDPOINTS["destination"]))
            elif name == "calc":
                agents.append(CalcAgent("calc", "mock://calc"))
        return agents

    async def _call_agents_parallel(self, agents: List[Any], message: str, context: List[Dict[str, Any]]):
        """Ejecuta en paralelo los agentes seleccionados."""
        payload = self._extract_context_data(context, message)
        results = await asyncio.gather(*[agent.query(payload) for agent in agents])
        return results

    def _extract_context_data(self, context, message: str):
        """Extrae variables clave del contexto previo (destino, fechas, presupuesto)."""
        texto = " ".join([c["message"] for c in context if c["role"] == "user"]) + " " + message
        destino = re.search(r"(?:viaje a|destino|ir a)\s+([A-Za-zÁÉÍÓÚáéíóúñ\s]+)", texto)
        presupuesto = re.search(r"(\d{2,5})\s?(?:€|euros|eur)?", texto)
        fechas = re.findall(r"\d{4}-\d{2}-\d{2}", texto)

        return {
            "destino": destino.group(1).strip() if destino else "Londres",
            "presupuesto": int(presupuesto.group(1)) if presupuesto else 800,
            "fechas": fechas or ["2025-12-10", "2025-12-15"]
        }

    async def _summarize_results(self, intent: str, results: List[Dict[str, Any]]) -> str:
        """Combina la respuesta de todos los agentes en un texto coherente."""
        summary_prompt = f"""
        Intención: {intent}
        Datos de los agentes: {results}

        Genera una respuesta clara y natural para el usuario, en tono profesional y amable.
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"(Error generando resumen: {e})"
