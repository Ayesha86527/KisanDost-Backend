# app/config.py
"""
Application configuration and constants.
Uses environment variables where appropriate.
"""

from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

# API keys (set in .env or Codespaces secrets)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Default language and models
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
TTS_PREFIX = os.getenv("TTS_PREFIX", "response")

# OCR language: "en", "ur", "multilang", etc.
OCR_LANG = os.getenv("OCR_LANG", "en")

# Output directories (Path objects)
BASE_OUTPUT = Path("outputs")
OUTPUT_DIRS = {
    "voice_outputs": BASE_OUTPUT / "voice_outputs",
    "transcripts": BASE_OUTPUT / "transcripts",
    "recordings": BASE_OUTPUT / "recordings",
    "ocr_outputs": BASE_OUTPUT / "ocr"
}

# Create directories if they do not exist
for p in OUTPUT_DIRS.values():
    p.mkdir(parents=True, exist_ok=True)

# ==========================
# 🧩 APP SETTINGS
# ==========================
DEBUG = True                    # Enable for verbose logs (set False in production)

