import pandas as pd
import numpy as np
from app.core.strategy_base import StrategyBase
from itertools import combinations


class PairsTradingBacktester(StrategyBase):
    """
    Pairs Trading Strategy — Statistical Arbitrage.

    Logic:
    - Find the top correlated pairs in the universe (e.g., HDFC vs ICICI).
    - Compute the spread = log(price_A) - log(price_B).
    - Calculate a rolling z-score of the spread.
    - LONG the spread (buy A, short B) when z-score < -2 (spread too low).
    - SHORT the spread (sell A, buy B) when z-score > +2 (spread too high).
    - The bet: the spread will revert to its mean.
    - Each pair is allocated an equal share of total capital.
    """

    def run(self, data: pd.DataFrame, z_entry: float = 2.0, z_exit: float = 0.5,
            spread_window: int = 20):
        data = self.prepare_data(data)

        # 1. Define Fundamentally Correlated "Sister" Companies
        pairs = [
            ("HDFCBANK.NS", "ICICIBANK.NS"),     # Private Banks
            ("TCS.NS", "INFY.NS"),               # IT Services
            ("RELIANCE.NS", "ONGC.NS"),          # Energy / Oil
            ("TATAMOTORS.NS", "M&M.NS"),         # Auto Manufacturing
            ("SUNPHARMA.NS", "CIPLA.NS")         # Pharmaceuticals
        ]

        # Calculate daily percentage returns for all stocks
        daily_returns = data.pct_change()

        pair_returns = {}

        # 2. Vectorized Math for each Pair (No Iteration over Days)
        for sym_a, sym_b in pairs:
            if sym_a not in data.columns or sym_b not in data.columns:
                # If a stock is missing from the data, this pair sits in cash (0% return)
                pair_returns[f"{sym_a}_{sym_b}"] = pd.Series(0.0, index=data.index)
                continue

            price_a = data[sym_a]
            price_b = data[sym_b]
            
            ret_a = daily_returns[sym_a]
            ret_b = daily_returns[sym_b]

            # The Spread: Distance between the two log prices
            spread = np.log(price_a) - np.log(price_b)
            
            # 20-Day Rolling Mean and Standard Dev
            spread_mean = spread.rolling(window=spread_window).mean()
            spread_std = spread.rolling(window=spread_window).std()

            # Z-Score: How many Standard Deviations away from the mean is the spread today?
            z_score = (spread - spread_mean) / spread_std.replace(0, np.nan)

            # --- Target Position Logic ---
            # 1 = Long A, Short B (Because A is unusually cheap compared to B)
            # -1 = Short A, Long B (Because A is unusually expensive compared to B)
            # 0 = Cash (Spread has returned to normal)
            
            position = pd.Series(np.nan, index=data.index)
            
            # Entry Conditions
            position[z_score < -z_entry] = 1.0
            position[z_score > z_entry] = -1.0
            
            # Exit Conditions (When Z-score crosses back near 0)
            position[(z_score > -z_exit) & (z_score < z_exit)] = 0.0
            
            # Forward fill the positions (Hold trade until exit condition met)
            position = position.ffill().fillna(0.0)
            
            # Shift by 1 to prevent lookahead bias (We calculate today, trade tomorrow)
            position = position.shift(1).fillna(0.0)

            # --- Calculate Daily Return for this specific pair ---
            # If position = 1: Apply +50% weight to A's return, -50% weight to B's return
            # If position = -1: Apply -50% weight to A's return, +50% weight to B's return
            pnl = position * (0.5 * ret_a - 0.5 * ret_b)
            
            pair_returns[f"{sym_a}_{sym_b}"] = pnl.fillna(0.0)

        # 3. Combine the 5 pairs into a single Portfolio
        # Total portfolio return is the average of the 5 independent pair returns
        portfolio_daily_returns = pd.DataFrame(pair_returns).mean(axis=1)

        # 4. Compounding Capital
        capital_history = float(self.initial_capital) * (1 + portfolio_daily_returns).cumprod()

        return capital_history
