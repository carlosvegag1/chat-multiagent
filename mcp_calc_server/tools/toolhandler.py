import os
from datetime import datetime
from typing import Any, Dict, List, Optional

DEFAULT_NIGHTLY_EUR = float(os.getenv("DEFAULT_NIGHTLY_EUR", "110"))

def _parse_price(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(str(v).replace(",", "."))
    except Exception:
        return None

def estimate_budget(
    flights: Optional[Dict[str, Any]] = None,
    hotels: Optional[Dict[str, Any]] = None,
    checkin: Optional[str] = None,
    checkout: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Calcula presupuesto estimado: vuelo más barato + noches * precio medio hotel (si no hay total).
    - flights: { "flights": [ { "price": ... }, ... ] }
    - hotels:  { "hotels":  [ { "price": ... }, ... ] }
    - checkin/checkout: YYYY-MM-DD
    """
    flights = flights.get("flights", []) if isinstance(flights, dict) else (flights or [])
    hotels  = hotels.get("hotels",  []) if isinstance(hotels,  dict) else (hotels  or [])

    # 1) Precio de vuelo mínimo
    flight_prices = [_parse_price(f.get("price")) for f in flights]
    flight_prices = [p for p in flight_prices if p is not None]
    min_flight = min(flight_prices) if flight_prices else 100.0

    # 2) Precio hotel: si vienen totales, usa media; si no, precio por noche por defecto
    hotel_prices = [_parse_price(h.get("price")) for h in hotels]
    hotel_prices = [p for p in hotel_prices if p is not None]
    nightly = (sum(hotel_prices) / len(hotel_prices)) if hotel_prices else DEFAULT_NIGHTLY_EUR

    # 3) Noches: prioriza checkin/checkout del orquestador
    nights = 3
    if checkin and checkout:
        try:
            ci = datetime.fromisoformat(checkin)
            co = datetime.fromisoformat(checkout)
            nights = max((co - ci).days, 1)
        except Exception:
            pass

    total = round(float(min_flight) + float(nightly) * int(nights), 2)

    return {
        "flights_min": float(min_flight),
        "nightly": float(nightly),
        "nights": int(nights),
        "total": float(total),
        # Para máxima compatibilidad:
        "total_eur": float(total),
        "currency": "EUR",
    }
