import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

# --- Logging Configuration ---
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOGGING_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler() # Log to console
    ]
)

def get_logger(name):
    """Creates a configured logger instance."""
    return logging.getLogger(name)

# --- Telegram Configuration ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("TELEGRAM_USER_ID", 0))
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
if ADMIN_CHAT_ID:
    try:
        ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)
    except ValueError:
        ADMIN_CHAT_ID = None

# --- Gemini AI Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Database Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///hotel_os_bot.db")

# --- MQTT Configuration ---
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "hotel/room1")

# --- Validation ---
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")
if not AUTHORIZED_USER_ID:
    raise ValueError("TELEGRAM_USER_ID environment variable not set!")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set!")
