import httpx
from fastapi import HTTPException
from config.app_config import settings as cfg


async def exchange_code_for_token(code: str) -> dict:
    url = "https://api.instagram.com/oauth/access_token"

    data = {
        "client_id": cfg.INSTAGRAM_APP_ID,
        "client_secret": cfg.INSTAGRAM_APP_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": cfg.redirect_uri,
        "code": code,
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(url, data=data)

    if r.status_code >= 400:
        raise HTTPException(400, r.text)

    return r.json()


# #говно
async def exchange_long_lived(short_token: str) -> dict:
    url = "https://graph.instagram.com/access_token"

    params = {
        "grant_type": "ig_exchange_token",
        "client_secret": cfg.INSTAGRAM_APP_SECRET,
        "access_token": short_token,
    }

    print(params)

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)

    print(r.json())

    if r.status_code >= 400:
        raise HTTPException(400, r.text)

    return r.json()


async def get_me(token: str) -> dict:
    url = "https://graph.instagram.com/v25.0/me"

    params = {
        "fields": "user_id,username",
        "access_token": token,
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)

    if r.status_code >= 400:
        raise HTTPException(400, r.text)

    return r.json()