# mcp_hotel_server/tools/toolhandler.py
from pydantic import BaseModel, Field
from typing import Dict, Any, List
import os, requests, json, time
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

AMADEUS_BASE_URL = os.getenv("AMADEUS_BASE_URL", "https://test.api.amadeus.com").strip()
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY", "").strip()
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET", "").strip()

# --- ✅ Modelo de Argumentos Actualizado ---
class HotelSearchArgs(BaseModel):
    city: str = Field(..., description="Código IATA de la ciudad")
    checkin: str = Field(..., description="YYYY-MM-DD")
    checkout: str = Field(..., description="YYYY-MM-DD")
    adults: int = Field(1, description="Número de huéspedes adultos")
    rooms: int = 1
    max_results: int = 5

TOKEN_PATH = os.path.join(os.path.dirname(__file__), "token.json")


def _get_access_token(retries: int = 2) -> str:
    # (sin cambios)
    url = f"{AMADEUS_BASE_URL}/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = f"grant_type=client_credentials&client_id={AMADEUS_API_KEY}&client_secret={AMADEUS_API_SECRET}"

    if os.path.exists(TOKEN_PATH):
        try:
            with open(TOKEN_PATH, "r", encoding="utf-8") as f:
                token_data = json.load(f)
            if time.time() < token_data.get("expires_at", 0) and "access_token" in token_data:
                print("[DEBUG] ♻️ Reutilizando token Amadeus cacheado (hoteles)")
                return token_data["access_token"]
        except Exception:
            pass

    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(url, data=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                token_data = resp.json()
                token_data["expires_at"] = time.time() + token_data.get("expires_in", 1800) - 10
                with open(TOKEN_PATH, "w", encoding="utf-8") as f:
                    json.dump(token_data, f, indent=2)
                print("[DEBUG] ✅ Token Amadeus (hoteles) OK")
                return token_data["access_token"]
            else:
                print(f"[ERROR] Auth Amadeus hoteles {resp.status_code}: {resp.text}")
                if attempt == retries:
                    raise Exception(resp.text)
        except Exception as e:
            if attempt == retries:
                raise
    raise Exception("No se pudo obtener token Amadeus (hoteles).")


# --- Lógica de Búsqueda Enriquecida ---
def search_hotels(args: HotelSearchArgs) -> Dict[str, Any]:
    city_code = args.city.upper()
    if len(city_code) != 3 or not city_code.isalpha():
        print(f"[HotelTool] Código de ciudad inválido: '{args.city}'. Se espera un IATA de 3 letras.")
        return {"hotels": [], "error": f"Código de ciudad inválido: '{args.city}'"}

    try:
        token = _get_access_token()
    except Exception as e:
        return {"hotels": [], "error": f"Error autenticando con Amadeus: {e}"}

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{AMADEUS_BASE_URL}/v1/reference-data/locations/hotels/by-city"
    
    # ✅ Nota: El parámetro 'adults' se recibe pero este endpoint no lo usa.
    # La estructura ya está lista para un endpoint más avanzado como /v3/shopping/hotel-offers
    params = {"cityCode": city_code, "radius": 20, "radiusUnit": "KM"}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        hotels_raw = data.get("data", [])
        
        hotels: List[Dict[str, Any]] = []
        for h in hotels_raw[: args.max_results]:
            address_parts = [
                h.get("address", {}).get("lines", [""])[0],
                h.get("address", {}).get("cityName"),
                h.get("address", {}).get("postalCode")
            ]
            full_address = ", ".join(filter(None, address_parts))
            
            hotels.append({
                "name": h.get("name", "Hotel sin nombre"),
                "hotelId": h.get("hotelId"),
                "rating": h.get("rating"),
                "address": full_address,
            })
        
        print(f"[HotelTool] Encontrados {len(hotels)} hoteles en {city_code} (parámetro 'adults'={args.adults} recibido)")
        return {"hotels": hotels}
    except requests.exceptions.HTTPError as http_err:
        print(f"[HotelTool] Error de API para {city_code}: {http_err.response.status_code}.")
        return {"hotels": [], "error": f"API de Hoteles respondió con error: {http_err.response.status_code}"}
    except Exception as e:
        return {"hotels": [], "error": f"Error obteniendo hoteles: {e}"}

# --- REGISTRO Y DISPATCHER ---
def list_tools():
    return [{"name": "hotel.search_hotels", "description": "Busca hoteles por ciudad para un número de huéspedes.", "parameters": HotelSearchArgs.schema()}]

def call_tool(name: str, args: dict):
    if name == "hotel.search_hotels":
        try:
            parsed_args = HotelSearchArgs(**args)
            return search_hotels(parsed_args)
        except Exception as e:
            return {"hotels": [], "error": f"Argumentos inválidos: {e}"}
    return {"error": f"Herramienta desconocida: {name}"}