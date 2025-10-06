from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

Role = Literal["user", "bot"]

class Message(BaseModel):
    role: Role
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z")

class Conversation(BaseModel):
    conversation_id: str
    history: List[Message] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z")
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z")

class UserIndex(BaseModel):
    user_id: str
    conversations: List[str] = Field(default_factory=list)
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z")

class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None  # si no llega, se crea

class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    context_snapshot: List[Message]
