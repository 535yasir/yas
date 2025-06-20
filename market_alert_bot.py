import yfinance as yf
import telebot
import time
import pandas as pd
from datetime import datetime

# إعدادات البوت
TELEGRAM_TOKEN = '8151824172:AAFUxxjqtxk3wt_um-U9FWW7JSQjopSI8hg'
CHAT_ID = '6500755943'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# قراءة قائمة الأسهم تحت 50$
with open("under_50_symbols.txt") as f:
    tickers = [line.strip() for line in f if line.strip()]

# إعدادات
chunk_size = 100
sleep_interval = 10
sent_alerts = {}

bot.send_message(CHAT_ID, "🚀 تم تشغيل البوت ✅ — جاري مراقبة الأسهم تحت 50 دولار\n(After + Pre + Regular Market)")

# فحص الأسهم
def process_chunk(chunk):
    for symbol in chunk:
        try:
            df = yf.download(symbol, period="1d", interval="1m", prepost=True, progress=False)
            if df.empty or len(df) < 5:
                continue

            current_price = df['Close'][-1]
            price_5min_ago = df['Close'][-5]
            price_change_pct = ((current_price - price_5min_ago) / price_5min_ago) * 100

            volume_now = df['Volume'][-1]
            avg_volume = df['Volume'][-60:].mean()
            volume_ratio = volume_now / avg_volume if avg_volume else 0

            stock_week = yf.Ticker(symbol).history(period="1wk", interval="1d")
            week_low = round(stock_week['Low'].min(), 2)
            week_high = round(stock_week['High'].max(), 2)

            entry_zone = ""
            if current_price > week_high:
                entry_zone = "🚀 كسر القمة — فرصة دخول"
            elif current_price < week_low:
                entry_zone = "🔻 كسر القاع — فرصة دخول"

            now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

            if (price_change_pct >= 3 or volume_ratio >= 3 or current_price > week_high or current_price < week_low) and symbol not in sent_alerts:
                message = (
                    f"🚨 زخم على {symbol}\n"
                    f"🚀 دخول الآن بسعر: ${round(current_price, 2)}\n"
                    f"📈 التغير 5 دقائق: {round(price_change_pct, 2)} %\n"
                    f"💰 حجم الآن: {round(volume_now)}\n"
                    f"📊 متوسط حجم 60 دقيقة: {round(avg_volume)}\n"
                    f"🔥 نسبة السيولة: {round(volume_ratio, 1)}x\n"
                    f"📉 أدنى أسبوع: {week_low} | 📈 أعلى أسبوع: {week_high}\n"
                    f"{entry_zone}\n"
                    f"⏰ {now}"
                )
                bot.send_message(CHAT_ID, message)
                sent_alerts[symbol] = True

        except Exception as e:
            print(f"Error for {symbol}: {e}")

# تقسيم الأسهم
def chunks(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

# بدء المراقبة
while True:
    now = datetime.utcnow()
    print(f"\n⏰ Running scan at {now} UTC — {len(tickers)} symbols")
    for chunk in chunks(tickers, chunk_size):
        process_chunk(chunk)
        time.sleep(sleep_interval)
