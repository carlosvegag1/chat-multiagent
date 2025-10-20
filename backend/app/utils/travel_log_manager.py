# backend/app/utils/travel_log_manager.py
from __future__ import annotations
import json, os, re, unicodedata
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from app.utils.structured_logger import log

ISO_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"

# --- NORMALIZACIÃ“N CIUDAD/IATA (CACHÃ‰ DINÃMICA) ---
IATA_TO_CITY = {
    "MAD": "Madrid", "BCN": "Barcelona", "PAR": "ParÃ­s", "LON": "Londres",
    "ROM": "Roma", "NYC": "Nueva York", "TYO": "Tokio"
}

CITY_ALIASES = {
    "madrid": ("Madrid", "MAD"), "barcelona": ("Barcelona", "BCN"),
    "paris": ("ParÃ­s", "PAR"), "parÃ­s": ("ParÃ­s", "PAR"),
    "londres": ("Londres", "LON"), "london": ("Londres", "LON"),
    "roma": ("Roma", "ROM"), "rome": ("Roma", "ROM"),
    "nueva york": ("Nueva York", "NYC"), "new york": ("Nueva York", "NYC"),
    "tokio": ("Tokio", "TYO"), "tokyo": ("Tokio", "TYO")
}

def _strip_accents(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def add_city_to_cache(city_name: str, iata_code: str):
    """
    AÃ±ade una nueva correspondencia ciudad-IATA a la cachÃ© en memoria para futuras consultas.
    """
    if not city_name or not iata_code or len(iata_code) != 3:
        return

    city_clean = city_name.strip()
    iata_upper = iata_code.strip().upper()
    alias_key = _strip_accents(city_clean).lower()

    if alias_key not in CITY_ALIASES:
        CITY_ALIASES[alias_key] = (city_clean, iata_upper)
        IATA_TO_CITY[iata_upper] = city_clean
        log.info(f"CachÃ© de ciudades actualizada: '{city_clean}' -> '{iata_upper}'", extra={"summary": "CACHE_UPDATE"})

def normalize_city(query: Optional[str]) -> Tuple[str, Optional[str]]:
    """
    Busca en la cachÃ© local el nombre canÃ³nico y el IATA de una ciudad.
    Si no lo encuentra, devuelve el nombre capitalizado y None como IATA.
    """
    if not query:
        return ("", None)

    q_raw = str(query).strip()
    q = _strip_accents(q_raw).lower()
    q_upper = q_raw.strip().upper()

    if q_upper in IATA_TO_CITY:
        return (IATA_TO_CITY[q_upper], q_upper)

    if q in CITY_ALIASES:
        return CITY_ALIASES[q]
        
    for alias, (city, iata) in CITY_ALIASES.items():
        if alias in q:
            return (city, iata)

    return (q_raw.strip().title(), None)

# ------------------ IO helpers ------------------

def _user_dir(base: str, user: str) -> str:
    # CorrecciÃ³n para asegurar que la ruta base 'backend' no se duplique
    if os.path.basename(base) == 'backend':
        return os.path.join(os.path.dirname(base), "data", "v2", "users", user)
    return os.path.join(base, "data", "v2", "users", user)

def _travel_log_path(base: str, user: str) -> str:
    return os.path.join(_user_dir(base, user), "travel_log.json")

def _ensure_user_dir(base: str, user: str) -> None:
    os.makedirs(_user_dir(base, user), exist_ok=True)

def _now_iso() -> str:
    return datetime.utcnow().strftime(ISO_FMT)

def _slugify(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9\-_. ]+", "", text).strip().lower()
    text = re.sub(r"\s+", "-", text)
    return text[:60] if text else "trip"

def load_travel_log(base: str, user: str) -> Dict[str, Any]:
    path = _travel_log_path(base, user)
    if not os.path.exists(path):
        _ensure_user_dir(base, user)
        base_data = {"user_id": user, "created_at": datetime.utcnow().isoformat(), "trips": []}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(base_data, f, ensure_ascii=False, indent=2)
        return base_data
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_travel_log(base: str, user: str, data: Dict[str, Any]) -> None:
    _ensure_user_dir(base, user)
    path = _travel_log_path(base, user)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ------------------ Fechas ------------------

def _parse_date(s: Optional[str]) -> Optional[date]:
    if not s: return None
    try:
        return datetime.fromisoformat(s.replace("Z", "")).date()
    except Exception:
        return None

def _segment_dates(seg: Dict[str, Any]) -> Tuple[Optional[date], Optional[date]]:
    if "checkin" in seg or "checkout" in seg:
        return _parse_date(seg.get("checkin")), _parse_date(seg.get("checkout"))
    if "date" in seg:
        d = _parse_date(seg.get("date"))
        return d, d
    return None, None

def _compute_trip_range_from_segments(segments: List[Dict[str, Any]]) -> Tuple[Optional[str], Optional[str]]:
    starts, ends = [], []
    for s in segments:
        d1, d2 = _segment_dates(s)
        if d1: starts.append(d1)
        if d2: ends.append(d2)
    if not starts and not ends: return None, None
    start = min(starts) if starts else None
    end = max(ends) if ends else start
    return (start.isoformat() if start else None, end.isoformat() if end else None)

# ------------------ API de viajes ------------------

def auto_title(dest_or_hint: str, start_date: Optional[str], end_date: Optional[str]) -> str:
    if start_date and end_date:
        return f"{dest_or_hint.title()} ({start_date} â†’ {end_date})"
    if start_date:
        return f"{dest_or_hint.title()} ({start_date})"
    return dest_or_hint.title()

def list_trips(base: str, user: str) -> List[Dict[str, Any]]:
    return load_travel_log(base, user).get("trips", [])

# ------------------ LIMPIEZA ------------------

def clean_travel_log(base: str, user: str, drop_empty: bool = True, full_reset: bool = False) -> Dict[str, Any]:
    path = _travel_log_path(base, user)
    _ensure_user_dir(base, user)
    if full_reset:
        new_data = {"user_id": user, "created_at": datetime.utcnow().isoformat(), "trips": []}
        with open(path, "w", encoding="utf-8") as f: json.dump(new_data, f, ensure_ascii=False, indent=2)
        print(f"[CleanTravelLog] Todos los viajes de '{user}' han sido eliminados (modo total).")
        return {"status": "ok", "message": f"ðŸ§¹ Todos los viajes de {user} han sido eliminados.", "summary": {"removed": "ALL"}}

    data = load_travel_log(base, user)
    trips = data.get("trips", [])
    if not trips: return {"trips": [], "summary": {"removed": 0, "duplicates": 0, "fixed": 0, "total": 0}}

    cleaned, seen = [], {}
    removed, duplicates, fixed = 0, 0, 0
    for t in trips:
        segs = t.get("segments", [])
        if drop_empty and not segs: removed += 1; continue
        city_h, iata = normalize_city(t.get("city") or t.get("title", ""))
        t["city"] = city_h
        if iata: t["iata"] = iata
        s, e = _compute_trip_range_from_segments(segs)
        if s: t["start_date"] = s
        if e: t["end_date"] = e
        if s or e: fixed += 1
        key = city_h.lower().strip()
        if key in seen: seen[key]["segments"].extend(t.get("segments", [])); duplicates += 1; continue
        seen[key] = t
    for city, trip in seen.items():
        s, e = _compute_trip_range_from_segments(trip.get("segments", []))
        trip["start_date"] = s or trip.get("start_date")
        trip["end_date"] = e or trip.get("end_date") or trip["start_date"]
        trip["title"] = auto_title(trip["city"], trip["start_date"], trip["end_date"])
        trip.setdefault("trip_id", f"{(trip.get('start_date') or '00000000').replace('-', '')}_{_slugify(trip['city'])}")
        trip.setdefault("status", "planned")
        cleaned.append(trip)
    data["trips"] = cleaned
    save_travel_log(base, user, data)
    summary = {"removed": removed, "duplicates": duplicates, "fixed": fixed, "total": len(cleaned)}
    print(f"[CleanTravelLog] {user}: removed={removed}, duplicates={duplicates}, fixed={fixed}, total={len(cleaned)}")
    return {"status": "ok", "message": f"Limpieza ejecutada para {user}.", "summary": summary}

# ------------------ CREACIÃ“N / REUSO DE VIAJES ------------------

def create_or_get_trip(base: str, user: str, title_hint: str, start_date: Optional[str], end_date: Optional[str]) -> Dict[str, Any]:
    data = load_travel_log(base, user)
    trips = data.get("trips", [])
    city_h, iata = normalize_city(title_hint)
    for t in trips:
        c2, _ = normalize_city(t.get("city") or "")
        if c2.lower() == city_h.lower():
            if start_date and not t.get("start_date"): t["start_date"] = start_date
            if end_date and not t.get("end_date"): t["end_date"] = end_date
            if iata and not t.get("iata"): t["iata"] = iata
            save_travel_log(base, user, data)
            return t
    slug = _slugify(city_h)
    trip_id = f"{(start_date or datetime.utcnow().strftime('%Y-%m-%d')).replace('-', '')}_{slug}"
    trip = {
        "trip_id": trip_id, "created_at": _now_iso(), "title": auto_title(city_h, start_date, end_date),
        "city": city_h, "iata": iata, "segments": [], "status": "planned", "notes": "", "agents_called": [],
        "start_date": start_date, "end_date": end_date or start_date,
    }
    data.setdefault("trips", []).append(trip)
    save_travel_log(base, user, data)
    return trip

# ------------------ GESTIÃ“N DE SEGMENTOS Y DATOS ------------------

def add_segment(base: str, user: str, trip_id: str, segment: Dict[str, Any], agent_name: Optional[str] = None) -> Dict[str, Any]:
    data = load_travel_log(base, user)
    trips = data.get("trips", [])
    target = None
    for t in trips:
        if t.get("trip_id") == trip_id: target = t; break
    if not target: raise ValueError(f"Trip not found: {trip_id}")
    for existing in target.get("segments", []):
        if existing.get("type") == segment.get("type"):
            if existing.get("date") == segment.get("date") or \
               (existing.get("checkin") == segment.get("checkin") and existing.get("checkout") == segment.get("checkout")):
                print(f"[add_segment] Segmento duplicado ignorado ({segment.get('type')})")
                return target
    target.setdefault("segments", []).append(segment)
    if agent_name: target.setdefault("agents_called", []).append(agent_name)
    s, e = _compute_trip_range_from_segments(target["segments"])
    if s: target["start_date"] = s
    if e: target["end_date"] = e
    target["title"] = auto_title(target["city"], target.get("start_date"), target.get("end_date"))
    save_travel_log(base, user, data)
    return target

def set_trip_budget(base: str, user: str, trip_id: str, budget_value: float) -> Dict[str, Any]:
    data = load_travel_log(base, user)
    trips = data.get("trips", [])
    updated = None
    for t in trips:
        if t.get("trip_id") == trip_id:
            t["budget"] = budget_value; t["budget_updated_at"] = _now_iso(); updated = t; break
    if updated: save_travel_log(base, user, data); print(f"[TravelLog] Presupuesto actualizado para {trip_id}: {budget_value} EUR"); return updated
    else: print(f"[TravelLog] No se encontrÃ³ el viaje {trip_id} para asignar presupuesto."); return {}

def set_trip_destination_info(base: str, user: str, trip_id: str, summary: str, pois: list, plan_sugerido: list) -> Dict[str, Any]:
    data = load_travel_log(base, user)
    trips = data.get("trips", [])
    updated = None
    for t in trips:
        if t.get("trip_id") == trip_id:
            t["destination_summary"] = summary
            t["destination_pois"] = pois
            t["destination_plan_sugerido"] = plan_sugerido
            t["destination_updated_at"] = _now_iso()
            updated = t
            break
    if updated:
        save_travel_log(base, user, data)
        log.info(f"Info de destino guardada para {trip_id} ({len(pois)} POIs).", extra={"summary": "LOG_DEST_SAVE"})
        return updated
    else:
        log.warning(f"No se encontrÃ³ el viaje {trip_id} para guardar destino.", extra={"summary": "LOG_DEST_FAIL"})
        return {}
