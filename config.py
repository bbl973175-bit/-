import os
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "").strip()
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "").strip()
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://127.0.0.1:5000/callback")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-me")
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "nexora.db"))
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "127.0.0.1")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "5000"))
def validate_bot_config():
    if not BOT_TOKEN or BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        raise RuntimeError("Set DISCORD_BOT_TOKEN in your .env file.")
