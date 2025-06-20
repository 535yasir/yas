import telebot
import requests
import time
from datetime import datetime

# استبدال هذه القيم بمعلوماتك
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"  # يمكن الحصول عليه من @userinfobot
TRADINGVIEW_API_KEY = "YOUR_TRADINGVIEW_API_KEY"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# دالة لجلب بيانات السهم من TradingView
def get_stock_data(symbol):
    url = f"https://api.tradingview.com/v1/symbols/{symbol}/quotes"
    headers = {"Authorization": f"Bearer {TRADINGVIEW_API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

# دالة لإرسال التنبيهات
def send_alert(symbol, price, change, alert_type):
    message = f"📊 **تنبيه سوق الأسهم**\n"
    message += f"🔄 **السهم:** {symbol}\n"
    message += f"💰 **السعر:** ${price}\n"
    message += f"📈 **التغيير:** {change}%\n"
    message += f"🚀 **النوع:** {'صعودي 🟢' if alert_type == 'bullish' else 'هبوطي 🔴'}\n"
    message += f"⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    bot.send_message(TELEGRAM_CHAT_ID, message, parse_mode="Markdown")

# دالة المراقبة المستمرة للأسهم
def monitor_stocks():
    stocks = ["AAPL", "TSLA", "AMZN", "MSFT"]  # الأسهم المراقبة
    
    for stock in stocks:
        data = get_stock_data(stock)
        if data:
            price = data["last"]
            change = data["change_percent"]
            
            if change >= 2:  # تنبيه عند صعود 2%
                send_alert(stock, price, change, "bullish")
            elif change <= -2:  # تنبيه عند هبوط 2%
                send_alert(stock, price, change, "bearish")

# تشغيل البوت
if __name__ == "__main__":
    while True:
        monitor_stocks()
        time.sleep(300)  # يتحقق كل 5 دقائق
