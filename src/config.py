import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory Paths
SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parent
DATA_DIR = BASE_DIR / "data"

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# API Keys & Models
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_MODEL = "gemini-3.6-flash"
EMBEDDING_MODEL = "gemini-embedding-001"

# Application Metadata
APP_NAME = "BizShield AI"
APP_TAGLINE = "AI-Powered Legal & Tax Assistant for Small Businesses"
APP_VERSION = "1.0.0 (Hackathon MVP)"
