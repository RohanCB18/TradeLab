import pandas as pd
import numpy as np
from app.core.strategy_base import StrategyBase

class MACDTrendBacktester(StrategyBase):
    """
    Dedicated backtester for the MACD Trend Following strategy.
    """
    def run(self, data, top_n=10, fast_period=12, slow_period=26, signal_period=9):
        data = self.prepare_data(data)
        
        # Vectorized MACD calculation for all 50 stocks simultaneously
        fast_ema = data.ewm(span=fast_period, adjust=False).mean()
        slow_ema = data.ewm(span=slow_period, adjust=False).mean()
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        capital = float(self.initial_capital)
        capital_history = pd.Series(index=data.index, dtype=float)
        
        # Start trading after the slow period to ensure EMA math has stabilized
        start_idx = slow_period
        capital_history.iloc[:start_idx] = capital
        
        for i in range(start_idx, len(data.index) - 1):
            today = data.index[i]
            tomorrow = data.index[i+1]
            
            # Extract today's MACD and Signal values
            day_macd = macd_line.iloc[i]
            day_signal = signal_line.iloc[i]
            
            # Filter Rule: We ONLY buy stocks in a confirmed uptrend (MACD > Signal)
            bullish_mask = day_macd > day_signal
            bullish_symbols = day_macd[bullish_mask].index
            
            if not bullish_symbols.empty:
                # Rank Rule: Calculate the Momentum Gap (MACD - Signal)
                gap = day_macd[bullish_symbols] - day_signal[bullish_symbols]
                
                # Select the Top 10 strongest momentum trends
                winners = gap.nlargest(top_n).index
                
                prices_today = data.loc[today, winners]
                prices_tomorrow = data.loc[tomorrow, winners]
                
                # Filter valid prices
                valid = prices_today > 0
                p_today = prices_today[valid]
                p_tomorrow = prices_tomorrow[valid]
                
                if not p_today.empty:
                    # Allocate capital equally among the leaders
                    shares = (capital / len(p_today)) / p_today
                    capital = float(np.sum(shares * p_tomorrow))
            
            capital_history.loc[tomorrow] = capital
            
        return capital_history.ffill()
