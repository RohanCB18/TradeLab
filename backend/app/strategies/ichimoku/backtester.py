import pandas as pd
import numpy as np
from app.core.strategy_base import StrategyBase


class IchimokuBacktester(StrategyBase):
    """
    Ichimoku Kinko Hyo Strategy — Multi-Dimensional Trend.

    Logic (simplified for cross-sectional universe):
    - Compute Tenkan-sen (9-period midpoint) and Kijun-sen (26-period midpoint).
    - Compute Senkou Span A and B to form the Kumo (cloud).
    - BUY signal: Tenkan > Kijun AND price > Kumo (above cloud = bullish).
    - SELL signal: Tenkan < Kijun OR price drops below cloud.
    - Select the top N stocks with the strongest bullish Ichimoku confirmation.
    - Equal weight allocation among selected stocks.
    """

    def run(self, data: pd.DataFrame, top_n: int = 10):
        data = self.prepare_data(data)

        # 1. Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
        tenkan = (data.rolling(9).max() + data.rolling(9).min()) / 2
        
        # 2. Kijun-sen (Base Line): (26-period high + 26-period low) / 2
        kijun = (data.rolling(26).max() + data.rolling(26).min()) / 2
        
        # 3. Senkou Span A (Leading Span A): (Tenkan + Kijun) / 2, projected 26 periods ahead
        # Note: In backtesting, we just shift it forward by 26 days to align it with today's price
        senkou_a = ((tenkan + kijun) / 2).shift(26)
        
        # 4. Senkou Span B (Leading Span B): (52-period high + 52-period low) / 2, projected 26 periods ahead
        senkou_b = ((data.rolling(52).max() + data.rolling(52).min()) / 2).shift(26)

        # 5. Bullish Confirmation Rules:
        # - Rule A: Tenkan must be above Kijun (Short term momentum > Medium term)
        # - Rule B: Price must be ABOVE the entire Kumo Cloud (Senkou A and Senkou B)
        # - (Chikou Span is omitted for vectorization performance as it's a lagging confirmation indicator)
        
        is_bullish = (tenkan > kijun) & (data > senkou_a) & (data > senkou_b)

        # Rank by Conviction: Distance between Tenkan and Kijun
        crossover_strength = tenkan - kijun

        capital = float(self.initial_capital)
        capital_history = pd.Series(index=data.index, dtype=float)
        
        # Start trading after the cloud has fully formed (52 days of history + 26 days of shift = 78 days)
        # To be safe and maximize data, we'll start at 78
        start_idx = 78
        if len(data) <= start_idx:
            capital_history[:] = capital
            return capital_history

        capital_history.iloc[:start_idx] = capital

        for i in range(start_idx, len(data.index) - 1):
            today = data.index[i]
            tomorrow = data.index[i + 1]

            # Select stocks that mathematically confirm all Bullish Ichimoku rules today
            bullish_today = is_bullish.iloc[i]
            strength_today = crossover_strength.iloc[i]
            
            # Filter and rank the Top N strongest trends
            eligible = strength_today[bullish_today].nlargest(top_n).index

            if not eligible.empty:
                prices_today = data.loc[today, eligible]
                prices_tomorrow = data.loc[tomorrow, eligible]
                
                valid = prices_today > 0
                p_today = prices_today[valid]
                p_tomorrow = prices_tomorrow[valid]

                if not p_today.empty:
                    # Allocate capital equally among the top Ichimoku trends
                    share_val = capital / len(p_today)
                    shares = share_val / p_today
                    capital = float(np.sum(shares * p_tomorrow))

            capital_history.loc[tomorrow] = capital

        return capital_history.ffill()
