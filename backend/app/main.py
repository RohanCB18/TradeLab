from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.backtest import router as backtest_router

app = FastAPI(title="TradeLab Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specific domains like ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(backtest_router)

@app.get("/")
def root():
    return {"status": "Backend is running"}
