import time
import pandas as pd
import yfinance as yf


class MarketDataService:
    """Fetches public market data with a tiny in-memory cache and synthetic fallback."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[float, pd.DataFrame]] = {}

    def history(self, symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        key = f"{symbol}:{period}:{interval}"
        cached = self._cache.get(key)
        if cached and time.time() - cached[0] < self.ttl_seconds:
            return cached[1]
        try:
            frame = yf.Ticker(symbol).history(period=period, interval=interval, auto_adjust=False)
            if frame.empty:
                raise ValueError("empty Yahoo Finance response")
        except Exception:
            frame = self._fallback_frame(symbol)
        self._cache[key] = (time.time(), frame)
        return frame

    def screen_universe(self, max_price: float | None = None) -> list[str]:
        symbols = ["AAPL", "MSFT", "NVDA", "AMD", "TSLA", "META", "GOOGL", "AMZN", "JPM", "XOM", "TCS.NS", "TATAMOTORS.NS", "INFY.NS"]
        if max_price is None:
            return symbols
        return [symbol for symbol in symbols if float(self.history(symbol)["Close"].iloc[-1]) <= max_price]

    def _fallback_frame(self, symbol: str) -> pd.DataFrame:
        dates = pd.date_range(end=pd.Timestamp.utcnow(), periods=120, freq="D")
        seed = sum(ord(ch) for ch in symbol)
        base = 50 + seed % 150
        drift = pd.Series(range(120), dtype=float) * ((seed % 7) - 2) / 100
        close = base + drift + pd.Series(range(120)).rolling(5, min_periods=1).mean() * 0.02
        return pd.DataFrame({"Open": close * 0.995, "High": close * 1.02, "Low": close * 0.98, "Close": close, "Volume": 1_000_000 + (seed % 100) * 10_000}, index=dates)
