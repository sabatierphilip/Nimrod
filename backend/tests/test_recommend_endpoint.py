import pandas as pd
from fastapi.testclient import TestClient
from app.main import app, market_data


def deterministic_frame(symbol: str, periods: int = 560) -> pd.DataFrame:
    dates = pd.bdate_range(end="2025-01-06", periods=periods)
    seed = sum(ord(ch) for ch in symbol)
    base = 40 + seed % 35
    trend = pd.Series(range(periods), index=dates, dtype=float) * (0.03 + (seed % 5) / 1000)
    wave = pd.Series([((i + seed) % 11) / 100 for i in range(periods)], index=dates)
    close = base + trend + wave
    return pd.DataFrame({"Open": close * 0.99, "High": close * 1.01, "Low": close * 0.98, "Close": close, "Volume": 1_000_000 + seed * 100}, index=dates)


def test_recommend_historical_replay_is_capital_aware_and_deterministic(monkeypatch):
    def fake_history(symbol, period="6mo", interval="1d", start=None, end=None):
        frame = deterministic_frame(symbol)
        if start:
            frame = frame[frame.index >= pd.Timestamp(start)]
        if end:
            frame = frame[frame.index < pd.Timestamp(end)]
        return frame

    monkeypatch.setattr(market_data, "history", fake_history)
    monkeypatch.setattr(market_data, "screen_universe", lambda max_price=None, market=None: ["AAA.NS", "BBB.NS", "EXPENSIVE.NS"])
    client = TestClient(app)
    payload = {"buy_date": "2025-01-03", "sell_date": "2025-01-06", "capital": 100, "number_of_stocks": 2, "market": "NSE", "risk_level": "Medium"}
    first = client.post("/recommend", json=payload)
    second = client.post("/recommend", json=payload)
    assert first.status_code == 200
    assert first.json() == second.json()
    body = first.json()
    assert body["mode"] == "historical_replay"
    assert body["recommendations"]
    assert sum(item["allocated_capital"] for item in body["recommendations"]) <= 100
    assert body["portfolio_metrics"]["actual_return"] is not None
    assert body["trade_log"]
