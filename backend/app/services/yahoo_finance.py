import yfinance as yf
import pandas as pd

SYMBOL_MAP = {
    "NIFTY50": "^NSEI",
    "NIFTY": "^NSEI",
    "SENSEX": "^BSESN",
}

def fetch_ohlcv(symbol: str, start: str, end: str):
    symbol = SYMBOL_MAP.get(symbol.upper(), symbol)

    df = yf.download(symbol, start=start, end=end)

    if df.empty:
        raise ValueError("No market data for given date range")

    # Handle MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Normalize index name safely
    df = df.reset_index()
    if "Date" not in df.columns and "Datetime" in df.columns:
        df.rename(columns={"Datetime": "Date"}, inplace=True)

    return df

