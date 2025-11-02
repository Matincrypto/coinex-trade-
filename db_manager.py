# db_manager.py
"""
مدیر پایگاه داده (Database Manager).
مسئول تمام ارتباطات با دیتابیس MySQL، شامل ایجاد جدول،
خواندن و به‌روزرسانی وضعیت پوزیشن‌ها.
"""
import mysql.connector
from mysql.connector import errorcode
import config

def create_connection():
    """ایجاد اتصال به پایگاه داده MySQL بر اساس اطلاعات کانفیگ"""
    try:
        conn = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("[DB Error] نام کاربری یا رمز عبور دیتابیس اشتباه است.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"[DB Error] دیتابیس '{config.DB_NAME}' وجود ندارد.")
        else:
            print(f"[DB Error] خطای اتصال به دیتابیس: {err}")
        return None

def initialize_database():
    """
    جدول مورد نیاز ربات را در دیتابیس ایجاد می‌کند.
    """
    conn = create_connection()
    if conn is None:
        print("[DB Error] اتصال به دیتابیس برای ساخت جدول برقرار نشد.")
        return False
        
    cursor = conn.cursor()
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS active_positions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(20) NOT NULL UNIQUE,
        side VARCHAR(10) NOT NULL,
        entry_price DECIMAL(20, 8) NOT NULL,
        amount VARCHAR(50) NOT NULL,
        last_signal_id VARCHAR(100)
    )
    """
    try:
        cursor.execute(create_table_query)
        print("[DB] موفقیت: جدول 'active_positions' بررسی/ایجاد شد.")
        return True
    except mysql.connector.Error as err:
        print(f"[DB] خطا در ایجاد جدول: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_position(symbol: str):
    """
    آخرین پوزیشن ذخیره شده در دیتابیس را برای یک سیمبل خاص برمی‌گرداند.
    """
    conn = create_connection()
    if conn is None:
        return None
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = "SELECT * FROM active_positions WHERE symbol = %s"
        cursor.execute(query, (symbol,))
        position = cursor.fetchone()
        return position
    except mysql.connector.Error as err:
        print(f"[DB] خطا در خواندن پوزیشن: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def update_position(symbol: str, side: str, price: float, amount: str, signal_id: str):
    """
    یک پوزیشن را در دیتابیس ذخیره یا آپدیت می‌کند (بر اساس سیمبل).
    """
    conn = create_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    
    query = """
    INSERT INTO active_positions (symbol, side, entry_price, amount, last_signal_id)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        side = VALUES(side),
        entry_price = VALUES(entry_price),
        amount = VALUES(amount),
        last_signal_id = VALUES(last_signal_id)
    """
    try:
        cursor.execute(query, (symbol, side, price, amount, signal_id))
        conn.commit()
        print(f"[DB] موفقیت: پوزیشن {symbol} در دیتابیس به {side} آپدیت شد.")
    except mysql.connector.Error as err:
        print(f"[DB] خطا در آپدیت پوزیشن: {err}")
    finally:
        cursor.close()
        conn.close()
