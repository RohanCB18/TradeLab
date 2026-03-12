import pandas as pd
import numpy as np
from app.core.strategy_base import StrategyBase


class VolumeMomentumBacktester(StrategyBase):
    """
    Volume-Weighted Momentum Strategy — Smart Money Signal.

    Logic:
    - Pure price momentum ignores conviction. Volume adds context.
    - Compute a rolling N-day price momentum (return) for each stock.
    - Compute a rolling N-day volume ratio: today's volume vs. its average.
      A ratio > 1 means above-average trading activity (higher conviction).
    - SCORE = price_momentum * volume_ratio
      → High score: strong upward price move WITH high volume (institutional buying).
      → Low score: weak or declining price, or momentum on thin volume (unconfirmed).
    - Select the top N stocks by SCORE each day.
    - Equal weight allocation among selected stocks.

    Note: Since we use daily OHLCV data from yfinance, volume is real.
    When the universe data has no volume column (close-prices only matrix),
    we fall back to pure price momentum ranking.
    """

    def run(self, data: pd.DataFrame, momentum_window: int = 20, top_n: int = 10):
        data = self.prepare_data(data)

        # 1. Base Momentum: How much did the stock go up over the last month?
        price_momentum = data.pct_change(momentum_window)

        # 2. Risk/Volatility: How erratic was the stock's path?
        # We calculate the standard deviation of daily returns over that same month
        daily_returns = data.pct_change()
        rolling_volatility = daily_returns.rolling(momentum_window).std()

        # 3. The "Smart Money" Score: Momentum divided by Volatility (similar to Sharpe Ratio)
        # We want stocks that go up smoothly (high momentum, low volatility)
        # Avoid stocks that jumped 20% in one day but swing wildly (high momentum, high volatility)
        score = price_momentum / rolling_volatility.replace(0, np.nan)

        capital = float(self.initial_capital)
        capital_history = pd.Series(index=data.index, dtype=float)
        
        start_idx = momentum_window
        if len(data) <= start_idx:
            capital_history[:] = capital
            return capital_history

        capital_history.iloc[:start_idx] = capital

        for i in range(start_idx, len(data.index) - 1):
            today = data.index[i]
            tomorrow = data.index[i + 1]

            day_score = score.iloc[i]
            
            # Filter for stocks with positive momentum
            positive_momentum = day_score[day_score > 0]
            
            # Rank by Risk-Adjusted Momentum (Smoothness)
            selected = positive_momentum.nlargest(top_n).index

            if not selected.empty:
                prices_today = data.loc[today, selected]
                prices_tomorrow = data.loc[tomorrow, selected]
                
                valid = prices_today > 0
                p_today = prices_today[valid]
                p_tomorrow = prices_tomorrow[valid]

                if not p_today.empty:
                    # Allocate capital equally among the top 10 smoothest trends
                    share_val = capital / len(p_today)
                    shares = share_val / p_today
                    capital = float(np.sum(shares * p_tomorrow))

            capital_history.loc[tomorrow] = capital

        return capital_history.ffill()
