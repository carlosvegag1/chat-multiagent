import os
from dotenv import load_dotenv

load_dotenv(override=True)

# En esta fase usaremos mocks, pero dejamos preparada la estructura real
MCP_ENDPOINTS = {
    "flight": os.getenv("MCP_FLIGHT_ENDPOINT", "mock://amadeus"),
    "hotel": os.getenv("MCP_HOTEL_ENDPOINT", "mock://hotels"),
    "weather": os.getenv("MCP_WEATHER_ENDPOINT", "mock://openweather"),
    "destination": os.getenv("MCP_DESTINATION_ENDPOINT", "mock://tripadvisor"),
}

# Claves o tokens (si existieran)
MCP_API_KEYS = {
    "amadeus": os.getenv("AMADEUS_API_KEY", "mock-key"),
    "openweather": os.getenv("OPENWEATHER_API_KEY", "mock-key"),
}
