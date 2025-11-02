# coinex_api.py
"""
ماژول API صرافی CoinEx.
شامل تمام توابع برای تعامل با اندپوینت‌های CoinEx،
از جمله احراز هویت، تنظیم اهرم، و ثبت سفارش.
"""
import requests
import hashlib
import json
import time
import config

# آدرس پایه API صرافی
BASE_URL = "https://api.coinex.com"

def _get_auth_headers(endpoint: str, body_str: str, method: str = "POST"):
    """
    یک تابع کمکی داخلی برای ساخت هدرهای احراز هویت V2.
    """
    timestamp = str(int(time.time() * 1000))
    
    # V2 Signature: Method + Endpoint + Body + Timestamp + SecretKey
    string_to_sign = f"{method}{endpoint}{body_str}{timestamp}{config.COINEX_SECRET_KEY}"
    
    signature = hashlib.sha256(string_to_sign.encode('utf-8')).hexdigest()
    
    return {
        'Content-Type': 'application/json',
        'X-COINEX-API-KEY': config.COINEX_ACCESS_ID,
        'X-COINEX-SIGNATURE': signature,
        'X-COINEX-TIMESTAMP': timestamp
    }

def adjust_leverage(market: str, margin_mode: str, leverage: int):
    """
    تنظیم اهرم و مد مارجین برای یک مارکت فیوچرز.
    """
    endpoint = "/futures/adjust-position-leverage"
    url = BASE_URL + endpoint
    
    body = {
        "market": market,
        "market_type": "FUTURES",
        "margin_mode": margin_mode,
        "leverage": leverage
    }
    body_str = json.dumps(body)
    
    headers = _get_auth_headers(endpoint, body_str, "POST")
    
    print(f"[API] 🌀 در حال تنظیم اهرم برای {market} به {leverage}x ({margin_mode})")
    
    try:
        response = requests.post(url, data=body_str, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if result.get("code") == 0:
            print(f"[API] ✅ موفقیت: اهرم با موفقیت تنظیم شد.")
            return result.get("data")
        else:
            print(f"[API] ❌ خطای API در تنظیم اهرم: {result.get('message')}")
            return None
            
    except requests.exceptions.HTTPError as http_err:
        print(f"[API] خطای HTTP (تنظیم اهرم): {http_err} | Response: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"[API] خطای Request (تنظیم اهرم): {err}")
        
    return None

def place_limit_order(market: str, side: str, amount: str, price: str):
    """
    برای ثبت سفارش لیمیت در فیوچرز CoinEx (برای باز کردن پوزیشن).
    Parameters: side (str): جهت سفارش ("buy" or "sell")
    """
    endpoint = "/futures/put-limit-order"
    url = BASE_URL + endpoint
    
    body = {
        "market": market,
        "market_type": "FUTURES",
        "side": side.lower(), # "buy" or "sell"
        "amount": amount,
        "price": price,
        "effect_type": "normal" # 'normal' برای باز کردن پوزیشن
    }
    body_str = json.dumps(body)
    
    headers = _get_auth_headers(endpoint, body_str, "POST")
    
    print(f"[API] 🌀 ارسال سفارش {side} {market} | Amount: {amount} | Price: {price}")
    
    try:
        response = requests.post(url, data=body_str, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if result.get("code") == 0:
            print(f"[API] ✅ موفقیت: سفارش {side} {market} با موفقیت ثبت شد.")
            return result.get("data")
        else:
            print(f"[API] ❌ خطای API در ثبت سفارش: {result.get('message')}")
            return None
            
    except requests.exceptions.HTTPError as http_err:
        print(f"[API] خطای HTTP (ثبت سفارش): {http_err} | Response: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"[API] خطای Request (ثبت سفارش): {err}")
        
    return None

def close_limit_order(market: str, side_to_close: str, amount: str, price: str):
    """
    برای بستن یک پوزیشن باز با یک سفارش لیمیت.
    Parameters: side_to_close (str): جهت پوزیشن فعلی ('long' or 'short')
    """
    
    # برای بستن 'long'، باید 'sell' کنیم.
    # برای بستن 'short'، باید 'buy' کنیم.
    close_side = "sell" if side_to_close == "long" else "buy"
    
    print(f"[API] 🌀 اقدام برای بستن پوزیشن {side_to_close} با سفارش {close_side} ...")
    
    # برای بستن پوزیشن از همان اندپوینت 'place_limit_order' استفاده می‌کنیم
    return place_limit_order(market, close_side, amount, price)
