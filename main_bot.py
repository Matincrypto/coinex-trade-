# main_bot.py
"""
فایل اجرایی اصلی ربات (Main Bot Runner).
این فایل مسئول اجرای حلقه اصلی ربات، دریافت سیگنال،
پردازش منطق ریورس (Reverse Logic) و فراخوانی توابع API و DB است.
"""
import requests
import time
import json
import config      # ایمپورت فایل تنظیمات
import db_manager  # ایمپورت مدیر دیتابیس
import coinex_api  # ایمپورت توابع API کوینکس

def get_latest_signal():
    """
    آخرین سیگنال را از API سیگنال‌دهی دریافت می‌کند.
    """
    try:
        response = requests.get(config.SIGNAL_API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("[Signal] خطای Timeout: سرور سیگنال پاسخ نداد.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[Signal] خطا در دریافت سیگنال: {e}")
        return None
    except json.JSONDecodeError:
        print("[Signal] خطا: پاسخ سرور سیگنال، فرمت JSON معتبر ندارد.")
        return None

def process_signal(signal_data):
    """
    هسته اصلی منطق ربات: پردازش سیگنال و اجرای مکانیزم ریورس.
    """
    
    # --- 1. استخراج داده‌های سیگنال ---
    symbol = signal_data.get("symbol")
    signal_id = signal_data.get("signal_id")
    signal_side_str = signal_data.get("signal_side") # "BUY" or "SELL"
    entry_price = signal_data.get("entry_price")
    
    # --- 2. فیلتر کردن سیگنال ---
    if symbol != config.TARGET_SYMBOL:
        return # سیگنال برای ارز مورد نظر ما نیست

    # تبدیل سیگنال "BUY"/"SELL" به پوزیشن "long"/"short"
    new_position_side = "long" if signal_side_str == "BUY" else "short"
    
    # --- 3. بررسی وضعیت فعلی (از دیتابیس) ---
    current_db_position = db_manager.get_position(config.TARGET_SYMBOL)
    
    # --- 4. جلوگیری از اجرای سیگنال تکراری ---
    if current_db_position and current_db_position['last_signal_id'] == signal_id:
        print(f"[Logic] سیگنال {signal_id} تکراری است. نادیده گرفته شد.")
        return

    print(f"--- 🟢 سیگنال جدید {config.TARGET_SYMBOL} دریافت شد ---")
    print(f"  ID: {signal_id} | Side: {new_position_side} | Price: {entry_price}")

    # --- 5. محاسبه مقدار سفارش (بر اساس 7 تتر) ---
    if entry_price is None or entry_price <= 0:
        print(f"  [Error] قیمت ورودی نامعتبر ({entry_price}). سیگنال نادیده گرفته شد.")
        return
        
    try:
        order_amount_btc_float = config.ORDER_USDT_VALUE / entry_price
        order_amount = f"{order_amount_btc_float:.8f}" # فرمت رشته‌ای با ۸ رقم اعشار
    except (TypeError, ZeroDivisionError) as e:
        print(f"  [Error] خطا در محاسبه مقدار سفارش: {e}. قیمت ورودی: {entry_price}")
        return

    limit_price = str(entry_price) # قیمت لیمیت برای سفارش
    print(f"  محاسبه: معامله {config.ORDER_USDT_VALUE}$ در {limit_price}$ = {order_amount} BTC")

    # --- 6. پیاده‌سازی منطق ریورس (Reverse Logic) ---
    
    if current_db_position is None:
        # --- حالت ۱: هیچ پوزیشنی نداریم ---
        print("  [Logic] وضعیت: پوزیشنی در دیتابیس نیست.")
        print(f"  [Action] در حال باز کردن پوزیشن جدید {new_position_side}...")
        
        order_result = coinex_api.place_limit_order(
            market=config.TARGET_SYMBOL,
            side=signal_side_str.lower(), # 'buy' or 'sell'
            amount=order_amount,
            price=limit_price
        )
        
        if order_result:
            db_manager.update_position(
                symbol=config.TARGET_SYMBOL,
                side=new_position_side,
                price=entry_price,
                amount=order_amount, # مقدار BTC را ذخیره می‌کنیم
                signal_id=signal_id
            )

    elif current_db_position['side'] != new_position_side:
        # --- حالت ۲: سیگنال جدید در خلاف جهت پوزیشن فعلی است (REVERSE) ---
        current_side = current_db_position['side']
        current_amount = current_db_position['amount']
        
        print(f"  [Logic] وضعیت: ریورس سیگنال! (پوزیشن فعلی: {current_side}، سیگنال جدید: {new_position_side})")
        
        # 1. بستن پوزیشن فعلی
        print(f"  [Action 1] در حال بستن پوزیشن {current_side} با مقدار {current_amount}...")
        close_result = coinex_api.close_limit_order(
            market=config.TARGET_SYMBOL,
            side_to_close=current_side, 
            amount=current_amount,
            price=limit_price # با قیمت سیگنال جدید می‌بندیم
        )
        
        if close_result is None:
            print("  [Error] خطای مهم: پوزیشن قبلی بسته نشد. عملیات ریورس متوقف شد.")
            return # از ادامه عملیات (باز کردن پوزیشن جدید) جلوگیری کن

        # 2. باز کردن پوزیشن جدید در جهت سیگنال
        print(f"  [Action 2] در حال باز کردن پوزیشن جدید {new_position_side} با مقدار {order_amount}...")
        new_order_result = coinex_api.place_limit_order(
            market=config.TARGET_SYMBOL,
            side=signal_side_str.lower(),
            amount=order_amount,
            price=limit_price
        )
        
        if new_order_result:
            # آپدیت دیتابیس با اطلاعات پوزیشن جدید
            db_manager.update_position(
                symbol=config.TARGET_SYMBOL,
                side=new_position_side,
                price=entry_price,
                amount=order_amount, # مقدار جدید BTC ذخیره می‌شود
                signal_id=signal_id
            )

    else:
        # --- حالت ۳: سیگنال جدید هم جهت با پوزیشن فعلی است ---
        print(f"  [Logic] وضعیت: سیگنال جدید ({new_position_side}) هم جهت با پوزیشن فعلی است.")
        print("  [Action] سیگنال نادیده گرفته شد (جلوگیری از انباشت پوزیشن).")
        pass


def start_bot_loop():
    """حلقه اصلی ربات برای بررسی مداوم سیگنال‌ها."""
    
    print(f"...:: ربات تریدر CoinEx (مدل ریورس) در حال اجرا است ::...")
    print(f"...:: فقط {config.TARGET_SYMBOL} معامله خواهد شد ::...")
    print(f"...:: بررسی سیگنال هر {config.LOOP_SLEEP_TIME_SECONDS} ثانیه ::...")

    while True:
        try:
            signal = get_latest_signal()
            
            if signal:
                process_signal(signal)
            
            time.sleep(config.LOOP_SLEEP_TIME_SECONDS) 
            
        except KeyboardInterrupt:
            print("\n...:: دریافت سیگنال توقف (Ctrl+C). ربات متوقف شد ::...")
            break
        except Exception as e:
            print(f"!!! خطای پیش‌بینی نشده در حلقه اصلی: {e}")
            print(f"ربات {config.LOOP_SLEEP_TIME_SECONDS * 2} ثانیه استراحت کرده و دوباره تلاش می‌کند...")
            time.sleep(config.LOOP_SLEEP_TIME_SECONDS * 2)

# --- بخش اصلی اجرای ربات ---
if __name__ == "__main__":
    
    print("--- [1/3] در حال راه‌اندازی ربات تریدر ---")
    
    # --- 1. آماده‌سازی اولیه دیتابیس ---
    print("\n--- [2/3] در حال بررسی و آماده‌سازی دیتابیس... ---")
    if not db_manager.initialize_database():
        print("\n!!! خطای بحرانی: اتصال به دیتابیس برقرار نشد. ربات متوقف می‌شود. !!!")
        exit(1) # خروج از برنامه با کد خطا

    # --- 2. تنظیم اهرم در صرافی (بر اساس کانفیگ) ---
    print("\n--- [3/3] در حال تنظیم اهرم در صرافی CoinEx... ---")
    leverage_set_success = coinex_api.adjust_leverage(
        market=config.TARGET_SYMBOL,
        margin_mode=config.TARGET_MARGIN_MODE,
        leverage=config.TARGET_LEVERAGE
    )
    
    # --- 3. شروع حلقه اصلی ربات ---
    if leverage_set_success:
        print("\n--- ✅ راه‌اندازی کامل شد. شروع حلقه اصلی معاملات... ---")
        start_bot_loop()
    else:
        print("\n!!! خطای بحرانی: اهرم تنظیم نشد. ربات اجرا نمی‌شود !!!")
        print("لطفا تنظیمات API (دسترسی فیوچرز) یا مقادیر کانفیگ را بررسی کنید.")
        exit(1) # خروج از برنامه با کد خطا
