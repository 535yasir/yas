import yfinance as yf
import telebot
import time
import threading
import pandas as pd
import datetime

# إعدادات البوت
TELEGRAM_TOKEN = '8151824172:AAFUxxjqtxk3wt_um-U9FWW7JSQjopSI8hg'
CHAT_ID = '6500755943'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# رسالة تأكيد بدء التشغيل
bot.send_message(CHAT_ID, "🚀 تم تشغيل البوت ✅ — جاري مراقبة السوق (After + Pre + Regular Market)")

# قراءة قائمة الأسهم
with open('all_us_stocks.txt', 'r') as f:
    tickers = [line.strip() for line in f.readlines()]

# إعدادات
chunk_size = 100
sleep_interval = 15
top_momentum_interval = 15 * 60

sent_alerts = set()
momentum_scores = {}

def is_market_open():
    now = datetime.datetime.utcnow()
    weekday = now.weekday()  # Monday=0, Sunday=6
    hour = now.hour
    minute = now.minute

    # US Market open hours (UTC): 13:00 - 20:00 UTC (Regular), with Pre/After ~11:00 - 01:00 UTC
    if weekday >= 5:  # Saturday or Sunday
        return False
    if 10 <= hour <= 23:  # Allow pre-market (from 10 UTC ~ 5-6 AM ET) to after-market
        return True
    return False

def process_chunk(chunk):
    for symbol in chunk:
        try:
            df = yf.download(symbol, period="5d", interval="1m", prepost=True, progress=False)
            if df.empty or len(df) < 16:
                continue

            current_price = df['Close'][-1]
            price_open_today = df[df.index.date == df.index[-1].date()]['Open'][0]
            price_15min_ago = df['Close'][-16]

            daily_change_pct = ((current_price - price_open_today) / price_open_today) * 100
            price_change_15min = ((current_price - price_15min_ago) / price_15min_ago) * 100

            volume_now = df['Volume'][-1]
            avg_volume = df['Volume'][-16:-1].mean()
            volume_ratio = volume_now / avg_volume if avg_volume else 0

            # سيولة — متوسط آخر 5 أيام
            df_daily = yf.download(symbol, period="5d", interval="1d", prepost=True, progress=False)
            if df_daily.empty:
                continue
            avg_liquidity = df_daily['Volume'].mean()
            liquidity_ratio = volume_now / avg_liquidity if avg_liquidity else 0

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

                liquidity_alert = ""
                if liquidity_ratio >= 3:
                    liquidity_alert = (
                        f"\n📢 سيولة استثنائية!\n"
                        f"💰 السيولة الحالية: {int(volume_now):,} سهم\n"
                        f"📊 متوسط 5 أيام: {int(avg_liquidity):,} سهم\n"
                        f"🔥 دخل أكثر من {round(liquidity_ratio, 2)}x من السيولة المعتادة!"
                    )

                message = (
                    f"🚨 زخم مفاجئ على {symbol}\n"
                    f"🚀 دخول الآن بسعر: ${round(current_price, 2)}\n"
                    f"📈 التغير اليومي: {round(daily_change_pct, 2)}٪\n"
                    f"📊 التغير آخر 15 دقيقة: {round(price_change_15min, 2)}٪\n"
                    f"🔥 نسبة الزخم: {round(volume_ratio, 2)}x\n"
                    f"📉 أقل سعر أسبوعي: {week_low}\n"
                    f"📈 أعلى سعر أسبوعي: {week_high}\n"
                    f"{entry_zone}{liquidity_alert}\n"
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
        if is_market_open():
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

        else:
            print("✅ السوق مغلق — لا إرسال.")
            time.sleep(5 * 60)  # Sleep 5 min then check again

def start_bot():
    total_chunks = len(tickers) // chunk_size + 1
    while True:
        if is_market_open():
            for i in range(total_chunks):
                start_idx = i * chunk_size
                end_idx = start_idx + chunk_size
                chunk = tickers[start_idx:end_idx]
                process_chunk(chunk)
                time.sleep(sleep_interval)
        else:
            print("✅ السوق مغلق — في انتظار الافتتاح...")
            time.sleep(5 * 60)

# تشغيل البوت
threading.Thread(target=start_bot).start()
threading.Thread(target=momentum_report).start()
