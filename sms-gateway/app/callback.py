from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from loguru import logger

app = FastAPI()

class CallbackPayload(BaseModel):
    message_uuid: str
    message_id: str
    timestamp: str
    status: str

@app.post("/callback")
async def receive_callback(payload: CallbackPayload):
    """
    Receive callback from Supabase to confirm message delivery status.
    """
    logger.info(f"Received callback for message {payload.message_id}: {payload.status}")
    return {"status": "ok"} 