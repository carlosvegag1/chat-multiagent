# backend/app/core/schemas.py
from typing import List, Optional, Literal, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import json
import time

# --- âœ… Modelos de Datos Enriquecidos ---

class FlightInfo(BaseModel):
    airline: Optional[str] = None
    flight_number: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    duration: Optional[str] = None
    stops: int = 0
    price: Optional[float] = None
    currency: str = "EUR"

class HotelInfo(BaseModel):
    name: Optional[str] = None
    hotelId: Optional[str] = None
    rating: Optional[int] = None
    address: Optional[str] = None # DirecciÃ³n simplificada a un string
    price_per_night: Optional[float] = None # Mantenido para el cÃ¡lculo de presupuesto
    currency: str = "EUR"

class POIInfo(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class DailyPlan(BaseModel):
    day: int
    activities: List[str] = Field(default_factory=list)

class BudgetInfo(BaseModel):
    total: Optional[float] = None
    currency: str = "EUR"

class StructuredReply(BaseModel):
    city: Optional[str] = None
    flights: Optional[List[FlightInfo]] = None
    hotels: Optional[List[HotelInfo]] = None
    pois: Optional[List[POIInfo]] = None
    summary: Optional[str] = None
    plan_sugerido: Optional[List[DailyPlan]] = None
    budget: Optional[BudgetInfo] = None
    error: Optional[str] = None

# --- Modelos de la API de Chat ---

class StructuredChatResponse(BaseModel):
    conversation_id: str
    intent: Optional[str] = None
    reply_text: str
    structured_data: Optional[StructuredReply] = None
    agents_called: List[str] = Field(default_factory=list)
    transcription: Optional[str] = None

    @field_validator("reply_text", mode="before")
    @classmethod
    def ensure_string(cls, v):
        if isinstance(v, (dict, list)):
            return json.dumps(v, ensure_ascii=False, indent=2)
        if v is None:
            return "[Sin respuesta]"
        return str(v)

# --- Modelos de Persistencia ---

Role = Literal["user", "bot"]

class Message(BaseModel):
    role: Role
    text: str
    structured_data: Optional[StructuredReply] = None
    ts: float = Field(default_factory=time.time)

class Conversation(BaseModel):
    convo_id: str
    user: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    messages: List[Message] = Field(default_factory=list)
