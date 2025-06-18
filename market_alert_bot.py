import yfinance as yf
import telebot
import time
import threading
import pandas as pd

# إعدادات البوت
TELEGRAM_TOKEN = 'ضع_التوكن_هنا'  # من @BotFather
CHAT_ID = 'ضع_معرف_الدردشة_هنا'    # من @userinfobot أو قناة تيليجرام

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 🔥 رسالة تأكيد بدء التشغيل
bot.send_message(CHAT_ID, "🚀 تم تشغيل البوت بنجاح! يتم الآن مراقبة السوق الأمريكي.")

# قائمة الأسهم
tickers = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA", "PEP", "ADBE", "COST",
    "CSCO", "AVGO", "TXN", "INTC", "QCOM", "AMGN", "HON", "SBUX", "AMD", "ISRG",
    "BKNG", "MDLZ", "ADI", "GILD", "REGN", "VRTX", "ZM", "KDP", "ROST", "MNST",
    "CDNS", "MAR", "FTNT", "CTSH", "WDAY", "EXC", "BIIB", "PCAR", "CHTR", "DLTR",
    "PAYX", "XEL", "EBAY", "ANSS", "LRCX", "MCHP", "TEAM", "ORLY", "KLAC", "FAST",
    "BRK.B", "JNJ", "V", "JPM", "UNH", "MA", "HD", "PG", "XOM", "LLY", "ABBV", "BAC",
    "MRK", "PFE", "KO", "TMO", "CVX", "ABT", "WMT", "DIS", "NFLX", "CRM", "T", "BA",
    "NKE", "GE", "INTU", "DHR", "LOW", "MDT", "AMAT", "GS", "NOW", "NEE", "PLD",
    "ADP", "AXP", "SPGI", "TJX", "BLK", "EL", "USB", "ZTS", "SO", "PGR", "MO",
    "F", "GM", "C", "COF", "MS", "ETN", "ADSK", "MRNA", "SHOP", "SNOW", "PLTR",
    "UBER", "LYFT", "RIVN", "LCID", "BIDU", "BABA", "JD", "NTES", "PDD", "TCEHY",
    "DOCU", "ROKU", "SPOT", "TWLO", "SQ", "AFRM", "DKNG", "PINS", "TTD", "ETSY",
    "ASML", "TSM", "NVAX", "COIN", "HOOD", "CRWD", "ZS", "NET", "PANW", "DDOG",
    "OKTA", "FSLY", "FUBO", "SOFI", "WBD", "PARA"
]

sent_alerts = set()

def check_stocks():
    while True:
        for symbol in tickers:
            try:
                df = yf.download(symbol, period="1d", interval="5m", progress=False)
                if df.empty or len(df) < 4:
                    continue

                current_price = df['Close'][-1]
                price_15min_ago = df['Close'][-4]
                price_change_pct = ((current_price - price_15min_ago) / price_15min_ago) * 100

                volume_now = df['Volume'][-1]
                avg_volume = df['Volume'][-4:-1].mean()
                volume_ratio = volume_now / avg_volume if avg_volume else 0

                stock_week = yf.Ticker(symbol).history(period="1wk", interval="1d")
                if stock_week.empty:
                    continue

                week_low = round(stock_week['Low'].min(), 2)
                week_high = round(stock_week['High'].max(), 2)

                if (price_change_pct >= 3 or volume_ratio >= 2) and symbol not in sent_alerts:
                    message = (
                        f"🚨 تنبيه زخم مفاجئ على {symbol}\n"
                        f"🔼 السعر الحالي: {round(current_price, 2)}\n"
                        f"📈 التغير خلال 15 دقيقة: {round(price_change_pct, 2)}٪\n"
                        f"🔥 نسبة الزخم (فوليوم): {round(volume_ratio, 2)}x\n"
                        f"📉 أقل سعر أسبوعي: {week_low}\n"
                        f"📈 أعلى سعر أسبوعي: {week_high}"
                    )
                    bot.send_message(CHAT_ID, message)
                    sent_alerts.add(symbol)

            except Exception as e:
                print(f"خطأ في {symbol}: {e}")

        time.sleep(60)  # تحديث كل دقيقة

# تشغيل المراقبة في الخلفية
threading.Thread(target=check_stocks).start()
