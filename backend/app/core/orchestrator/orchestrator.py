from __future__ import annotations
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from datetime import datetime, timedelta
import os, json, asyncio, re

from app.utils.structured_logger import log
from app.agents.travel_memory_agent import TravelMemoryAgent
from app.agents.flight_agent import FlightAgent
from app.agents.hotel_agent import HotelAgent
from app.agents.destination_agent import DestinationAgent
from app.agents.calc_agent import CalcAgent
from app.agents.normalizer_agent import NormalizerAgent
from app.utils.memory_manager import MemoryManager
import app.utils.travel_log_manager as tlm
from app.utils.travel_log_manager import normalize_city, add_city_to_cache
from app.core.schemas import FlightInfo, HotelInfo, BudgetInfo

DEFAULT_ORIGIN_IATA = os.getenv("DEFAULT_ORIGIN_IATA", "MAD")

def _next_friday_from_today() -> datetime:
    today = datetime.now()
    return (today + timedelta(days=(4 - today.weekday() + 7) % 7)).replace(hour=0, minute=0, second=0, microsecond=0)

def _iso_date(d: datetime) -> str:
    return d.date().isoformat()

class Orchestrator:
    def __init__(self, openai_api_key: str, data_path: str = "data/v2"):
        self.data_path = data_path
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.memory_manager = MemoryManager(os.path.join(data_path, "users"))
        self.normalizer_agent = NormalizerAgent(openai_api_key=openai_api_key, cache_path=os.path.join(data_path, "users"))
        self.destination_agent = DestinationAgent()
        self.flight_agent = FlightAgent()
        self.hotel_agent = HotelAgent()
        self.calc_agent = CalcAgent()
        self.travel_memory_agent = TravelMemoryAgent(data_path=os.path.join(data_path, "users"))
        log.info("Orchestrator (V2 - Modular) inicializado.", extra={"summary": "INIT_OK"})

    def _ensure_travel_log(self, user_id: str):
        user_dir = os.path.join(self.data_path, "users", user_id)
        os.makedirs(user_dir, exist_ok=True)
        travel_log_path = os.path.join(user_dir, "travel_log.json")
        if not os.path.exists(travel_log_path):
            log.info(f"Creando travel_log.json para {user_id}", extra={"summary": "CREATE_LOG"})
            with open(travel_log_path, "w", encoding="utf-8") as f:
                json.dump({"user_id": user_id, "created_at": datetime.now().isoformat(), "trips": []}, f, indent=2)

    async def _geo_normalize(self, location: str) -> str:
        prompt = (f"Un usuario quiere planificar un viaje a '{location}'. Para buscar vuelos y hoteles, ¿cuál es la ciudad principal y más práctica, "
                  f"que probablemente tenga un aeropuerto internacional (IATA)? Responde solo con el nombre de la ciudad. "
                  f"Ejemplos:\n- 'Provenza' -> 'Marsella'\n- 'Toscana' -> 'Florencia'\n- 'Costa Amalfitana' -> 'Nápoles'")
        try:
            completion = await self.client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.0)
            city = completion.choices[0].message.content.strip().replace(".", "")
            log.info(f"Geo-normalización inteligente: '{location}' -> '{city}'", extra={"summary": "GEO_NORM_SMART"})
            return city
        except Exception:
            return location
    
    async def _find_iata_dynamically(self, city_name: str) -> Optional[str]:
        prompt = (f"¿Cuál es el principal código de aeropuerto IATA de 3 letras para la ciudad de '{city_name}'? "
                  "Responde únicamente con el código de 3 letras. Si no estás seguro o no existe, responde 'N/A'.\n"
                  "Ejemplos:\n- 'Cusco' -> 'CUZ'\n- 'Marrakech' -> 'RAK'\n- 'Zanzíbar' -> 'ZNZ'")
        try:
            completion = await self.client.chat.completions.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.0
            )
            code = completion.choices[0].message.content.strip().upper()
            if re.fullmatch(r"^[A-Z]{3}$", code):
                return code
            return None
        except Exception as e:
            log.error(f"Error al buscar IATA dinámicamente para '{city_name}': {e}", extra={"summary": "IATA_FIND_FAIL"})
            return None

    async def handle(self, user_id: str, conversation_id: str, message: str) -> Dict[str, Any]:
        self._ensure_travel_log(user_id)
        last_context = await self.memory_manager.load_context(user_id)
        
        context_for_norm = {}
        if last_context.get("clarification_needed"):
            context_for_norm = {"clarification_needed": True, "pending_intent": last_context.get("pending_intent")}
        elif "last_city" in last_context:
            context_for_norm["last_city"] = last_context["last_city"]

        normalized = await self.normalizer_agent.normalize(user_id, message, context_for_norm)
        intent, entities = normalized.get("intent"), normalized.get("entities", {})

        if last_context.get("clarification_needed") and last_context.get("pending_intent"):
            pending_intent = last_context["pending_intent"]
            intent = pending_intent["intent"]
            final_entities = pending_intent.get("entities", {})
            final_entities.update(entities)
            entities = final_entities
            log.info(f"BLINDAJE DE CLARIFICACIÓN: Intención forzada a '{intent}'.", extra={"summary": "CLARIFICATION_SHIELD_APPLIED"})

        if "city" not in entities and "last_city" in context_for_norm:
            entities["city"] = context_for_norm["last_city"]

        if "city" in entities and entities["city"] and entities["city"] != "*":
            original = entities["city"]
            _, is_iata = normalize_city(original)
            if not is_iata:
                entities["city"] = await self._geo_normalize(original)

        log.info(f"Intención final: {intent}, Entidades: {entities}", extra={"intent": intent})

        # --- Lógica de Despacho Principal ---
        search_intents = ["PLAN_TRIP", "SEARCH_FLIGHTS", "SEARCH_HOTELS", "GET_DESTINATION_INFO"]
        memory_intents = ["LIST_TRIPS", "SHIFT_TRIP", "EXTEND_TRIP", "SHORTEN_TRIP", "DELETE_TRIP"]

        result_data: Dict[str, Any] = {}
        agents_called: List[str] = []

        if intent in search_intents:
            if not entities.get("city"):
                return self._end_conversation(
                    user_id, conversation_id, message,
                    "No he entendido a qué destino te refieres. ¿Podrías indicármelo?",
                    "ERROR_NO_CITY", entities
                )
            result_data, agents_called = await self._dispatch_and_gather_tasks(intent, entities)

        elif intent in memory_intents:
            result_data = await self._handle_memory_op(intent, entities, user_id)
            agents_called = [intent.lower()]
        
        else:  # UNKNOWN o intenciones no manejadas
            reply_text = "No he entendido bien tu petición. Puedo planificar viajes, buscar vuelos u hoteles, y darte información sobre destinos."
            return self._end_conversation(user_id, conversation_id, message, reply_text, intent, entities)

        structured_reply, reply_text = self._summarize(user_id, intent, entities, result_data)

        # Actualizar contexto para el siguiente turno
        current_city = entities.get("city") or result_data.get("city")
        new_context = {"last_intent": intent}
        if current_city and current_city != "*":
            new_context["last_city"] = current_city
        
        return self._end_conversation(
            user_id, conversation_id, message, reply_text, intent, entities,
            structured_reply, agents_called, new_context
        )

    def _end_conversation(self, user_id, conv_id, msg, reply_text, intent, args, structured_data=None, tool=None, context=None):
        asyncio.create_task(self.memory_manager.save_context(user_id, context or {}))
        return {
            "intent": intent, "args": args,
            "structured_data": structured_data or {},
            "reply_text": reply_text, "agents_called": tool or []
        }

    # --- ✅ NUEVO CEREBRO MODULAR ---
    async def _dispatch_and_gather_tasks(self, intent: str, entities: Dict[str, Any]) -> tuple[Dict[str, Any], List[str]]:
        city_norm, iata_norm = normalize_city(entities.get("city", ""))
        if not iata_norm:
            log.info(f"IATA para '{city_norm}' no en caché. Buscando dinámicamente...", extra={"summary": "IATA_CACHE_MISS"})
            iata_norm = await self._find_iata_dynamically(city_norm)
            if iata_norm:
                add_city_to_cache(city_norm, iata_norm)
        
        n_days = entities.get("days")
        if not isinstance(n_days, int) or n_days <= 0:
            n_days = 3
        
        adults = entities.get("adults", 1)
        start_dt = _next_friday_from_today()
        checkin = _iso_date(start_dt)
        checkout = _iso_date(start_dt + timedelta(days=n_days))
        destination_query = iata_norm or city_norm

        tasks = []
        agents_to_call: List[str] = []
        
        # Construir lista de tareas basadas en la intención
        if intent in ["PLAN_TRIP", "SEARCH_FLIGHTS"]:
            tasks.append(self.flight_agent.query(origin=DEFAULT_ORIGIN_IATA, destination=destination_query, date=checkin, adults=adults))
            agents_to_call.append("flight")
        if intent in ["PLAN_TRIP", "SEARCH_HOTELS"]:
            tasks.append(self.hotel_agent.query(city=destination_query, checkin=checkin, checkout=checkout, adults=adults))
            agents_to_call.append("hotel")
        if intent in ["PLAN_TRIP", "GET_DESTINATION_INFO"]:
            tasks.append(self.destination_agent.query(city=city_norm, days=n_days))
            agents_to_call.append("destination")

        # Ejecutar tareas en paralelo
        results = await asyncio.gather(*tasks)
        
        # Fusionar resultados
        merged_results: Dict[str, Any] = {
            "city": city_norm, "iata": iata_norm,
            "checkin": checkin, "checkout": checkout, "adults": adults
        }
        for res in results:
            merged_results.update(res)

        # Llamar a la calculadora de presupuesto si tenemos datos de vuelos u hoteles
        if "flights" in merged_results or "hotels" in merged_results:
            budget_resp = await self.calc_agent.query(
                flights=merged_results.get("flights", []),
                hotels=merged_results.get("hotels", []),
                checkin=checkin, checkout=checkout, adults=adults
            )
            merged_results["budget"] = budget_resp.get("total_eur")
            agents_to_call.append("calc")

        return merged_results, agents_to_call

    async def _handle_memory_op(self, intent: str, args: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Ejecuta operaciones sobre la memoria de viajes.
        - LIST_TRIPS: NO requiere city -> pasa solo user_id.
        - Resto: requiere city cuando aplica; si falta, intenta inferir viaje activo.
        """
        # Caso especial: LIST_TRIPS NO usa 'city'
        if intent == "LIST_TRIPS":
            return self.travel_memory_agent.list_trips(user_id)

        # Para el resto de operaciones, resolvemos city si no viene
        city_arg = args.get("city")
        if not city_arg and city_arg != "*":
            active_trips = [t for t in tlm.load_travel_log("backend", user_id).get("trips", []) if t.get("status") != "cancelled"]
            if len(active_trips) == 1:
                city_arg = active_trips[0].get("city")

        tool_map = {
            "SHIFT_TRIP": self.travel_memory_agent.shift_trip_dates,
            "EXTEND_TRIP": self.travel_memory_agent.extend_stay,
            "SHORTEN_TRIP": self.travel_memory_agent.shorten_stay,
            "DELETE_TRIP": self.travel_memory_agent.delete_trip,
        }
        handler = tool_map.get(intent)
        if not handler:
            return {"error": f"Operación de memoria no implementada: {intent}"}

        # Construir argumentos para el handler
        handler_args = [user_id, city_arg] if city_arg else [user_id]
        if intent == "SHIFT_TRIP":
            handler_args.append(int(args.get("days_shift", 0)))
        if intent == "EXTEND_TRIP":
            handler_args.append(int(args.get("days_change", 0)))
        if intent == "SHORTEN_TRIP":
            handler_args.append(abs(int(args.get("days_change", 0))))
        
        return handler(*handler_args)

    # --- ✅ FUNCIÓN DE RESUMEN MODULARIZADA ---
    def _summarize(self, user_id: str, intent: str, args: Dict[str, Any], result: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
        if "error" in result and result["error"] and intent not in ["PLAN_TRIP", "SEARCH_FLIGHTS", "SEARCH_HOTELS"]:
            return {"error": result['error']}, f"⚠️ Hubo un problema: {result['error']}"

        if intent in ["LIST_TRIPS", "SHIFT_TRIP", "EXTEND_TRIP", "SHORTEN_TRIP", "DELETE_TRIP"]:
            return {}, result.get("summary", "Operación completada.")

        # Para intenciones de búsqueda y planificación
        city = result.get("city", "Destino")
        
        # Lógica para construir el texto de respuesta
        reply_text = ""
        if intent == "SEARCH_FLIGHTS":
            reply_text = f"Aquí tienes los vuelos que encontré para **{city}**:"
        elif intent == "SEARCH_HOTELS":
            reply_text = f"Estos son los hoteles disponibles en **{city}**:"
        elif intent == "GET_DESTINATION_INFO":
            reply_text = f"Esto es lo que sé sobre **{city}**:"
        else:
            reply_text = f"Aquí tienes tu plan para **{city}**."

        # Guardar en el log de viaje solo si es un plan completo
        if intent == "PLAN_TRIP":
            trip = tlm.create_or_get_trip("backend", user_id, city, result.get("checkin"), result.get("checkout"))
            trip_id = trip["trip_id"]
            if result.get("summary") or result.get("pois") or result.get("plan_sugerido"):
                tlm.set_trip_destination_info(
                    "backend", user_id, trip_id,
                    result.get("summary", ""), result.get("pois", []), result.get("plan_sugerido", [])
                )
            if (b := result.get("budget")) is not None:
                tlm.set_trip_budget("backend", user_id, trip_id, float(b))
        
        structured_data = {
            "city": city,
            "flights": [FlightInfo(**f).model_dump() for f in result.get("flights", [])],
            "hotels": [HotelInfo(**h).model_dump() for h in result.get("hotels", [])],
            "pois": result.get("pois", []),
            "summary": result.get("summary"),
            "plan_sugerido": result.get("plan_sugerido"),
            "budget": BudgetInfo(total=result.get("budget")).model_dump() if result.get("budget") is not None else None
        }

        # Añadir notas de error si algún agente falló
        errors = [v.get("error") for k, v in result.items() if isinstance(v, dict) and "error" in v]
        if errors:
            error_note = "\n\n**Nota:** " + " y ".join(errors)
            reply_text += error_note
            structured_data["error"] = error_note

        return structured_data, reply_text
