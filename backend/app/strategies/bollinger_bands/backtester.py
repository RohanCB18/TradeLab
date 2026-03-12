import pandas as pd
import numpy as np
from app.core.strategy_base import StrategyBase


class BollingerBandsBacktester(StrategyBase):
    """
    Bollinger Band Squeeze Strategy — Volatility Breakout.

    Logic:
    - Compute 20-day Bollinger Bands (SMA ± 2 * std) for each symbol.
    - Detect a "squeeze": when bandwidth (upper - lower) / middle is at a
      20-day low, indicating compressed volatility about to expand.
    - Buy stocks exiting the squeeze upward (price crosses above upper band).
    - Hold until price reverts to the middle band (SMA), then exit.
    - Equal allocation among selected breakout stocks.
    """

    def run(self, data: pd.DataFrame, window: int = 20, num_std: float = 2.0, hold_period: int = 5):
        data = self.prepare_data(data)

        # 1. Compute Bollinger Bands (SMA, Upper, Lower) for all 50 stocks
        sma = data.rolling(window).mean()
        std = data.rolling(window).std()
        upper = sma + num_std * std
        lower = sma - num_std * std
        
        # 2. Compute Bandwidth (Volatility Compression)
        bandwidth = (upper - lower) / sma.replace(0, np.nan)
        
        # 3. Detect the "Squeeze" -> Bandwidth is at a 20-day low
        is_squeeze = bandwidth == bandwidth.rolling(window).min()
        
        # 4. Detect the "Breakout" -> Price closes ABOVE the Upper Band
        # AND yesterday was in a Squeeze (compressed volatility released upwards)
        breakout_up = (data > upper) & is_squeeze.shift(1).fillna(False)

        capital = float(self.initial_capital)
        capital_history = pd.Series(index=data.index, dtype=float)
        
        start_idx = window
        capital_history.iloc[:start_idx] = capital

        # Dictionary to track stocks we are actively holding and how many days left
        # Format: { 'RELIANCE.NS': 3 } -> Holding Reliance for 3 more days
        active_holds = {}

        for i in range(start_idx, len(data.index) - 1):
            today = data.index[i]
            tomorrow = data.index[i + 1]

            # Decrement holding period for all active positions
            # Remove positions that have reached 0 days remaining
            expired_holds = []
            for stock in active_holds:
                active_holds[stock] -= 1
                if active_holds[stock] <= 0:
                    expired_holds.append(stock)
            
            for stock in expired_holds:
                del active_holds[stock]

            # Find NEW Breakouts today
            today_breakouts = breakout_up.iloc[i]
            new_symbols = today_breakouts[today_breakouts].index
            
            # Add new breakouts to our holding dictionary with the full holding period
            for symbol in new_symbols:
                active_holds[symbol] = hold_period
                
            # Combine new and existing holds to get today's active portfolio
            selected_symbols = list(active_holds.keys())

            if selected_symbols:
                prices_today = data.loc[today, selected_symbols]
                prices_tomorrow = data.loc[tomorrow, selected_symbols]
                
                valid = prices_today > 0
                p_today = prices_today[valid]
                p_tomorrow = prices_tomorrow[valid]

                if not p_today.empty:
                    # Allocate capital equally among all active breakout holds
                    share_val = capital / len(p_today)
                    shares = share_val / p_today
                    capital = float(np.sum(shares * p_tomorrow))

            capital_history.loc[tomorrow] = capital

        return capital_history.ffill()
