# backend/main.py
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from backend.api.routes.logs import router as logs_router
from backend.api.routes.read import router as read_router
from backend.core.config import settings
from backend.core.logger import setup_logging

# init logging sớm
setup_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # === startup ===
    # Place for warmups if needed
    yield
    # === shutdown ===
    # Place for teardowns if needed


app: FastAPI = FastAPI(title="mini-SIEM Collector API", lifespan=lifespan)
app.include_router(logs_router)
app.include_router(read_router)
