# mcp_flight_server/tools/tools_flight.py

from pydantic import BaseModel, Field
from typing import Dict, Any, List
import requests
import os
import json
import time
from dotenv import load_dotenv

# Carga de credenciales robusta
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

AMADEUS_BASE_URL = os.getenv("AMADEUS_BASE_URL", "https://test.api.amadeus.com").strip()
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY", "").strip()
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET", "").strip()

# Modelo de entrada (sin cambios)
class FlightSearchArgs(BaseModel):
    origin: str = Field(..., description="Código IATA de la ciudad de salida (por ejemplo, MAD)")
    destination: str = Field(..., description="Código IATA de la ciudad destino (por ejemplo, LIS)")
    date: str = Field(..., description="Fecha de salida (YYYY-MM-DD)")
    adults: int = 1
    max_results: int = 5

# Autenticación (sin cambios)
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "token.json")
def _get_access_token(retries: int = 2) -> str:
    # ... (el código de autenticación no necesita cambios)
    if os.path.exists(TOKEN_PATH):
        try:
            with open(TOKEN_PATH, "r", encoding="utf-8") as f:
                token_data = json.load(f)
            expires_at = token_data.get("expires_at", 0)
            if time.time() < expires_at and "access_token" in token_data:
                print("[DEBUG] ♻️ Reutilizando token Amadeus cacheado (vuelos)")
                return token_data["access_token"]
            else:
                print("[DEBUG] ⚠️ Token expirado o inválido, generando uno nuevo...")
        except Exception as e:
            print(f"[WARN] No se pudo leer token.json: {e}")
    url = f"{AMADEUS_BASE_URL}/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = f"grant_type=client_credentials&client_id={AMADEUS_API_KEY}&client_secret={AMADEUS_API_SECRET}"
    for attempt in range(1, retries + 1):
        try:
            print(f"[DEBUG] 🔑 Intento {attempt}/{retries}: solicitando nuevo token a {url}")
            resp = requests.post(url, data=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                token_data = resp.json()
                access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 1800)
                if not access_token:
                    raise ValueError(f"Respuesta sin 'access_token': {token_data}")
                token_data["expires_at"] = time.time() + expires_in - 30
                with open(TOKEN_PATH, "w", encoding="utf-8") as f:
                    json.dump(token_data, f, indent=2)
                print(f"[DEBUG] ✅ Nuevo token Amadeus guardado (expira en {expires_in}s)")
                return access_token
            else:
                print(f"[ERROR] ❌ Error autenticando Amadeus ({resp.status_code}): {resp.text}")
                if attempt == retries:
                    raise Exception(f"Fallo tras {retries} intentos: {resp.text}")
        except requests.exceptions.Timeout:
            print(f"[WARN] ⏳ Timeout en autenticación Amadeus (intento {attempt}/{retries})")
            if attempt == retries:
                raise
        except Exception as e:
            print(f"[ERROR] ⚠️ Fallo en autenticación Amadeus: {e}")
            if attempt == retries:
                raise
    raise Exception("No se pudo obtener el token tras múltiples intentos.")

# ✅ FUNCIÓN DE BÚSQUEDA DE VUELOS ENRIQUECIDA
def search_flights(args: FlightSearchArgs) -> Dict[str, Any]:
    """Busca vuelos en Amadeus y devuelve un conjunto de datos enriquecido."""
    try:
        token = _get_access_token()
    except Exception as e:
        return {"error": f"Error autenticando con Amadeus: {e}"}

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{AMADEUS_BASE_URL}/v2/shopping/flight-offers"
    params = {
        "originLocationCode": args.origin.upper(),
        "destinationLocationCode": args.destination.upper(),
        "departureDate": args.date,
        "adults": args.adults,
        "max": args.max_results,
        "nonStop": "true", # Buscamos vuelos directos para simplificar
        "currencyCode": "EUR"
    }

    print(f"[DEBUG] ✈️ Solicitando vuelos a {url} con params={params}")
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        flights: List[Dict[str, Any]] = []
        for offer in data.get("data", []):
            itinerary = offer.get("itineraries", [{}])[0]
            if not itinerary: continue
            
            segment = itinerary.get("segments", [{}])[0]
            if not segment: continue

            # ✅ Extraemos todos los datos relevantes
            flights.append({
                "airline": segment.get("carrierCode"),
                "flight_number": segment.get("number"),
                "origin": segment.get("departure", {}).get("iataCode"),
                "destination": segment.get("arrival", {}).get("iataCode"),
                "departure_time": segment.get("departure", {}).get("at"),
                "arrival_time": segment.get("arrival", {}).get("at"),
                "duration": itinerary.get("duration"),
                "price": offer.get("price", {}).get("total"),
                "currency": offer.get("price", {}).get("currency"),
            })

        print(f"[FlightTool] Encontrados {len(flights)} vuelos de {args.origin} a {args.destination}")
        return { "flights": flights }

    except requests.exceptions.HTTPError as http_err:
        return {"error": f"Error HTTP: {http_err.response.status_code} - {http_err.response.text}"}
    except requests.exceptions.Timeout:
        return {"error": "Timeout en la solicitud a Amadeus."}
    except Exception as e:
        return {"error": f"Error procesando vuelos: {e}"}

# Registro MCP (sin cambios)
TOOLS = {
    "flight.search_flights": {
        "description": "Busca vuelos reales usando la API de Amadeus (sandbox).",
        "schema": FlightSearchArgs.model_json_schema(),
        "handler": search_flights,
        "args_cls": FlightSearchArgs
    }
}