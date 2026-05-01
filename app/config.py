# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            f"Check your .env file against .env.example."
        )
    return value


# --- External services ---
GROQ_API_KEY: str = _require("GROQ_API_KEY")

# --- Database ---
DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/support.db")

# --- LLM ---
LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "10"))

# --- App ---
APP_ENV: str = os.getenv("APP_ENV", "development")