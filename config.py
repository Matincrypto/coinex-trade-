# config.py
"""
فایل تنظیمات ربات (Config File).
تمام اطلاعات حساس، کلیدهای API، اطلاعات دیتابیس و پارامترهای
ثابت ربات در اینجا ذخیره می‌شوند.
"""

# --- 1. تنظیمات API صرافی CoinEx ---
# (!!! اینجا کلیدهای جدید و معتبر خود را با دسترسی فیوچرز وارد کنید !!!)
COINEX_ACCESS_ID = "81CBDCBC00E94A689B82F4CFEF8A75E1"
COINEX_SECRET_KEY = "28CF6727B4BA1BC7FD3FAEE0D0B7794753EB397011E41F0F"

# --- 2. تنظیمات API سیگنال ---
SIGNAL_API_URL = "http://103.75.198.172:8080/signals"

# --- 3. تنظیمات پایگاه داده MySQL ---
DB_HOST = "localhost"
DB_USER = "your_db_user"
DB_PASSWORD = "YourStrongPassword123!"
DB_NAME = "coinex_bot_db"

# --- 4. تنظیمات ترید و پوزیشن ---
TARGET_SYMBOL = "BTCUSDT"
ORDER_USDT_VALUE = 7.0
TARGET_LEVERAGE = 10
TARGET_MARGIN_MODE = "cross"

# --- 5. تنظیمات اجرای ربات ---
LOOP_SLEEP_TIME_SECONDS = 15
