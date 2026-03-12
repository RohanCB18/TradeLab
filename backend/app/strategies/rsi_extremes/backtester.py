import pandas as pd
import numpy as np
from app.core.strategy_base import StrategyBase


class RSIExtremesBacktester(StrategyBase):
    """
    RSI Extremes Strategy — Mean Reversion via Oscillator.

    Logic:
    - Calculate RSI(14) for every stock in the universe daily.
    - Buy stocks where RSI < 30 (oversold) — expecting a bounce.
    - Sell / avoid stocks where RSI > 70 (overbought).
    - Equal weight allocation among all oversold stocks.
    - If no oversold stocks exist that day, hold cash.
    """

    def run(self, data: pd.DataFrame, rsi_period: int = 14, oversold: float = 30.0):
        data = self.prepare_data(data)

        # Vectorized RSI Calculation for all 50 stocks simultaneously
        delta = data.diff()
        
        # Separate gains and losses
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        
        # Calculate Wilder's Smoothing (Exponential Moving Average)
        avg_gain = gain.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
        avg_loss = loss.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi_df = 100 - (100 / (1 + rs))

        capital = float(self.initial_capital)
        capital_history = pd.Series(index=data.index, dtype=float)
        
        # Start trading after the RSI window populates
        start_idx = rsi_period
        capital_history.iloc[:start_idx] = capital

        for i in range(start_idx, len(data.index) - 1):
            today = data.index[i]
            tomorrow = data.index[i + 1]

            # Select stocks mathematically classified as "Oversold" today (RSI < 30)
            rsi_today = rsi_df.iloc[i]
            selected = rsi_today[rsi_today < oversold].index

            if not selected.empty:
                prices_today = data.loc[today, selected]
                prices_tomorrow = data.loc[tomorrow, selected]
                
                # Filter valid prices
                valid = prices_today > 0
                p_today = prices_today[valid]
                p_tomorrow = prices_tomorrow[valid]

                if not p_today.empty:
                    # Allocate capital equally among ALL oversold stocks that day
                    share_val = capital / len(p_today)
                    shares = share_val / p_today
                    capital = float(np.sum(shares * p_tomorrow))

            # If no stocks are oversold today, capital remains untouched (held in cash)
            capital_history.loc[tomorrow] = capital

        return capital_history.ffill()
