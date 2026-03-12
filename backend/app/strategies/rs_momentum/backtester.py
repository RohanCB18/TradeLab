import pandas as pd
import numpy as np
from app.core.strategy_base import StrategyBase

class RSMomentumBacktester(StrategyBase):
    """
    Dedicated backtester for the Relative Strength Momentum (Biggest Winners) strategy.
    """
    def run(self, data, top_n=10, lookback=20):
        data = self.prepare_data(data)
        
        # Calculate the momentum score (e.g., trailing 20-day percentage return)
        momentum_returns = data.pct_change(periods=lookback)
        
        capital = float(self.initial_capital)
        capital_history = pd.Series(index=data.index, dtype=float)
        
        # We cannot trade during the lookback period because we don't have enough history
        capital_history.iloc[:lookback] = capital
        
        for i in range(lookback, len(data.index) - 1):
            today = data.index[i]
            tomorrow = data.index[i+1]
            
            # Identify the Top N Momentum Leaders today based on their 20-day return
            day_momentum = momentum_returns.iloc[i]
            winners = day_momentum.nlargest(top_n).index
            
            if not winners.empty:
                prices_today = data.loc[today, winners]
                prices_tomorrow = data.loc[tomorrow, winners]
                
                # Filter out zeroes to prevent division errors
                valid = prices_today > 0
                p_today = prices_today[valid]
                p_tomorrow = prices_tomorrow[valid]
                
                if not p_today.empty:
                    # Allocate capital equally among the leaders
                    shares = (capital / len(p_today)) / p_today
                    capital = float(np.sum(shares * p_tomorrow))
            
            capital_history.loc[tomorrow] = capital
            
        return capital_history.ffill()
