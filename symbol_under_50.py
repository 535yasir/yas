import pandas as pd
import yfinance as yf
import requests
from io import StringIO
import time

# روابط الأسهم
nasdaq_url = "https://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
other_url  = "https://ftp.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"

def download_symbols():
    print("📥 تحميل رموز السوق ...")
    
    # NASDAQ
    r1 = requests.get(nasdaq_url)
    nasdaq_df = pd.read_csv(StringIO(r1.text), sep="|")
    nasdaq_df = nasdaq_df[nasdaq_df['Test Issue'] == 'N']
    nasdaq_symbols = nasdaq_df['Symbol'].tolist()
    
    # NYSE / AMEX
    r2 = requests.get(other_url)
    other_df = pd.read_csv(StringIO(r2.text), sep="|")
    other_df = other_df[other_df['Test Issue'] == 'N']
    other_symbols = other_df['ACT Symbol'].tolist()
    
    all_symbols = sorted(set(nasdaq_symbols + other_symbols))
    print(f"✅ إجمالي الأسهم: {len(all_symbols)}")

    return all_symbols

def filter_symbols_under_50(symbols):
    print("🔎 جاري فحص الأسعار ... (قد يستغرق بعض الوقت)")
    under_50 = []

    for symbol in symbols:
        try:
            data = yf.download(symbol, period='1d', interval='1d', progress=False)
            if data.empty:
                continue
            latest_price = data['Close'][-1]
            if latest_price <= 50:
                under_50.append(symbol)
            
            # تأخير خفيف لمنع الحظر من ياهو
            time.sleep(0.1)
        
        except Exception as e:
            continue
    
    print(f"✅ عدد الأسهم تحت 50 دولار: {len(under_50)}")

    # حفظها في ملف
    with open("under_50_symbols.txt", "w") as f:
        for sym in under_50:
            f.write(sym + "\n")
    
    print("✅ تم حفظ الملف: under_50_symbols.txt")

# تشغيل السكربت
symbols = download_symbols()
filter_symbols_under_50(symbols)
