import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE_URL = "https://finnhub.io/api/v1"
SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
RAW_DIR = Path(__file__).parent / "data" / "raw"


def get_quote(symbol: str, api_key: str) -> dict:
    response = requests.get(
        f"{BASE_URL}/quote",
        params={"symbol": symbol, "token": api_key},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def fetch_and_save() -> str:
    api_key = os.environ["FINNHUB_API_KEY"]
    results = []
    for symbol in SYMBOLS:
        quote = get_quote(symbol, api_key)
        quote["symbol"] = symbol
        quote["fetched_at"] = datetime.now(timezone.utc).isoformat()
        results.append(quote)
        print(f"Fetched {symbol}: ${quote['c']}")
        time.sleep(1)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filepath = RAW_DIR / f"quotes_{timestamp}.json"
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} quotes to {filepath}")
    return str(filepath)


if __name__ == "__main__":
    fetch_and_save()