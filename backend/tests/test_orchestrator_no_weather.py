# tests/test_orchestrator_no_weather.py
import pytest
import asyncio
import os
from app.core.orchestrator.orchestrator import Orchestrator
from app.config.settings import settings


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    orch = Orchestrator(openai_api_key=os.getenv("OPENAI_API_KEY", "dummy-key"))
    assert orch is not None
    assert hasattr(orch, "flight_agent")
    assert hasattr(orch, "hotel_agent")
    assert hasattr(orch, "destination_agent")
    assert hasattr(orch, "calc_agent")
    assert not hasattr(orch, "weather_agent")  # WeatherAgent desactivado


@pytest.mark.asyncio
async def test_fake_flight_query(monkeypatch):
    orch = Orchestrator(openai_api_key=settings.OPENAI_API_KEY or "dummy-key")

    async def mock_flight_query(**kwargs):
        return {"flights": [{"origin": "MAD", "destination": "LIS"}]}

    orch.flight_agent.query = mock_flight_query
    result = await orch._dispatch_agent("flight_search", {"origin": "MAD", "destination": "LIS"})
    assert "flights" in result
    assert result["flights"][0]["destination"] == "LIS"


@pytest.mark.asyncio
async def test_calc_agent(monkeypatch):
    orch = Orchestrator(openai_api_key=settings.OPENAI_API_KEY or "dummy-key")

    async def mock_calc_query(**kwargs):
        return {"ok": True, "result": 42}

    orch.calc_agent.query = mock_calc_query
    result = await orch._dispatch_agent("calc_sum", {"a": 20, "b": 22})
    assert result["ok"]
    assert result["result"] == 42


@pytest.mark.asyncio
async def test_weather_disabled():
    orch = Orchestrator(openai_api_key=settings.OPENAI_API_KEY or "dummy-key")
    result = await orch._dispatch_agent("get_current_weather", {"city": "Lisbon"})
    assert "WeatherAgent desactivado" in result["summary"]
