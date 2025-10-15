import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# OpenAI
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

GROQ_KEY = os.getenv("GROQ_API_KEY")
# Admin (optional, can be 0)
ADMIN_ID = int(os.getenv("ADMIN_ID", "7075011101"))

AAU_NEWS_BOT = os.getenv("AAU_NEWS_BOT", "https://t.me/AAU_STUDENTSBOT")
MODULES_BOT = os.getenv("MODULES_BOT", "https://t.me/Savvysocietybot")
