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

    def _find_top_pairs(self, data: pd.DataFrame, n_pairs: int = 5, lookback: int = 60):
        """Find the most correlated pairs using the first 'lookback' days."""
        early_data = data.iloc[:lookback]
        log_prices = np.log(early_data.replace(0, np.nan).dropna(axis=1))
        corr_matrix = log_prices.corr()

        pairs = []
        for a, b in combinations(corr_matrix.columns, 2):
            pairs.append((a, b, corr_matrix.loc[a, b]))

        pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        return [(a, b) for a, b, _ in pairs[:n_pairs]]

    def run(self, data: pd.DataFrame, n_pairs: int = 5, z_entry: float = 2.0,
            spread_window: int = 20, lookback: int = 60):
        data = self.prepare_data(data)

        if len(data) < lookback + spread_window + 5:
            return pd.Series(self.initial_capital, index=data.index, dtype=float)

        top_pairs = self._find_top_pairs(data, n_pairs=n_pairs, lookback=lookback)

        capital = float(self.initial_capital)
        capital_history = pd.Series(index=data.index, dtype=float)
        capital_history.iloc[0] = capital

        if not top_pairs:
            return capital_history.fillna(capital)

        capital_per_pair = capital / len(top_pairs)

        # Run simulation for each pair independently, sum results
        pair_capitals = {pair: capital_per_pair for pair in top_pairs}

        for i in range(lookback + spread_window, len(data.index) - 1):
            today = data.index[i]
            tomorrow = data.index[i + 1]

            total = 0.0
            for (sym_a, sym_b) in top_pairs:
                pair_cap = pair_capitals[(sym_a, sym_b)]

                price_a = data[sym_a].iloc[i - spread_window:i + 1]
                price_b = data[sym_b].iloc[i - spread_window:i + 1]

                if price_a.min() <= 0 or price_b.min() <= 0:
                    total += pair_cap
                    continue

                spread = np.log(price_a) - np.log(price_b)
                spread_mean = spread.mean()
                spread_std = spread.std()

                if spread_std == 0:
                    total += pair_cap
                    continue

                z = (spread.iloc[-1] - spread_mean) / spread_std

                pa_today = data.loc[today, sym_a]
                pb_today = data.loc[today, sym_b]
                pa_tomorrow = data.loc[tomorrow, sym_a]
                pb_tomorrow = data.loc[tomorrow, sym_b]

                half = pair_cap / 2

                if z < -z_entry:
                    # Long A, Short B (spread will widen back up)
                    shares_a = half / pa_today
                    shares_b = half / pb_today
                    pair_cap = float(shares_a * pa_tomorrow - shares_b * pb_tomorrow + half)

                elif z > z_entry:
                    # Short A, Long B
                    shares_a = half / pa_today
                    shares_b = half / pb_today
                    pair_cap = float(-shares_a * pa_tomorrow + shares_b * pb_tomorrow + half)

                pair_capitals[(sym_a, sym_b)] = max(pair_cap, 0.01)
                total += pair_capitals[(sym_a, sym_b)]

            capital = total
            capital_history.loc[tomorrow] = capital

        return capital_history.ffill()
