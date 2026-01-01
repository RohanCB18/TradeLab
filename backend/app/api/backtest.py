from fastapi import APIRouter, HTTPException
from app.services.yahoo_finance import fetch_ohlcv
import pandas as pd

router = APIRouter()

@router.get("/data/ohlcv")
def get_ohlcv_data(symbol: str, start: str, end: str):
    try:
        df = fetch_ohlcv(symbol, start, end)

        if df.empty:
            raise HTTPException(status_code=404, detail="No data")

        # 🔥 THIS IS THE FIX
        df = df.reset_index()
        df["Date"] = df["Date"].astype(str)

        return {
            "symbol": symbol,
            "data": df.to_dict(orient="records")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
