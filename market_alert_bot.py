import yfinance as yf
import telebot
import pandas as pd
import time
import schedule
from datetime import datetime

# إعدادات البوت
TELEGRAM_TOKEN = '8151824172:AAFUxxjqtxk3wt_um-U9FWW7JSQjopSI8hg'
CHAT_ID = '6500755943'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# قائمة الأسهم
with open("all_us_stocks.txt", "r") as f:
    symbols = [line.strip() for line in f if line.strip()]

# معلمات الزخم
volume_ratio_threshold = 3.0
price_change_pct_threshold = 5.0

# سجل الإشعارات المرسلة
sent_alerts = set()

# دالة فحص سهم واحد
def check_stock(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="5m", prepost=True, progress=False)
        if df.empty or len(df) < 5:
            return None
        
        current_price = df['Close'].iloc[-1]
        price_15min_ago = df['Close'].iloc[-4]
        price_change_pct = ((current_price - price_15min_ago) / price_15min_ago) * 100

        volume_now = df['Volume'].iloc[-1]
        avg_volume_5d = df['Volume'].mean()
        volume_ratio = volume_now / avg_volume_5d if avg_volume_5d > 0 else 0

        stock_week = yf.Ticker(symbol).history(period="1wk", interval="1d")
        week_low = round(stock_week['Low'].min(), 2)
        week_high = round(stock_week['High'].max(), 2)

        alert_text = ""

        if price_change_pct >= price_change_pct_threshold or volume_ratio >= volume_ratio_threshold or current_price >= week_high or current_price <= week_low:
            alert_text = (
                f"🚀 تنبيه زخم للسهم: {symbol}\n"
                f"📈 السعر الحالي: {current_price:.2f}\n"
                f"📊 نسبة التغير 15 دقيقة: {price_change_pct:.2f}%\n"
                f"💰 حجم التداول الحالي: {volume_now}\n"
                f"📊 معدل السيولة 5 أيام: {avg_volume_5d:.0f} (x{volume_ratio:.1f})\n"
                f"📉 أدنى أسبوع: {week_low} — 📈 أعلى أسبوع: {week_high}\n"
                f"⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
            )
        
        return alert_text if alert_text else None

    except Exception as e:
        print(f"[Error] {symbol} — {e}")
        return None

# دالة المسح
def run_scan():
    bot.send_message(CHAT_ID, f"📡 بدء مسح السوق... ({len(symbols)} أسهم) ⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    alerts = []

    for symbol in symbols:
        if symbol in sent_alerts:
            continue
        alert = check_stock(symbol)
        if alert:
            alerts.append(alert)
            sent_alerts.add(symbol)
            bot.send_message(CHAT_ID, alert)
        
        time.sleep(0.2)  # لمنع الضغط على API

    if not alerts:
        print(f"[{datetime.utcnow()}] No strong alerts this cycle.")
    else:
        print(f"[{datetime.utcnow()}] Sent {len(alerts)} alerts.")

# جدول الإرسال (كل 15 دقيقة)
schedule.every(15).minutes.do(run_scan)

# عند بدء التشغيل
bot.send_message(CHAT_ID, "🚀 تم تشغيل البوت ✅ — جاري مراقبة السوق (After + Pre + Regular Market)\nسيتم إرسال التنبيهات 🔔 كل 15 دقيقة.")

# حلقة تشغيل مستمرة
while True:
    schedule.run_pending()
    time.sleep(1)
