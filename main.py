import yfinance as yf
import pandas as pd
import time
import requests
import os

# إعدادات تيليجرام (من متغيرات البيئة)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# تحميل قائمة الأسهم من ملف CSV
tickers = pd.read_csv("tickers.csv")["symbol"].tolist()

# الحد الأدنى للزخم أو السيولة لإرسال التنبيه
MIN_VOLUME = 5_000_000
MIN_PERCENT_CHANGE = 4

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("خطأ في إرسال التنبيه:", e)

while True:
    for symbol in tickers:
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period="1d", interval="5m")

            if df.empty or len(df) < 2:
                continue

            last_row = df.iloc[-1]
            prev_row = df.iloc[-2]

            price_now = last_row["Close"]
            price_before = prev_row["Close"]
            volume_now = last_row["Volume"]
            percent_change = ((price_now - price_before) / price_before) * 100

            if volume_now >= MIN_VOLUME or abs(percent_change) >= MIN_PERCENT_CHANGE:
                msg = f"""🚨 تنبيه لحظي:
🔹 الرمز: {symbol}
💵 السعر: {round(price_now, 2)}$
📈 التغير: {round(percent_change, 2)}%
🔊 السيولة: {int(volume_now):,}"""

                send_telegram_alert(msg)
                print("تم إرسال تنبيه:", symbol)
        except Exception as e:
            print(f"خطأ في {symbol}: {e}")
    time.sleep(60)  # كل دقيقة