from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)

# تحميل المتغيرات البيئية
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')

@app.route('/webhook', methods=['POST'])
def webhook():
    # التحقق من الأمان
    if request.headers.get('X-SECRET') != WEBHOOK_SECRET:
        return "Unauthorized", 401
    
    try:
        data = request.json
        ticker = data.get('ticker', 'N/A')
        price = data.get('price', 'N/A')
        change = data.get('change', 'N/A')
        volume = data.get('volume', 'N/A')
        reason = data.get('reason', 'تغيير غير طبيعي')
        
        # بناء الرسالة
        message = (
            f"🚨 **تنبيه سوقي**: {ticker}\n"
            f"▫️ **السعر**: ${price}\n"
            f"▫️ **التغير**: {change}%\n"
            f"▫️ **الحجم**: {volume}\n"
            f"▫️ **السبب**: {reason}\n"
            f"#تنبيهات_الأسهم"
        )
        
        # إرسال إلى تلجرام
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(telegram_url, json=payload)
        
        return "OK", 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
