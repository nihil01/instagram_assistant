from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from config.deps import get_db
from config.app_config import settings
from services.instagram_signature import verify_signature
from services.webhooks import handle_message

router = APIRouter()


@router.get("/webhook")
async def verify(hub_mode: str, hub_challenge: str, hub_verify_token: str):

    if hub_mode != "subscribe":
        raise HTTPException(status_code=400, detail="Invalid hub.mode")

    if hub_verify_token != settings.VERIFY_TOKEN:
        raise HTTPException(403)
    
    return PlainTextResponse(hub_challenge)


@router.post("/webhook")
async def webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.body()
    sig = request.headers.get("x-hub-signature-256")

    if not sig:
        raise HTTPException(status_code=400)

    if not verify_signature(body, sig):
        raise HTTPException(403)

    payload = await request.json()

    for entry in payload.get("entry", []):

        if entry.get("is_echo") is True:
            return

        for msg in entry.get("messaging", []):
            if "message" in msg:
                await handle_message(msg, db)

    return {"ok": True}