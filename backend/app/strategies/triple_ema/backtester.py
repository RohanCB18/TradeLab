import pandas as pd
import numpy as np
from app.core.strategy_base import StrategyBase


class TripleEMABacktester(StrategyBase):
    """
    Triple EMA Ribbon Strategy — Trend Following via Smoothing.

    Logic:
    - Compute 3 EMAs per stock: fast (8), medium (21), slow (55).
    - "Perfect Bullish Alignment": EMA8 > EMA21 > EMA55 (strong uptrend).
    - "Pullback Entry": price dips below EMA8 but stays above EMA21.
    - BUY stocks in perfect alignment where a pullback to EMA21 was just seen.
    - This captures high-probability trend continuation after a healthy retest.
    - Rank by (EMA8 - EMA55) / EMA55 to find the strongest trends.
    - Equal weight allocation among top N selected stocks.
    """

    def run(self, data: pd.DataFrame, fast: int = 8, med: int = 21, slow: int = 55, top_n: int = 10):
        data = self.prepare_data(data)

        # 1. Compute 3 EMAs
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_med = data.ewm(span=med, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()

        # 2. Perfect bullish alignment
        aligned = (ema_fast > ema_med) & (ema_med > ema_slow)

        # 3. Pullback logic: Yesterday closed below EMA8 (testing support), Today closed above EMA8 (bouncing)
        pullback_bounce = (data.shift(1) < ema_fast.shift(1)) & (data.shift(1) > ema_med.shift(1)) & (data > ema_fast)

        # 4. Base Score: Conviction of the trend (Distance between Fast and Slow)
        trend_strength = (ema_fast - ema_slow) / ema_slow.replace(0, np.nan)

        capital = float(self.initial_capital)
        capital_history = pd.Series(index=data.index, dtype=float)
        
        # EMA55 requires 55 days to fully stabilize
        start_idx = slow
        if len(data) <= start_idx:
            capital_history[:] = capital
            return capital_history

        capital_history.iloc[:start_idx] = capital

        for i in range(start_idx, len(data.index) - 1):
            today = data.index[i]
            tomorrow = data.index[i + 1]

            is_aligned = aligned.iloc[i]
            is_bouncing = pullback_bounce.iloc[i]
            strength = trend_strength.iloc[i]

            # Only consider stocks in a perfectly aligned uptrend
            eligible = strength[is_aligned]
            
            # Prioritize stocks that are actively bouncing off a pullback today
            # We give them an artificial "boost" so they jump to the top of the #10 Rankings
            bounce_boost = is_bouncing[is_aligned].astype(float) * 100.0 
            eligible = eligible + bounce_boost

            selected = eligible.nlargest(top_n).index

            if not selected.empty:
                prices_today = data.loc[today, selected]
                prices_tomorrow = data.loc[tomorrow, selected]
                
                valid = prices_today > 0
                p_today = prices_today[valid]
                p_tomorrow = prices_tomorrow[valid]

                if not p_today.empty:
                    # Allocate capital equally among the Top 10 EMA trends
                    share_val = capital / len(p_today)
                    shares = share_val / p_today
                    capital = float(np.sum(shares * p_tomorrow))

            capital_history.loc[tomorrow] = capital

        return capital_history.ffill()
