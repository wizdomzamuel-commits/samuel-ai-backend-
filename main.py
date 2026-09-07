"""
Samuel AI — personal assistant backend.

Entrypoint that wires together the FastAPI app, database, routes, and
background scheduler.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import notifications, summaries
from app.core.config import get_settings
from app.db.database import init_db
from app.services.scheduler_service import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="A personal AI assistant backend: notification storage + OpenAI-powered daily/weekly summaries.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notifications.router, prefix=settings.API_V1_PREFIX)
app.include_router(summaries.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["health"])
def root():
    return {"app": settings.APP_NAME, "status": "ok"}


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy"}
