import yfinance as yf
import pandas as pd
import time
import requests
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

tickers = pd.read_csv("tickers.csv")["Symbol"].tolist()

MIN_PERCENT_CHANGE = 3
VOLUME_THRESHOLD = 5_000_000
ZOKHOM_RATIO = 2

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("❌ خطأ في إرسال التنبيه:", e)

while True:
    for symbol in tickers:
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period="1d", interval="5m")

            if df.empty or len(df) < 5:
                continue

            last = df.iloc[-1]
            prev = df.iloc[-2]
            avg_volume = df["Volume"].rolling(window=5).mean().iloc[-1]

            price_now = last["Close"]
            price_before = prev["Close"]
            volume_now = last["Volume"]
            percent_change = ((price_now - price_before) / price_before) * 100

            if (
                percent_change >= MIN_PERCENT_CHANGE
                or volume_now >= VOLUME_THRESHOLD
                or volume_now > avg_volume * ZOKHOM_RATIO
            ):
                msg = f"""🚨 تنبيه لحظي:
📈 الرمز: {symbol}
💵 السعر: {round(price_now, 2)} $
📊 التغير: {round(percent_change, 2)} %
🔊 حجم التداول: {int(volume_now):,}
🔁 متوسط الحجم: {int(avg_volume):,}"""

                send_telegram_alert(msg)
                print("✅ تم إرسال تنبيه:", symbol)
        except Exception as e:
            print(f"⚠️ خطأ في {symbol}: {e}")

    time.sleep(15)
