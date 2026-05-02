# app/api/routes/health.py
import logging
from fastapi import APIRouter
from app.api.schemas import HealthResponse
from app.config import APP_ENV
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API and database connectivity."""
    db_status = "ok"
    try:
        db = SessionLocal()
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db.close()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "error"

    return HealthResponse(
        status="ok",
        env=APP_ENV,
        database=db_status,
    )