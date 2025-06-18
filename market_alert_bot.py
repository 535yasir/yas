import yfinance as yf
import telebot
import time
import threading
import pandas as pd
import datetime

# إعدادات البوت
TELEGRAM_TOKEN = '8151824172:AAFUxxjqtxk3wt_um-U9FWW7JSQjopSI8hg'
CHAT_ID ='6500755943'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# رسالة تأكيد بدء التشغيل
bot.send_message(CHAT_ID, "🚀 تم تشغيل البوت ✅ — جاري مراقبة السوق (After + Pre + Regular Market)")

# قراءة قائمة الأسهم
with open('all_us_stocks.txt', 'r') as f:
    tickers = [line.strip() for line in f.readlines()]

# إعدادات
chunk_size = 300
sleep_interval = 10
top_momentum_interval = 15 * 60

sent_alerts = set()
momentum_scores = {}

def process_chunk(chunk):
    for symbol in chunk:
        try:
            df = yf.download(symbol, period="1d", interval="1m", prepost=True, progress=False)
            if df.empty or len(df) < 16:
                continue

            current_price = df['Close'][-1]
            price_open_today = df['Close'][0]
            price_15min_ago = df['Close'][-16]

            daily_change_pct = ((current_price - price_open_today) / price_open_today) * 100
            price_change_15min = ((current_price - price_15min_ago) / price_15min_ago) * 100

            volume_now = df['Volume'][-1]
            avg_volume = df['Volume'][-16:-1].mean()
            volume_ratio = volume_now / avg_volume if avg_volume else 0

            stock_week = yf.Ticker(symbol).history(period="1wk", interval="1d")
            if stock_week.empty:
                continue

            week_low = round(stock_week['Low'].min(), 2)
            week_high = round(stock_week['High'].max(), 2)

            momentum_score = (daily_change_pct * volume_ratio)
            momentum_scores[symbol] = momentum_score

            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if (daily_change_pct >= 3 or price_change_15min >= 3 or volume_ratio >= 2) and symbol not in sent_alerts:
                entry_zone = ""
                if current_price > week_high:
                    entry_zone = "🚀 كسر القمة — فرصة دخول"
                elif current_price < week_low:
                    entry_zone = "🔻 كسر القاع — فرصة دخول"

                message = (
                    f"🚨 زخم مفاجئ على {symbol}\n"
                    f"🔼 السعر الحالي: {round(current_price, 2)}\n"
                    f"📈 التغير اليومي: {round(daily_change_pct, 2)}٪\n"
                    f"📊 التغير آخر 15 دقيقة: {round(price_change_15min, 2)}٪\n"
                    f"🔥 نسبة الزخم: {round(volume_ratio, 2)}x\n"
                    f"📉 أقل سعر أسبوعي: {week_low}\n"
                    f"📈 أعلى سعر أسبوعي: {week_high}\n"
                    f"{entry_zone}\n"
                    f"⏰ {now}"
                )
                bot.send_message(CHAT_ID, message)
                sent_alerts.add(symbol)

        except Exception as e:
            print(f"⚠️ Skipping {symbol}: {e}")
            continue

def momentum_report():
    bot.send_message(CHAT_ID, "✅ بدأ تقرير Top 10 Momentum — سيتم الإرسال كل 15 دقيقة.")
    while True:
        time.sleep(top_momentum_interval)
        if not momentum_scores:
            continue

        top_10 = sorted(momentum_scores.items(), key=lambda x: x[1], reverse=True)[:10]

        report = "🔥 Top 10 Momentum Stocks 🔥\n"
        for i, (symbol, score) in enumerate(top_10, 1):
            report += f"{i}. {symbol} — Momentum Score: {round(score, 2)}\n"

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report += f"\n⏰ {now}"

        bot.send_message(CHAT_ID, report)

def start_bot():
    total_chunks = len(tickers) // chunk_size + 1
    while True:
        for i in range(total_chunks):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size
            chunk = tickers[start_idx:end_idx]
            process_chunk(chunk)
            time.sleep(sleep_interval)

# تشغيل البوت
threading.Thread(target=start_bot).start()
threading.Thread(target=momentum_report).start()
