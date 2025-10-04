import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"  # Используем gpt-4o вместо gpt-5-codex (который пока не доступен)
OPENAI_VISION_MODEL = "gpt-4o"  # Модель с поддержкой vision

# Database Configuration
DATABASE_PATH = "calorie_counter.db"

# Rate Limiting
MAX_REQUESTS_PER_MINUTE = 20

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "bot.log"

# Daily calorie recommendations (можно расширить для разных пользователей)
DEFAULT_DAILY_CALORIES = 2000

# СБП Configuration
SBP_MERCHANT_ID = os.getenv("SBP_MERCHANT_ID", "your_merchant_id")
SBP_SECRET_KEY = os.getenv("SBP_SECRET_KEY", "your_secret_key")
SBP_API_URL = os.getenv("SBP_API_URL", "https://sbp.nspk.ru/api/")

# Payment Server Configuration
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
SERVER_IP = os.getenv("SERVER_IP", "188.253.16.50")

# Webhook URL (автоматически формируется)
WEBHOOK_URL = f"http://{SERVER_IP}:{SERVER_PORT}/webhook/sbp"

# Payment Configuration
PAYMENT_PRICES = {
    "limited_10": {"price": 100, "limit": 10, "description": "10 анализов"},
    "limited_50": {"price": 400, "limit": 50, "description": "50 анализов"},
    "limited_100": {"price": 700, "limit": 100, "description": "100 анализов"},
    "unlimited": {"price": 1500, "limit": None, "description": "Безлимитный доступ"}
}
