# config.py
"""
فایل تنظیمات ربات (Config File).
تمام اطلاعات حساس، کلیدهای API، اطلاعات دیتابیس و پارامترهای
ثابت ربات در اینجا ذخیره می‌شوند.
"""

# --- 1. تنظیمات API صرافی CoinEx ---
# (این کلیدها را با کلیدهای واقعی خود جایگزین کنید)
COINEX_ACCESS_ID = "81CBDCBC00E94A689B82F4CFEF8A75E1"
COINEX_SECRET_KEY = "28CF6727B4BA1BC7FD3FAEE0D0B7794753EB397011E41F0F"

# --- 2. تنظیمات API سیگنال ---
# آدرس API که سیگنال‌های ترید را از آن دریافت می‌کنیم
SIGNAL_API_URL = "http://103.75.198.172:8080/signals"

# --- 3. تنظیمات پایگاه داده MySQL ---
DB_HOST = "localhost"  # یا آدرس IP سرور دیتابیس
DB_USER = "your_db_user" # نام کاربری دیتابیس شما
DB_PASSWORD = "YourStrongPassword123!" # پسورد دیتابیس
DB_NAME = "coinex_bot_db" # نام دیتابیسی که ایجاد می‌کنید

# --- 4. تنظیمات ترید و پوزیشن ---
# ربات فقط روی این ارز کار خواهد کرد
TARGET_SYMBOL = "BTCUSDT"

# مقدار هر معامله بر حسب تتر (USDT)
# ربات این مقدار را به صورت خودکار به BTC تبدیل می‌کند
ORDER_USDT_VALUE = 7.0

# اهرم و مد مارجین که ربات در شروع کار تنظیم خواهد کرد
TARGET_LEVERAGE = 10           # اهرم مورد نظر (عدد صحیح)
TARGET_MARGIN_MODE = "cross"   # "cross" or "isolated"

# --- 5. تنظیمات اجرای ربات ---
# فاصله زمانی (به ثانیه) بین هر بار چک کردن سیگنال
LOOP_SLEEP_TIME_SECONDS = 15
