import pandas as pd
import numpy as np
from app.core.strategy_base import StrategyBase


class OpeningRangeBreakoutBacktester(StrategyBase):
    """
    Opening Range Breakout (ORB) Strategy — Daily Momentum.

    Logic:
    - The "opening range" is defined using the first `range_days` trading days
      of each rolling month as a proxy for a period's high/low.
    - A BREAKOUT LONG signal fires when today's price closes ABOVE the
      rolling high established over the prior `range_days` window.
    - A BREAKOUT SHORT signal fires when today's price closes BELOW the
      rolling low — we avoid these stocks (sit in cash allocation for them).
    - Select the top N stocks with the strongest upward breakout magnitude
      (how far above the range high the close is, as a % of range).
    - Equal weight allocation among selected breakout stocks.
    - This captures momentum continuation after range compression.
    """

    def run(self, data: pd.DataFrame, range_days: int = 5, top_n: int = 10, hold_period: int = 5):
        data = self.prepare_data(data)

        # 1. Define the "Floor" and "Ceiling" of the consolidation range
        # Using the last `range_days` to define the short-term trading box
        rolling_high = data.shift(1).rolling(range_days).max()
        rolling_low = data.shift(1).rolling(range_days).min()

        # 2. Breakout condition: Today's Close explodes ABOVE the Ceiling
        breakout_up = data > rolling_high

        # 3. Magnitude: How aggressive was the breakout? (Distance past ceiling / Height of the box)
        range_size = (rolling_high - rolling_low).replace(0, np.nan)
        breakout_magnitude = (data - rolling_high) / range_size

        capital = float(self.initial_capital)
        capital_history = pd.Series(index=data.index, dtype=float)
        
        start_idx = range_days + 1
        if len(data) <= start_idx:
            capital_history[:] = capital
            return capital_history

        capital_history.iloc[:start_idx] = capital

        # Track active positions and their remaining hold time
        active_holds = {}

        for i in range(start_idx, len(data.index) - 1):
            today = data.index[i]
            tomorrow = data.index[i + 1]

            # Decrement holding period for all active positions
            expired_holds = []
            for stock in active_holds:
                active_holds[stock] -= 1
                if active_holds[stock] <= 0:
                    expired_holds.append(stock)
            
            for stock in expired_holds:
                del active_holds[stock]

            # Find NEW Breakouts today
            is_breakout = breakout_up.iloc[i]
            magnitude_today = breakout_magnitude.iloc[i][is_breakout]
            
            # Rank by violence of the breakout and take top N
            new_symbols = magnitude_today.nlargest(top_n).index
            
            # Add new breakouts to holding dictionary
            for symbol in new_symbols:
                active_holds[symbol] = hold_period

            selected_symbols = list(active_holds.keys())

            if selected_symbols:
                prices_today = data.loc[today, selected_symbols]
                prices_tomorrow = data.loc[tomorrow, selected_symbols]
                
                valid = prices_today > 0
                p_today = prices_today[valid]
                p_tomorrow = prices_tomorrow[valid]

                if not p_today.empty:
                    # Allocate capital equally among all active holds
                    share_val = capital / len(p_today)
                    shares = share_val / p_today
                    capital = float(np.sum(shares * p_tomorrow))

            capital_history.loc[tomorrow] = capital

        return capital_history.ffill()
