"""Application configuration."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root or next to executable
if getattr(sys, "frozen", False):
    _BASE_DIR = Path(sys.executable).parent
else:
    _BASE_DIR = Path(__file__).resolve().parent

load_dotenv(_BASE_DIR / ".env")

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{(_BASE_DIR / 'testing_system.db').as_posix()}",
)

# Open Trivia DB API (https://opentdb.com/) — free, no API key required
OPENTDB_BASE_URL = os.getenv("OPENTDB_BASE_URL", "https://opentdb.com/api.php")
OPENTDB_CATEGORY_URL = os.getenv(
    "OPENTDB_CATEGORY_URL", "https://opentdb.com/api_category.php"
)
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "15"))
USE_FALLBACK_ON_ERROR = os.getenv("USE_FALLBACK_ON_ERROR", "true").lower() == "true"

# Application defaults
APP_NAME = "Online Testing System"
APP_VERSION = "1.0.0"
DEFAULT_QUESTIONS = int(os.getenv("DEFAULT_QUESTIONS", "10"))
DEFAULT_DURATION_MINUTES = int(os.getenv("DEFAULT_DURATION_MINUTES", "15"))
DEFAULT_THEME = os.getenv("DEFAULT_THEME", "dark")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
DEFAULT_SOUND = os.getenv("DEFAULT_SOUND", "true").lower() == "true"

# Topic → Open Trivia DB category ID (None = any category)
TOPIC_CATEGORY_MAP: dict[str, int | None] = {
    "Computer Science": 18,       # Science: Computers
    "Programming": 18,            # Science: Computers
    "Mathematics": 19,            # Science: Mathematics
    "Physics": 17,                # Science & Nature
    "Verilog": 18,                # Closest available category
    "Digital Logic": 18,          # Closest available category
    "General Knowledge": 9,
}

TOPICS = list(TOPIC_CATEGORY_MAP.keys())
QUESTION_COUNTS = [5, 10, 20, 30, 50]
TIME_LIMITS = {
    "5 minutes": 5,
    "10 minutes": 10,
    "15 minutes": 15,
    "30 minutes": 30,
    "60 minutes": 60,
}
POINTS_PER_QUESTION = 1
