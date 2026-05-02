# app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, health
from app.config import APP_ENV, BASE_DIR
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
    init_db()
    # Auto-seed if database is empty
    _auto_seed()
    get_agent()
    logger.info("Database, seed data, and agent ready.")
    yield


def _auto_seed():
    """Seed the database with mock data if it is empty."""
    from app.db.database import SessionLocal
    from app.db.models import Order
    db = SessionLocal()
    try:
        count = db.query(Order).count()
        if count == 0:
            logger.info("Database is empty — running seed data")
            import sys
            sys.path.append(str(BASE_DIR))
            from scripts.seed_data import seed
            seed()
        else:
            logger.info(f"Database already has {count} orders — skipping seed")
    finally:
        db.close()

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