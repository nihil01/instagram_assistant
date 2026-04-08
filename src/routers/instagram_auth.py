from fastapi import APIRouter, HTTPException, Query, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from config.deps import get_db
from services.instagram_oauth import (
    exchange_code_for_token,
    exchange_long_lived,
    get_me,
)
from services.company import upsert_company

router = APIRouter()


@router.get("/auth/callback")
async def callback(code: str = Query(...), db: AsyncSession = Depends(get_db)):
    api_token = await exchange_code_for_token(code)
    long = await exchange_long_lived(api_token["access_token"])

    profile = await get_me(long["access_token"])

    token=long["access_token"]
    expires_in=long["expires_in"]

    await upsert_company(
        db,
        instagram_account_id=str(profile["user_id"]),
        username=profile.get("username"),
        name=profile.get("name"),
        token=token,
        expires_in=expires_in
    )

    return {"status": "ok"}



@router.post("/deauthorize")
async def deauthorize(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # form = await request.form()
    # signed_request = form.get("signed_request")

    # if not signed_request:
    #     raise HTTPException(status_code=400, detail="Missing signed_request")

    # data = parse_signed_request(signed_request)
    # if not data:
    #     raise HTTPException(status_code=400, detail="Invalid signed_request")

    # user_id = str(data.get("user_id") or data.get("profile_id") or "")

    # await handle_deauthorize(db, user_id=user_id, payload=data)

    return {
        "status": "ok",
        # "deauthorized_user": user_id,
    }


@router.post("/delete_data")
async def delete_data(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # form = await request.form()
    # signed_request = form.get("signed_request")

    # if not signed_request:
    #     raise HTTPException(status_code=400, detail="Missing signed_request")

    # data = parse_signed_request(signed_request)
    # if not data:
    #     raise HTTPException(status_code=400, detail="Invalid signed_request")

    # user_id = str(data.get("user_id") or data.get("profile_id") or "")

    # confirmation_code = uuid.uuid4()

    # await handle_delete_data(
    #     db,
    #     user_id=user_id,
    #     confirmation_code=confirmation_code,
    #     payload=data,
    # )

    # status_url = f"{settings.app_base_url}/delete-data/status/{confirmation_code}"

    return {
        "status": "ok",
        # "deauthorized_user": user_id,
    }