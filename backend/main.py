from fastapi import FastAPI

from backend.api.routes.logs import router as logs_router
from backend.core.config import settings
from backend.core.logger import setup_logging

app: FastAPI = FastAPI(title="mini-SIEM Collector API")
setup_logging(settings.LOG_LEVEL)
app.include_router(logs_router)


@app.on_event("startup")
async def _startup() -> None:
    # Place for warmups if needed
    return
