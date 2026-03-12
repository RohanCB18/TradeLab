import pandas as pd
import numpy as np

def calculate_metrics(capital_series):
    """
    Standardized performance metric calculation for all strategies.
    """
    if capital_series.empty:
        return {}
        
    returns = capital_series.pct_change().dropna()
    
    # Annualized Return
    total_return = float((capital_series.iloc[-1] / capital_series.iloc[0]) - 1)
    days = (capital_series.index[-1] - capital_series.index[0]).days
    annualized_return = float((1 + total_return)**(365/max(days, 1)) - 1)
        
    # Volatility
    annualized_vol = float(returns.std() * np.sqrt(252))
    
    # Sharpe Ratio
    sharpe_ratio = float(annualized_return / annualized_vol) if annualized_vol != 0 else 0.0
    
    # Max Drawdown
    rolling_max = capital_series.cummax()
    drawdown = (capital_series / rolling_max) - 1
    max_drawdown = float(drawdown.min())
    
    return {
        "total_return": round(total_return, 4),
        "annualized_return": round(annualized_return, 4),
        "annualized_volatility": round(annualized_vol, 4),
        "sharpe_ratio": round(sharpe_ratio, 4),
        "max_drawdown": round(max_drawdown, 4)
    }

class StrategyBase:
    """
    Base class providing common utilities for dedicated strategy backtesters.
    """
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
    
    def prepare_data(self, data):
        """Common data preparation logic. Drops impossible anomalous prices (e.g. unadjusted splits)."""
        df = data.ffill().dropna(how='all')
        
        # Calculate daily percentage returns
        returns = df.pct_change()
        
        # Mask out physically impossible single-day returns for large caps (e.g., > 50% or < -50%)
        # These are almost always unadjusted stock splits or YF data glitches.
        glitch_mask = (returns > 0.50) | (returns < -0.50)
        
        # Replace glitch prices with NaN, then forward fill the last known good price
        df[glitch_mask] = np.nan
        return df.ffill()
