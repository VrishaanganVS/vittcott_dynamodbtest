import os
from dotenv import load_dotenv

# Load environment variables from .env file at project root
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path=env_path)

# API Keys and Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FINANCEHUB_API_KEY = os.getenv("FINANCEHUB_API_KEY")

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_PORTFOLIO_BUCKET = os.getenv("S3_PORTFOLIO_BUCKET", "vittcott-uploads-xyz123")

# CORS and Frontend
FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "http://localhost:3000")

# AI/Prompt Settings
MAX_PROMPT_CHARS = int(os.getenv("MAX_PROMPT_CHARS", 2000))
AI_TIMEOUT_SECONDS = int(os.getenv("AI_TIMEOUT_SECONDS", 200))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", 4096))

# Uvicorn/Server
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "false").lower() in ("1", "true", "yes")
