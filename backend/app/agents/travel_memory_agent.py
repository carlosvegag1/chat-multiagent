# backend/app/agents/travel_memory_agent.py
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from app.utils.travel_log_manager import load_travel_log, save_travel_log

# ðŸ”» NOTA: La lÃ­nea que causaba el error (from app.agents.travel_memory_agent...) ha sido eliminada. ðŸ”»

def _norm(s: Optional[str]) -> str:
    return s.strip().lower() if s else ""

def _parse_dt(dt: Optional[str], fallback: Optional[datetime] = None) -> datetime:
    if not dt: return fallback or datetime.now()
    try:
        # Maneja ambos formatos, con y sin Z
        return datetime.fromisoformat(dt.replace("Z", ""))
    except Exception:
        return fallback or datetime.now()

def _iso_date_only(dt: datetime) -> str:
    return dt.date().isoformat()

class TravelMemoryAgent:
    """ðŸ§  Agente de memoria contextual de viajes (con respuestas enriquecidas)."""

    def __init__(self, data_path: str = "backend/data/v2/users"):
        self.data_path = data_path

    def _find_target_trip(self, user_id: str, city: str) -> Optional[Dict[str, Any]]:
        log = load_travel_log("backend", user_id)
        trips = [t for t in log.get("trips", []) if t.get("status") != "cancelled"]
        if not trips: return None

        city_norm = _norm(city)
        if not city_norm and len(trips) == 1:
            return trips[0]
        
        for t in trips:
            if city_norm and city_norm in _norm(t.get("city", "")):
                return t
        return None

    def list_trips(self, user_id: str) -> Dict[str, Any]:
        try:
            log = load_travel_log("backend", user_id)
            trips = [t for t in log.get("trips", []) if t.get("status") != "cancelled"]
            if not trips: return {"summary": "No tienes viajes registrados todavÃ­a."}
            
            resumen = ["AquÃ­ tienes un resumen de tus viajes:"]
            for t in sorted(trips, key=lambda x: x.get("start_date", "")):
                city = t.get("city") or "Â¿Destino?"
                start = self._fmt(t.get("start_date")) or "?"
                end = self._fmt(t.get("end_date")) or start
                budget = t.get("budget")
                budget_txt = f" con un presupuesto de ~{budget:.0f}â‚¬" if budget is not None else ""
                resumen.append(f"- **{city}**: del {start} al {end}{budget_txt}.")
            
            return {"summary": "\n".join(resumen)}
        except Exception as e:
            return {"summary": f"âš ï¸ Error al listar viajes: {e}"}

    def _modify_stay(self, user_id: str, city: str, days_change: int) -> Dict[str, Any]:
        target_trip = self._find_target_trip(user_id, city)
        if not target_trip:
            return {"summary": f"âš ï¸ No encontrÃ© un viaje a **{city or 'ese destino'}** para modificar."}

        start_date = _parse_dt(target_trip.get("start_date"))
        end_date = _parse_dt(target_trip.get("end_date") or target_trip.get("start_date"))
        new_end_date = end_date + timedelta(days=days_change)
        
        if new_end_date < start_date:
            return {"summary": f"âš ï¸ No se puede acortar el viaje a **{target_trip['city']}** mÃ¡s allÃ¡ de su fecha de inicio."}

        target_trip["end_date"] = _iso_date_only(new_end_date)
        
        log_data = load_travel_log("backend", user_id)
        log_data["trips"] = [target_trip if t.get("trip_id") == target_trip.get("trip_id") else t for t in log_data.get("trips", [])]
        save_travel_log("backend", user_id, log_data)

        new_duration = (new_end_date - start_date).days
        action_word = "extendido" if days_change > 0 else "acortado"
        
        summary = f"âœ… Viaje a **{target_trip['city']}** {action_word}. Ahora dura **{new_duration} dÃ­as**, del {self._fmt(_iso_date_only(start_date))} al {self._fmt(_iso_date_only(new_end_date))}."
        return {"summary": summary, "updated_trip": target_trip}

    def extend_stay(self, user_id: str, city: str, extra_days: int) -> Dict[str, Any]:
        return self._modify_stay(user_id, city, abs(extra_days))

    def shorten_stay(self, user_id: str, city: str, days_to_remove: int) -> Dict[str, Any]:
        return self._modify_stay(user_id, city, -abs(days_to_remove))

    def shift_trip_dates(self, user_id: str, city: str, days_shift: int) -> Dict[str, Any]:
        target_trip = self._find_target_trip(user_id, city)
        if not target_trip: return {"summary": f"âš ï¸ No encontrÃ© un viaje a **{city or 'ese destino'}**."}
        
        new_dates = {}
        for key in ["start_date", "end_date"]:
            if date_str := target_trip.get(key):
                dt = _parse_dt(date_str) + timedelta(days=days_shift)
                new_date_iso = _iso_date_only(dt)
                target_trip[key] = new_date_iso
                new_dates[key] = new_date_iso

        log_data = load_travel_log("backend", user_id)
        log_data["trips"] = [target_trip if t.get("trip_id") == target_trip.get("trip_id") else t for t in log_data.get("trips", [])]
        save_travel_log("backend", user_id, log_data)
        
        summary = f"âœ… Fechas del viaje a **{target_trip['city']}** desplazadas. Nuevas fechas: del {self._fmt(new_dates.get('start_date'))} al {self._fmt(new_dates.get('end_date'))}."
        return {"summary": summary, "updated_trip": target_trip}

    def delete_trip(self, user_id: str, city: str) -> Dict[str, Any]:
        log_data = load_travel_log("backend", user_id)
        trips = log_data.get("trips", [])
        city_norm = _norm(city)

        if not city_norm or city_norm in {"todos", "todo", "all", "*"}:
            if not trips: return {"summary": "No tienes viajes registrados."}
            log_data["trips"] = []
            save_travel_log("backend", user_id, log_data)
            return {"summary": "ðŸ§¹ Todos tus viajes han sido eliminados."}
        
        original_count = len(trips)
        new_trips = [t for t in trips if city_norm not in _norm(t.get("city", ""))]
        
        if len(new_trips) == original_count: return {"summary": f"âš ï¸ No encontrÃ© un viaje a **{city}** para eliminar."}
        
        log_data["trips"] = new_trips
        save_travel_log("backend", user_id, log_data)
        return {"summary": f"ðŸ—‘ï¸ Viaje a **{city}** eliminado correctamente."}

    @staticmethod
    def _fmt(s: str) -> str:
        try:
            return datetime.fromisoformat(s).strftime("%d/%m/%Y")
        except:
            return s or "?"

