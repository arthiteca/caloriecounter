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
