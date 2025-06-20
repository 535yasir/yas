import pandas as pd
import requests
from io import StringIO

nasdaq_url = "https://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
other_url  = "https://ftp.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"

def download_clean_symbols():
    print("📥 Downloading NASDAQ...")
    r1 = requests.get(nasdaq_url)
    nasdaq_df = pd.read_csv(StringIO(r1.text), sep="|")
    nasdaq_df = nasdaq_df[nasdaq_df['Test Issue'] == 'N']
    nasdaq_symbols = nasdaq_df['Symbol'].tolist()

    print("📥 Downloading NYSE/AMEX...")
    r2 = requests.get(other_url)
    other_df = pd.read_csv(StringIO(r2.text), sep="|")
    other_df = other_df[other_df['Test Issue'] == 'N']
    other_symbols = other_df['ACT Symbol'].tolist()

    all_symbols = sorted(set(nasdaq_symbols + other_symbols))
    print(f"✅ Found {len(all_symbols)} Common Stocks")

    with open("all_us_stocks.txt", "w") as f:
        for sym in all_symbols:
            f.write(sym + "\n")

    print("✅ Saved to all_us_stocks.txt")

if __name__ == "__main__":
    download_clean_symbols()
