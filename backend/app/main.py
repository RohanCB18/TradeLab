from fastapi import FastAPI
from app.api.backtest import router as backtest_router

app = FastAPI(title="TradeLab Backend")

app.include_router(backtest_router)

@app.get("/")
def root():
    return {"status": "Backend is running"}
