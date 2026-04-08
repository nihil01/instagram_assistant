import logging

import httpx
from fastapi import HTTPException

from config.app_config import settings as cfg

logger = logging.getLogger(__name__)


async def exchange_code_for_token(code: str) -> dict:
    url = "https://api.instagram.com/oauth/access_token"

    data = {
        "client_id": cfg.INSTAGRAM_APP_ID,
        "client_secret": cfg.INSTAGRAM_APP_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": cfg.redirect_uri,
        "code": code,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(url, data=data)

    if response.status_code >= 400:
        logger.error("exchange_code_for_token failed: %s", response.text)
        raise HTTPException(400, response.text)

    return response.json()


async def exchange_long_lived(short_token: str) -> dict:
    url = "https://graph.instagram.com/access_token"

    params = {
        "grant_type": "ig_exchange_token",
        "client_secret": cfg.INSTAGRAM_APP_SECRET,
        "access_token": short_token,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)

    if response.status_code >= 400:
        logger.error("exchange_long_lived failed: %s", response.text)
        raise HTTPException(400, response.text)

    return response.json()


async def get_me(token: str) -> dict:
    url = "https://graph.instagram.com/v25.0/me"

    params = {
        "fields": "user_id,username",
        "access_token": token,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)

    if response.status_code >= 400:
        logger.error("get_me failed: %s", response.text)
        raise HTTPException(400, response.text)

    return response.json()
