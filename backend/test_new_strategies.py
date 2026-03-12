import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np

from app.strategies.rsi_extremes.backtester import RSIExtremesBacktester
from app.strategies.bollinger_bands.backtester import BollingerBandsBacktester
from app.strategies.ichimoku.backtester import IchimokuBacktester
from app.strategies.pairs_trading.backtester import PairsTradingBacktester
from app.strategies.triple_ema.backtester import TripleEMABacktester
from app.core.strategy_base import calculate_metrics

print("Imports OK - running quick test...")

dates = pd.date_range("2023-01-01", periods=120)
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM"]
np.random.seed(42)
data = pd.DataFrame(
    np.random.randn(120, len(symbols)).cumsum(axis=0) + 150,
    index=dates, columns=symbols
)

strategies = [
    ("RSI Extremes",       RSIExtremesBacktester),
    ("Bollinger Bands",    BollingerBandsBacktester),
    ("Ichimoku Cloud",     IchimokuBacktester),
    ("Pairs Trading",      PairsTradingBacktester),
    ("Triple EMA Ribbon",  TripleEMABacktester),
]

for name, cls in strategies:
    eq = cls(initial_capital=100000).run(data)
    final = eq.dropna().iloc[-1]
    m = calculate_metrics(eq.dropna())
    print(f"  {name}: Final = ${final:,.2f} | Sharpe = {m['sharpe_ratio']:.4f}")

print("\nAll 5 new strategies PASSED!")
