from fastapi import APIRouter, HTTPException
from app.services.yahoo_finance import fetch_ohlcv, fetch_constituents, fetch_universe_data
from app.core.strategy_base import calculate_metrics

# --- Original 3 ---
from app.strategies.mean_reversion.backtester import MeanReversionBacktester
from app.strategies.rs_momentum.backtester import RSMomentumBacktester
from app.strategies.macd_trend.backtester import MACDTrendBacktester

# --- Batch 2 (5 new) ---
from app.strategies.rsi_extremes.backtester import RSIExtremesBacktester
from app.strategies.bollinger_bands.backtester import BollingerBandsBacktester
from app.strategies.ichimoku.backtester import IchimokuBacktester
from app.strategies.pairs_trading.backtester import PairsTradingBacktester
from app.strategies.triple_ema.backtester import TripleEMABacktester

# --- Final 2 (completing 10) ---
from app.strategies.opening_range_breakout.backtester import OpeningRangeBreakoutBacktester
from app.strategies.volume_momentum.backtester import VolumeMomentumBacktester

import pandas as pd

router = APIRouter()

# ─── Registry ────────────────────────────────────────────────────────────────

BACKTESTERS = {
    "mean_reversion":          MeanReversionBacktester,
    "rs_momentum":             RSMomentumBacktester,
    "macd_trend":              MACDTrendBacktester,
    "rsi_extremes":            RSIExtremesBacktester,
    "bollinger_bands":         BollingerBandsBacktester,
    "ichimoku":                IchimokuBacktester,
    "pairs_trading":           PairsTradingBacktester,
    "triple_ema":              TripleEMABacktester,
    "opening_range_breakout":  OpeningRangeBreakoutBacktester,
    "volume_momentum":         VolumeMomentumBacktester,
}

STRATEGY_META = {
    "mean_reversion":          {"name": "Mean Reversion",           "type": "Mean Reversion",        "description": "Buy yesterday's biggest losers expecting a bounce back."},
    "rs_momentum":             {"name": "RS Momentum",              "type": "Momentum",               "description": "Buy yesterday's top performers riding the trend."},
    "macd_trend":              {"name": "MACD Trend",               "type": "Trend Following",        "description": "EMA crossover-based trend following across the universe."},
    "rsi_extremes":            {"name": "RSI Extremes",             "type": "Mean Reversion",        "description": "Buy oversold stocks (RSI < 30) expecting an oscillator bounce."},
    "bollinger_bands":         {"name": "Bollinger Band Squeeze",   "type": "Volatility Breakout",   "description": "Trade breakouts from low-volatility Bollinger Band compression zones."},
    "ichimoku":                {"name": "Ichimoku Cloud",           "type": "Complex Trend",         "description": "Multi-component Japanese indicator confirming trend with cloud analysis."},
    "pairs_trading":           {"name": "Pairs Trading",            "type": "Statistical Arbitrage", "description": "Exploit mean-reverting spreads between correlated stock pairs."},
    "triple_ema":              {"name": "Triple EMA Ribbon",        "type": "Trend Following",       "description": "Buy stocks aligned EMA8 > EMA21 > EMA55 after a healthy pullback."},
    "opening_range_breakout":  {"name": "Opening Range Breakout",   "type": "Breakout",              "description": "Buy stocks breaking above their rolling recent high with strength."},
    "volume_momentum":         {"name": "Volume-Weighted Momentum", "type": "Momentum",              "description": "Score = price momentum × volume ratio to filter high-conviction moves."},
}


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/strategies")
def list_strategies():
    """Return all 10 strategy IDs with metadata."""
    return [{"id": sid, **meta} for sid, meta in STRATEGY_META.items()]


@router.get("/data/ohlcv")
def get_ohlcv_data(symbol: str, start: str, end: str):
    try:
        df = fetch_ohlcv(symbol, start, end)
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        df = df.reset_index()
        df["Date"] = df["Date"].astype(str)
        return {"symbol": symbol, "data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/run")
def run_backtest(
    strategy_id: str,
    universe: str = "DOW",
    start: str = "2023-01-01",
    end: str = "2024-01-01",
    initial_capital: float = 100000.0
):
    if strategy_id not in BACKTESTERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown strategy. Available: {list(BACKTESTERS.keys())}"
        )

    try:
        # 1. Fetch universe stock prices
        symbols = fetch_constituents(universe)
        data = fetch_universe_data(symbols, start, end)
        if data.empty:
            raise HTTPException(status_code=404, detail="No market data found")

        # 2. Benchmark (DIA = Dow ETF, ^NSEI = Nifty)
        benchmark_symbol = "DIA" if universe == "DOW" else "^NSEI"
        benchmark_raw = fetch_ohlcv(benchmark_symbol, start, end)
        
        # Try to safely get the price column for the benchmark
        price_col = "Adj Close" if "Adj Close" in benchmark_raw.columns else "Close"
        if price_col not in benchmark_raw.columns:
            price_col = benchmark_raw.columns[1] # the first real column after Date
        
        benchmark_equity = (
            benchmark_raw.set_index("Date")[price_col]
            .pct_change().add(1).cumprod().mul(initial_capital)
        )

        # 3. Run dedicated backtester
        backtester = BACKTESTERS[strategy_id](initial_capital=initial_capital)
        equity_curve = backtester.run(data)

        # 4. Performance metrics
        metrics = calculate_metrics(equity_curve)

        import numpy as np
        
        # 5. Chart-ready output
        results = []
        for date, val in equity_curve.items():
            bench_val = benchmark_equity.get(date, None)
            
            # Clean strategy value (NaN/Inf -> None)
            s_val = None if pd.isna(val) or np.isinf(val) else round(float(val), 2)
            
            # Clean benchmark value (NaN/Inf -> None)
            if bench_val is None or pd.isna(bench_val) or np.isinf(bench_val):
                b_val = None
            else:
                b_val = round(float(bench_val), 2)
            
            results.append({
                "date": str(date.date()),
                "strategy": s_val,
                "benchmark": b_val
            })

        return {
            "strategy": strategy_id,
            "strategy_name": STRATEGY_META[strategy_id]["name"],
            "strategy_type": STRATEGY_META[strategy_id]["type"],
            "universe": universe,
            "metrics": metrics,
            "chart_data": results
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
