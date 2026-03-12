import pandas as pd
import numpy as np
import sys
import os

# Ensure the backend directory is in the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Fixing imports for the new Dedicated architecture
from app.strategies.mean_reversion.backtester import MeanReversionBacktester
from app.core.strategy_base import calculate_metrics

def run_standalone_test():
    print("--- Running Standalone Logic Test (Dedicated Architecture) ---")
    
    # Create fake data for 5 stocks over 10 days
    dates = pd.date_range("2023-01-01", periods=10)
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    data = pd.DataFrame(np.random.randn(10, 5).cumsum(axis=0) + 100, index=dates, columns=symbols)
    
    print("Mock Data Sample:")
    print(data.head())
    
    # Run Dedicated Mean Reversion Backtester
    backtester = MeanReversionBacktester(initial_capital=100000)
    equity_curve = backtester.run(data, top_n=2)
    
    print("\nEquity Curve Sample:")
    print(equity_curve.head())
    
    metrics = calculate_metrics(equity_curve)
    print("\nCalculated Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
    
    if equity_curve.iloc[-1] > 0:
        print("\nDedicated Logic Test PASSED!")
    else:
        print("\nDedicated Logic Test FAILED!")

if __name__ == "__main__":
    run_standalone_test()
