# app/routers/agents_test.py
from __future__ import annotations
from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any
from app.agents.flight_agent import FlightAgent
from app.agents.hotel_agent import HotelAgent
from app.agents.destination_agent import DestinationAgent
from app.agents.calc_agent import CalcAgent
from app.utils import travel_log_manager as tlm

router = APIRouter(prefix="/agents-test", tags=["agents-test"])

@router.get("/flight")
async def test_flight(origin: str = Query(...), destination: str = Query(...), date: str = Query(...), adults: int = Query(1)):
    agent = FlightAgent()
    return await agent.query(origin=origin, destination=destination, date=date, adults=adults)

@router.get("/hotel")
async def test_hotel(city: str = Query(...), checkin: str = Query(...), checkout: str = Query(...), guests: int = Query(2)):
    agent = HotelAgent()
    return await agent.query(city=city, checkin=checkin, checkout=checkout, guests=guests)

@router.get("/destination")
async def test_destination(city: str = Query(...)):
    agent = DestinationAgent()
    return await agent.query(city=city)

# 💰 Calc: permite probar MCP calc con payloads mínimos y ver fallback del orquestador si se desea
@router.get("/calc")
async def test_calc(
    flight_prices: Optional[str] = Query(None, description="Lista CSV de precios de vuelos, ej: '40.5,55,120'"),
    nights: Optional[int] = Query(None, description="Noches de hotel para simular budget local"),
    nightly_eur: Optional[float] = Query(None, description="Precio por noche para simular, por defecto .env DEFAULT_NIGHTLY_EUR")
):
    agent = CalcAgent()
    flights = []
    if flight_prices:
        for p in flight_prices.split(","):
            p = p.strip()
            if not p: continue
            flights.append({"price": p, "currency": "EUR"})
    hotels = [{"price": (nightly_eur or 110), "currency": "EUR"}] if nights else []
    result = await agent.query(flights={"flights": flights}, hotels={"hotels": hotels})
    return {"flights_input": flights, "nights": nights, "calc_result": result}

@router.get("/memory/clean")
def clean_memory(user: str = Query("Carlos")):
    try:
        summary = tlm.clean_travel_log("backend", user)
        return {"status": "ok", "message": f"Travel log de {user} limpiado correctamente.", "summary": summary}
    except Exception as e:
        return {"status": "error", "message": f"Error al limpiar travel log: {str(e)}"}
