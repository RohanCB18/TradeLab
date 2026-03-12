import requests
import time

BASE_URL = "http://127.0.0.1:8001"

def test_strategy(strategy_id):
    print(f"\n--- Testing Strategy: {strategy_id} ---")
    params = {
        "strategy_id": strategy_id,
        "universe": "DOW",
        "start": "2023-01-01",
        "end": "2024-01-01"
    }
    try:
        response = requests.get(f"{BASE_URL}/run", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Metrics:")
            for k, v in data['metrics'].items():
                print(f"  {k}: {v}")
            print(f"Chart Data Points: {len(data['chart_data'])}")
        else:
            print(f"Failed! Status: {response.status_code}, Detail: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Note: Make sure the server is running before executing this
    for sid in ["mean_reversion", "rs_momentum", "macd_trend"]:
        test_strategy(sid)
