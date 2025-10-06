from fastapi import APIRouter
from app.core.orchestrator.orchestrator import Orchestrator
import os, asyncio

router = APIRouter(prefix="/v2/orchestrator", tags=["orchestrator"])

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

@router.post("/run")
async def orchestrate(user_id: str = "carlos", conversation_id: str = "demo1", message: str = "Planea un viaje a Londres con 800 euros"):
    orchestrator = Orchestrator(openai_api_key=OPENAI_KEY)
    result = await orchestrator.handle(user_id, conversation_id, message)
    return result
