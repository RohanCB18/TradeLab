import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np

from app.strategies.mean_reversion.backtester import MeanReversionBacktester
from app.strategies.rs_momentum.backtester import RSMomentumBacktester
from app.strategies.macd_trend.backtester import MACDTrendBacktester
from app.strategies.rsi_extremes.backtester import RSIExtremesBacktester
from app.strategies.bollinger_bands.backtester import BollingerBandsBacktester
from app.strategies.ichimoku.backtester import IchimokuBacktester
from app.strategies.pairs_trading.backtester import PairsTradingBacktester
from app.strategies.triple_ema.backtester import TripleEMABacktester
from app.strategies.opening_range_breakout.backtester import OpeningRangeBreakoutBacktester
from app.strategies.volume_momentum.backtester import VolumeMomentumBacktester
from app.core.strategy_base import calculate_metrics

print("=== TradeLab Backend — Full Strategy Test Suite ===\n")

# Synthetic test data
dates = pd.date_range("2023-01-01", periods=150)
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "WMT", "KO"]
np.random.seed(42)
data = pd.DataFrame(
    np.random.randn(150, len(symbols)).cumsum(axis=0) + 150,
    index=dates, columns=symbols
)

ALL_STRATEGIES = [
    ("1. Mean Reversion",          MeanReversionBacktester),
    ("2. RS Momentum",             RSMomentumBacktester),
    ("3. MACD Trend",              MACDTrendBacktester),
    ("4. RSI Extremes",            RSIExtremesBacktester),
    ("5. Bollinger Band Squeeze",  BollingerBandsBacktester),
    ("6. Ichimoku Cloud",          IchimokuBacktester),
    ("7. Pairs Trading",           PairsTradingBacktester),
    ("8. Triple EMA Ribbon",       TripleEMABacktester),
    ("9. Opening Range Breakout",  OpeningRangeBreakoutBacktester),
    ("10. Volume-Weighted Momentum", VolumeMomentumBacktester),
]

all_passed = True
for name, cls in ALL_STRATEGIES:
    try:
        eq = cls(initial_capital=100000).run(data)
        final = eq.dropna().iloc[-1]
        m = calculate_metrics(eq.dropna())
        status = "PASS" if final > 0 else "WARN"
        print(f"  [{status}] {name}")
        print(f"         Final = ${final:>12,.2f} | Sharpe = {m['sharpe_ratio']:>8.4f} | Max DD = {m['max_drawdown']:>7.4f}")
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        all_passed = False

print()
print("=" * 52)
if all_passed:
    print("  ALL 10 STRATEGIES PASSED ✓")
else:
    print("  SOME STRATEGIES FAILED — check above")
print("=" * 52)
