from typing import Dict, Any, List, Optional
from datetime import datetime

DEFAULT_NIGHTLY_EUR = float(110.0)  # Coste por defecto por noche

class CalcAgent:
    """
    Agente responsable de consolidar los costes de vuelos y hoteles
    y devolver un presupuesto total normalizado.
    """

    def _parse_price(self, price_val: Any) -> Optional[float]:
        """Convierte un valor de precio a float, manejando strings y comas."""
        if price_val is None or str(price_val).strip().lower() in ["", "n/a"]:
            return None
        try:
            return float(str(price_val).replace(",", "."))
        except (ValueError, TypeError):
            return None

    def _get_min_flight_price(self, flights: List[Dict[str, Any]]) -> float:
        """Encuentra el precio mÃ­nimo de una lista de vuelos."""
        min_price = float('inf')
        found = False
        for f in flights:
            price = self._parse_price(f.get("price"))
            if price is not None and price < min_price:
                min_price = price
                found = True
        return min_price if found else 0.0

    def _estimate_hotel_cost(self, hotels: List[Dict[str, Any]], checkin: Optional[str], checkout: Optional[str]) -> float:
        """Estima el coste total del hotel."""
        # OpciÃ³n 1: Si los hoteles ya traen un precio total, usar el mÃ¡s barato
        min_hotel_price = float('inf')
        found_price = False
        for h in hotels:
            price = self._parse_price(h.get("price"))
            if price is not None and price < min_hotel_price:
                min_hotel_price = price
                found_price = True

        if found_price:
            return min_hotel_price

        # OpciÃ³n 2: Si no hay precios, estimar por nÃºmero de noches
        if checkin and checkout:
            try:
                d1 = datetime.fromisoformat(checkin)
                d2 = datetime.fromisoformat(checkout)
                nights = max(0, (d2.date() - d1.date()).days)
                return nights * DEFAULT_NIGHTLY_EUR
            except (ValueError, TypeError):
                pass

        # Fallback si no hay fechas ni precios
        return DEFAULT_NIGHTLY_EUR * 3  # Asumimos 3 noches por defecto

    async def query(
        self,
        flights: Dict[str, Any],
        hotels: Dict[str, Any],
        checkin: Optional[str] = None,
        checkout: Optional[str] = None,
        adults: Optional[int] = None,
        **kwargs: Any,  # <-- ignora parÃ¡metros futuros sin romper
    ) -> Dict[str, Any]:
        """
        Calcula el presupuesto total estimado.
        Se basa en el vuelo mÃ¡s barato y el coste total de hotel.
        'adults' es aceptado por compatibilidad pero no altera el cÃ¡lculo.
        """
        try:
            flight_list = flights.get("flights", []) if isinstance(flights, dict) else (flights or [])
            hotel_list = hotels.get("hotels", []) if isinstance(hotels, dict) else (hotels or [])

            # Calcular coste de vuelos (el mÃ¡s barato)
            flight_cost = self._get_min_flight_price(flight_list)

            # Calcular coste de hotel
            hotel_cost = self._estimate_hotel_cost(hotel_list, checkin, checkout)

            total = round(flight_cost + hotel_cost, 2)

            return {
                "total_eur": total,
                "currency": "EUR",
                "breakdown": {
                    "flights_eur": round(flight_cost, 2),
                    "hotels_eur": round(hotel_cost, 2),
                },
                "calculation_method": "min_flight + estimated_hotel",
            }
        except Exception as e:
            print(f"[CalcAgent] Error en query(): {e}")
            return {"total_eur": "N/A", "error": str(e)}

