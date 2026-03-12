import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import threading

# Global lock to prevent yfinance multithreading crashes during concurrent UI requests
YF_LOCK = threading.Lock()

# In-memory cache so comparing 4 strategies doesn't download the Nifty 50 4 separate times
UNIVERSE_CACHE = {}
OHLCV_CACHE = {}

SYMBOL_MAP = {
    "NIFTY50": "^NSEI",
    "NIFTY": "^NSEI",
    "SENSEX": "^BSESN",
    "DOW": "^DJI",
}

def fetch_constituents(index_name: str):
    """
    Return a hardcoded list of major NIFTY 50 Indian stocks.
    This bypasses any web scraping errors.
    """
    # Top ~40-50 highly liquid NIFTY 50 stocks
    return [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", 
        "ICICIBANK.NS", "SBI.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
        "LT.NS", "AXISBANK.NS", "BAJFINANCE.NS", "MARUTI.NS", "ASIANPAINT.NS",
        "HCLTECH.NS", "SUNPHARMA.NS", "TITAN.NS", "TATASTEEL.NS", "ULTRACEMCO.NS",
        "WIPRO.NS", "M&M.NS", "NTPC.NS", "NESTLEIND.NS", "POWERGRID.NS",
        "TECHM.NS", "HINDALCO.NS", "ONGC.NS", "JSWSTEEL.NS", "SBILIFE.NS",
        "GRASIM.NS", "DRREDDY.NS", "BRITANNIA.NS", "INDUSINDBK.NS", "BAJAJFINSV.NS",
        "EICHERMOT.NS", "TATAMOTORS.NS", "COALINDIA.NS", "CIPLA.NS", "APOLLOHOSP.NS",
        "DIVISLAB.NS", "TATACONSUM.NS", "HEROMOTOCO.NS", "BAJAJ-AUTO.NS", "BPCL.NS"
    ]

def fetch_ohlcv(symbol: str, start: str, end: str):
    symbol = SYMBOL_MAP.get(symbol.upper(), symbol)
    cache_key = (symbol, start, end)
    
    with YF_LOCK:
        if cache_key in OHLCV_CACHE:
            return OHLCV_CACHE[cache_key].copy()
            
        df = yf.download(symbol, start=start, end=end, progress=False)
        
        if df.empty:
            raise ValueError(f"No market data for {symbol} for given date range")
        
        if isinstance(df.columns, pd.MultiIndex):
            if 'Price' in df.columns.names or len(df.columns.levels) > 1:
                try:
                    df.columns = df.columns.get_level_values(0)
                except:
                    pass
        
        df = df.reset_index()
        if "Date" not in df.columns and "Datetime" in df.columns:
            df.rename(columns={"Datetime": "Date"}, inplace=True)
            
        OHLCV_CACHE[cache_key] = df
        return df.copy()
    if df.empty:
        raise ValueError(f"No market data for {symbol} for given date range")
    
    if isinstance(df.columns, pd.MultiIndex):
        # With newer versions of yfinance, the top level is 'Price' ('Adj Close', etc) 
        # and the second level is the 'Ticker'.
        if 'Price' in df.columns.names or len(df.columns.levels) > 1:
            try:
                df.columns = df.columns.get_level_values(0)
            except:
                pass
    
    df = df.reset_index()
    if "Date" not in df.columns and "Datetime" in df.columns:
        df.rename(columns={"Datetime": "Date"}, inplace=True)
    return df

def fetch_universe_data(symbols: list, start: str, end: str):
    """
    Fetch Adj Close data for a list of symbols and concatenate into a single DataFrame.
    """
    cache_key = (tuple(sorted(symbols)), start, end)
    
    with YF_LOCK:
        if cache_key in UNIVERSE_CACHE:
            return UNIVERSE_CACHE[cache_key].copy()
            
        dataframes = []
        for symbol in symbols:
            try:
                data = yf.download(symbol, start=start, end=end, progress=False)
                if not data.empty:
                    # yfinance returns a MultiIndex if passing a list, but also sometimes for single symbols recently.
                    # If there's a multiindex, flatten it or select 'Adj Close' correctly.
                    try:
                        if isinstance(data.columns, pd.MultiIndex):
                            data = data.xs('Adj Close', level=0, axis=1)
                        else:
                            data = data[['Adj Close']]
                    except:
                        # Fallback if cross-section fails or names are different
                        if 'Adj Close' in data.columns:
                            data = data[['Adj Close']]
                        elif 'Close' in data.columns:
                            data = data[['Close']]
                        else:
                            raise ValueError(f"Could not find price column for {symbol}")
                            
                    data.columns = [symbol]
                    dataframes.append(data)
            except Exception as e:
                print(f"Failed to fetch {symbol}: {e}")
                
        if not dataframes:
            result = pd.DataFrame()
        else:
            result = pd.concat(dataframes, axis=1).ffill()
            
        UNIVERSE_CACHE[cache_key] = result
        return result.copy()

