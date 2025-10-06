import asyncio
from fastapi import APIRouter
from app.agents.flight_agent import FlightAgent
from app.agents.hotel_agent import HotelAgent
from app.agents.weather_agent import WeatherAgent
from app.agents.destination_agent import DestinationAgent
from app.agents.calc_agent import CalcAgent
from app.config.settings import MCP_ENDPOINTS

router = APIRouter(prefix="/v2/agents", tags=["agents"])

@router.get("/health")
def agents_health():
    return {"status": "ok", "agents": list(MCP_ENDPOINTS.keys())}

@router.get("/mock_all")
async def mock_all(destino: str = "Londres", fechas: str = "10-15 diciembre", presupuesto: int = 800):
    payload = {"destino": destino, "fechas": fechas, "presupuesto": presupuesto}

    # Crear instancias
    flight = FlightAgent("flight", MCP_ENDPOINTS["flight"])
    hotel = HotelAgent("hotel", MCP_ENDPOINTS["hotel"])
    weather = WeatherAgent("weather", MCP_ENDPOINTS["weather"])
    dest = DestinationAgent("destination", MCP_ENDPOINTS["destination"])
    calc = CalcAgent("calc", "mock://calc")

    # Ejecutar en paralelo
    results = await asyncio.gather(
        flight.query(payload),
        hotel.query(payload),
        weather.query(payload),
        dest.query(payload),
        calc.query(payload),
    )

    return {"results": results}
