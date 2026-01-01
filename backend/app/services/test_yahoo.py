from app.services.yahoo_finance import fetch_ohlcv

df = fetch_ohlcv("^NSEI", "2023-01-01", "2024-01-01")

print(df.head())
print(df.tail())
