"""Settings shared by every script. Change the model here, or set CLAUDE_MODEL in .env."""
import os

from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
MAX_WORKERS = 3  # how many test cases run at the same time


def require_api_key():
    """Stop with a clear message if the key is missing."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit(
            "ANTHROPIC_API_KEY is missing. Copy .env.example to .env and add your key."
        )
