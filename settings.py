import os
import pytz
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
GROUP_ID = int(os.getenv("GROUP_ID"))
TIMEZONE = os.getenv("TIMEZONE", "Asia/Tashkent")

# Настройка часового пояса
tz = pytz.timezone(TIMEZONE)

# Настройка диапазона: последние 7 дней
now = datetime.now(tz)
seven_days_ago = now - timedelta(days=7)

