from app import queue
from fastapi import APIRouter

router = APIRouter()

@router.get("/get_queue")
async def list_queue():
    return {"queue": queue}