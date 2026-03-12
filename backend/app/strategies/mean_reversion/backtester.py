import pandas as pd
import numpy as np
from app.core.strategy_base import StrategyBase

class MeanReversionBacktester(StrategyBase):
    """
    Dedicated backtester for the Mean Reversion (Biggest Losers) strategy.
    """
    def run(self, data, top_n=10):
        # 1. Prepare data and calculate daily returns
        data = self.prepare_data(data)
        daily_returns = data.pct_change()
        
        capital = self.initial_capital
        capital_history = pd.Series(index=data.index, dtype=float)
        capital_history.iloc[0] = capital
        
        # 2. Simulation Loop
        for i in range(len(data.index) - 1):
            today = data.index[i]
            tomorrow = data.index[i+1]
            
            # JetBrains Strategy Logic: Buy the 10 biggest losers at the close today, sell tomorrow.
            day_returns = daily_returns.iloc[i]
            losers = day_returns.nsmallest(top_n).index
            
            if not losers.empty:
                # Get the closing prices for these stocks on the current and next trading days
                prices_today = data.loc[today, losers]
                prices_tomorrow = data.loc[tomorrow, losers]
                
                # Filter valid prices (prevent division by zero or negative prices)
                valid = prices_today > 0
                p_today = prices_today[valid]
                p_tomorrow = prices_tomorrow[valid]
                
                if not p_today.empty:
                    # Distribute our capital equally among these stocks and buy shares
                    shares = (capital / len(p_today)) / p_today
                    
                    # The next day, sell all shares at the closing price and update our capital
                    capital = float(np.sum(shares * p_tomorrow))
            
            capital_history.loc[tomorrow] = capital
            
        return capital_history.ffill()
