import json, os, re, hashlib
from datetime import datetime
from typing import Dict, Any
from openai import AsyncOpenAI
from app.utils.structured_logger import log

class NormalizerAgent:
    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini", cache_path: str = "backend/data/v2/users"):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.model = model
        self.cache_path = cache_path
        log.info("NormalizerAgent (v2.0 - Modular Intents) inicializado.", extra={"summary": "INIT_OK", "tool": "NormalizerAgent"})

    def _get_cache_path(self, user_id: str) -> str:
        user_dir = os.path.join(self.cache_path, user_id)
        os.makedirs(user_dir, exist_ok=True)
        return os.path.join(user_dir, "intent_cache.json")

    def _load_cache(self, user_id: str) -> Dict[str, Any]:
        path = self._get_cache_path(user_id)
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return {}

    def _save_cache(self, user_id: str, cache_data: Dict[str, Any]):
        with open(self._get_cache_path(user_id), "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

    def _extract_json_from_response(self, text: str) -> str:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return match.group(0)
        raise ValueError("No se encontró un bloque JSON en la respuesta del LLM.")

    # --- ✅ PROMPT V2 - MODULAR Y PARAMETRIZADO ---
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        context_str = f"Contexto de la conversación actual: {json.dumps(context)}" if context else ""

        return f"""
Eres un motor NLU V2 para un asistente de viajes modular. Tu misión es detectar la intención del usuario y extraer las entidades relevantes. Hoy es {today}. {context_str}

## Intenciones y Entidades Disponibles

- **Intenciones Principales**:
  - `PLAN_TRIP`: Petición genérica para planificar un viaje completo.
  - `SEARCH_FLIGHTS`: Petición específica para buscar SOLO vuelos.
  - `SEARCH_HOTELS`: Petición específica para buscar SOLO hoteles.
  - `GET_DESTINATION_INFO`: Petición específica para obtener SOLO información de un lugar (resumen, POIs).

- **Intenciones Secundarias**: `LIST_TRIPS`, `SHIFT_TRIP`, `EXTEND_TRIP`, `SHORTEN_TRIP`, `DELETE_TRIP`, `UNKNOWN`.

- **Entidades**:
  - `city` (str): El destino del viaje.
  - `days` (int): La duración total del viaje.
  - `adults` (int): El número de personas que viajan.
  - `days_shift` (int): Desplazamiento relativo de fechas.
  - `days_change` (int): Cambio relativo de duración.

## Reglas Críticas Inquebrantables
1. **JSON, Y SOLO JSON**: Tu respuesta DEBE ser únicamente un objeto JSON válido.
2. **Prioridad a la Especificidad**: Si el usuario pide explícitamente "vuelos" u "hoteles", usa `SEARCH_FLIGHTS` o `SEARCH_HOTELS`. Usa `PLAN_TRIP` solo para peticiones genéricas como "un viaje a...".
3. **IGNORA ENTIDADES DESCONOCIDAS**: Si el usuario menciona detalles que no son entidades disponibles (presupuesto, tipo de hotel...), ignóralos.
4. **Uso del Contexto**: Si no se menciona ciudad y existe `last_city` en el contexto, úsala.

## Manual de Operaciones V2
### Caso 1: Peticiones Modulares
- User: "busca vuelos a Gran Canaria para 4 personas" -> {{"intent":"SEARCH_FLIGHTS","entities":{{"city":"Gran Canaria","adults":4}}}}
- User: "qué hoteles hay en Oporto para una pareja?" -> {{"intent":"SEARCH_HOTELS","entities":{{"city":"Oporto","adults":2}}}}
- User: "dame info sobre Tokio" -> {{"intent":"GET_DESTINATION_INFO","entities":{{"city":"Tokio"}}}}
- User: "vuelos y hoteles para ir a Roma 3 días" -> {{"intent":"PLAN_TRIP","entities":{{"city":"Roma","days":3}}}}

### Caso 2: Peticiones Genéricas
- User: "un viaje a Kioto de 5 días" -> {{"intent":"PLAN_TRIP","entities":{{"city":"Kioto","days":5,"adults":1}}}}
- User: "prepara una escapada a la Toscana" -> {{"intent":"PLAN_TRIP","entities":{{"city":"Toscana","adults":1}}}}

### Caso 3: Uso del Contexto
- User: "y para 3 personas?" | Context: {{"last_city": "Roma"}} -> {{"intent":"PLAN_TRIP","entities":{{"city":"Roma", "adults":3}}}}
- User: "y si solo quiero ver hoteles?" | Context: {{"last_city": "Roma"}} -> {{"intent":"SEARCH_HOTELS","entities":{{"city":"Roma"}}}}
"""

    async def normalize(self, user_id: str, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza una entrada a {intent, entities} con caché versionada.
        Si el cache hit trae UNKNOWN, se recalcula y se sobrescribe.
        """
        # --- Construye el prompt y una semilla de versión para invalidar caché vieja ---
        system_prompt = self._build_system_prompt(context)
        version_seed = hashlib.sha256(system_prompt.encode()).hexdigest()[:8]

        # --- Clave de caché: mensaje + contexto + versión del prompt ---
        context_key = json.dumps(context, sort_keys=True)
        cache_key_source = f"{message}||{context_key}||{version_seed}"
        msg_hash = hashlib.sha256(cache_key_source.encode()).hexdigest()

        cache = self._load_cache(user_id)

        # Si hay cache y NO es UNKNOWN, devuélvelo; si es UNKNOWN, forzamos recomputación
        cached = cache.get(msg_hash)
        if cached and cached.get("intent") != "UNKNOWN":
            log.info("Cache HIT.", extra={"intent": "CACHE_HIT", "tool": "NormalizerAgent"})
            return cached
        elif cached:
            log.info("Cache HIT (UNKNOWN) → Recomputando.", extra={"intent": "CACHE_HIT_RECOMPUTE", "tool": "NormalizerAgent"})

        # --- Llamada al LLM ---
        log.info("Cache MISS. Llamando a LLM.", extra={"intent": "LLM_CALL", "tool": "NormalizerAgent"})
        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": message}],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            response_text = completion.choices[0].message.content

            json_str = self._extract_json_from_response(response_text)
            normalized_data: Dict[str, Any] = json.loads(json_str)

            if "intent" not in normalized_data or "entities" not in normalized_data:
                raise ValueError("JSON sin estructura esperada.")

            # Valor por defecto de adults si aplica
            if normalized_data.get("intent") in ["PLAN_TRIP", "SEARCH_FLIGHTS", "SEARCH_HOTELS"]:
                normalized_data.setdefault("entities", {})
                normalized_data["entities"].setdefault("adults", 1)

            # --- Paracaídas heurístico si sigue UNKNOWN ---
            if normalized_data.get("intent") == "UNKNOWN":
                txt = message.lower()

                if any(w in txt for w in ["vuelo", "vuelos"]):
                    normalized_data["intent"] = "SEARCH_FLIGHTS"
                elif any(w in txt for w in ["hotel", "hoteles"]):
                    normalized_data["intent"] = "SEARCH_HOTELS"
                elif any(w in txt for w in ["info", "información", "qué ver", "que ver"]):
                    normalized_data["intent"] = "GET_DESTINATION_INFO"
                elif any(w in txt for w in ["viaje", "plan", "escapada", "itinerario"]):
                    normalized_data["intent"] = "PLAN_TRIP"

                entities = normalized_data.setdefault("entities", {})

                m = re.search(r"(\d+)\s*(personas|adultos?)", txt)
                if m:
                    entities["adults"] = int(m.group(1))
                else:
                    entities.setdefault("adults", 1)

                m = re.search(r"\ba\s+([a-záéíóúüñ\s]+?)(?=\s+(?:para|de)\b|$)", txt)
                if m:
                    city_guess = m.group(1).strip().title()
                    city_guess = re.sub(r"\s+", " ", city_guess)
                    entities["city"] = city_guess

            # Guarda en caché y devuelve
            cache[msg_hash] = normalized_data
            self._save_cache(user_id, cache)
            return normalized_data

        except Exception as e:
            log.error(
                f"Error en Normalizer: {e}. Respuesta del LLM: '{locals().get('response_text', 'N/A')}'",
                exc_info=False,
                extra={"tool": "NormalizerAgent", "summary": "LLM_PARSE_FAIL"},
            )
            return {"intent": "UNKNOWN", "entities": {"error": str(e)}}
