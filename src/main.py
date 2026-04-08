import logging
import time

from fastapi import FastAPI, Request

from routers.instagram_auth import router as auth_router
from routers.instagram_static import static_router
from routers.instagram_webhook import router as webhook_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(title="Instagram Bot Application")
logger = logging.getLogger(__name__)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


app.include_router(auth_router)
app.include_router(webhook_router)
app.include_router(static_router)
