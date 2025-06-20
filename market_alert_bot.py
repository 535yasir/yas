import yfinance as yf
import telebot
import time
import pandas as pd
from datetime import datetime

# إعدادات البوت
TELEGRAM_TOKEN = '8151824172:AAFUxxjqtxk3wt_um-U9FWW7JSQjopSI8hg'
CHAT_ID = '6500755943'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# تحميل قائمة الأسهم
with open("all_us_stocks.txt") as f:
    tickers = [line.strip() for line in f if line.strip()]

# إعدادات المراقبة
chunk_size = 300
sleep_interval = 10
sent_alerts = {}

bot.send_message(CHAT_ID, "🚀 تم تشغيل البوت ✅ — جاري مراقبة السوق\n(After + Pre + Regular Market)")

# الدالة الرئيسية لمراقبة الأسهم
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

            # زخم عالي
            if price_change_pct >= 3 and symbol not in sent_alerts:
                text = f"🚨 *{symbol}* — زخم عالي!\n💰 السعر الحالي: {round(current_price, 2)}\n📈 التغير: {round(price_change_pct, 2)} %"
                bot.send_message(CHAT_ID, text, parse_mode="Markdown")
                sent_alerts[symbol] = True

            # سيولة استثنائية
            if volume_ratio >= 3:
                text = f"🔴 سيولة استثنائية!\n{symbol}\n💵 السيولة الحالية: {round(volume_now)}\n📊 متوسط 60 دقيقة: {round(avg_volume)}\n🔥 دخل أكثر من {round(volume_ratio, 1)}x السيولة المعتادة!"
                bot.send_message(CHAT_ID, text)

        except Exception as e:
            print(f"Error for {symbol}: {e}")

# تقسيم الأسهم إلى دفعات
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
