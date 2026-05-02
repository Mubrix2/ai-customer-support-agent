# app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, health
from app.config import APP_ENV
from app.db.database import init_db
from app.core.agent import get_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting AI Customer Support Agent API | env={APP_ENV}")
    # Initialise database tables
    init_db()
    # Pre-compile the agent so first request is not slow
    get_agent()
    logger.info("Database and agent ready.")
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Customer Support Agent",
        description=(
            "A multi-turn AI support agent for TechMart Nigeria. "
            "Handles order inquiries, complaints, and escalations."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(chat.router, prefix="/api/v1")

    return app


app = create_app()