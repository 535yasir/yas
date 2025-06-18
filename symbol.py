import pandas as pd
import requests
from io import StringIO

# روابط الملفات الرسمية من Nasdaq Trader
nasdaq_url = "https://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
other_url  = "https://ftp.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"

def download_clean_symbols():
    # Download NASDAQ
    print("📥 Downloading NASDAQ...")
    r1 = requests.get(nasdaq_url)
    nasdaq_df = pd.read_csv(StringIO(r1.text), sep="|")
    nasdaq_df = nasdaq_df[nasdaq_df['Test Issue'] == 'N']  # Exclude test issues
    nasdaq_symbols = nasdaq_df['Symbol'].tolist()

    # Download NYSE / AMEX
    print("📥 Downloading NYSE/AMEX...")
    r2 = requests.get(other_url)
    other_df = pd.read_csv(StringIO(r2.text), sep="|")
    other_df = other_df[other_df['Test Issue'] == 'N']  # Exclude test issues
    other_symbols = other_df['ACT Symbol'].tolist()

    # Combine
    all_symbols = sorted(set(nasdaq_symbols + other_symbols))

    print(f"✅ Found {len(all_symbols)} Common Stocks")

    # Save to file
    with open("all_us_stocks.txt", "w") as f:
        for sym in all_symbols:
            f.write(sym + "\n")

    print("✅ Saved to all_us_stocks.txt")

# Run it
download_clean_symbols()
