from fastapi import FastAPI
from routers.instagram_auth import router as auth_router
from routers.instagram_webhook import router as webhook_router
from routers.instagram_static import static_router

app = FastAPI(title="Instagram Bot Application")

app.include_router(auth_router)
app.include_router(webhook_router)
app.include_router(static_router)
