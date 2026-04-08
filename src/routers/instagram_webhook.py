import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.app_config import settings
from config.deps import get_db
from services.instagram_signature import verify_signature
from services.webhooks import handle_message

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/webhook")
async def verify(hub_mode: str, hub_challenge: str, hub_verify_token: str):
    if hub_mode != "subscribe":
        raise HTTPException(status_code=400, detail="Invalid hub.mode")

    if hub_verify_token != settings.VERIFY_TOKEN:
        raise HTTPException(403)

    logger.info("Webhook verification succeeded")
    return PlainTextResponse(hub_challenge)


@router.post("/webhook")
async def webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.body()
    signature = request.headers.get("x-hub-signature-256")

    if not signature:
        logger.warning("Missing webhook signature header")
        raise HTTPException(status_code=400)

    if not verify_signature(body, signature):
        logger.warning("Webhook signature verification failed")
        raise HTTPException(403)

    payload = await request.json()

    for entry in payload.get("entry", []):
        if entry.get("is_echo") is True:
            logger.info("Skipping echo webhook entry")
            continue

        for message_event in entry.get("messaging", []):
            if "message" in message_event:
                await handle_message(message_event, db)

    return {"ok": True}
