import logging

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.deps import get_db
from services.company import upsert_company
from services.instagram_oauth import exchange_code_for_token, exchange_long_lived, get_me

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/auth/callback")
async def callback(code: str = Query(...), db: AsyncSession = Depends(get_db)):
    api_token = await exchange_code_for_token(code)
    long_lived = await exchange_long_lived(api_token["access_token"])
    profile = await get_me(long_lived["access_token"])

    await upsert_company(
        db,
        instagram_account_id=str(profile["user_id"]),
        username=profile.get("username"),
        name=profile.get("name"),
        token=long_lived["access_token"],
        expires_in=long_lived["expires_in"],
    )

    logger.info("OAuth callback completed for instagram_account_id=%s", profile["user_id"])
    return {"status": "ok"}


@router.post("/deauthorize")
async def deauthorize(request: Request, db: AsyncSession = Depends(get_db)):
    logger.info("Received deauthorize request")
    return {"status": "ok"}


@router.post("/delete_data")
async def delete_data(request: Request, db: AsyncSession = Depends(get_db)):
    logger.info("Received delete_data request")
    return {"status": "ok"}
