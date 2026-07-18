import pandas as pd


class FeatureEngineer:
    """Deterministically builds point-in-time features from OHLCV candles."""

    def build(self, frame: pd.DataFrame, benchmark: pd.DataFrame | None = None, news_sentiment: float = 50.0, sector_strength: float = 50.0, market_trend: float = 0.0, volatility_index: float | None = None) -> pd.DataFrame:
        data = frame.copy().sort_index()
        close = data["Close"]
        high = data["High"]
        low = data["Low"]
        volume = data["Volume"]
        features = pd.DataFrame(index=data.index)
        features["daily_return"] = close.pct_change()
        features["weekly_return"] = close.pct_change(5)
        features["momentum_10"] = close.pct_change(10)
        features["rolling_volatility_20"] = features["daily_return"].rolling(20).std()
        features["volume_change"] = volume.pct_change()
        features["rsi_14"] = self._rsi(close)
        macd, signal = self._macd(close)
        features["macd"] = macd
        features["macd_signal"] = signal
        features["ema_20"] = close.ewm(span=20, adjust=False).mean()
        features["sma_50"] = close.rolling(50).mean()
        features["price_relative_to_ema_20"] = close / features["ema_20"] - 1
        features["price_relative_to_sma_50"] = close / features["sma_50"] - 1
        features["vwap"] = (close * volume).cumsum() / volume.cumsum()
        features["atr_14"] = self._atr(high, low, close)
        features["adx_14"] = self._adx(high, low, close)
        features["obv"] = (volume.where(close.diff() >= 0, -volume)).cumsum()
        support = low.rolling(30).min()
        resistance = high.rolling(30).max()
        features["distance_to_support"] = close / support - 1
        features["distance_to_resistance"] = close / resistance - 1
        features["gap_percent"] = data["Open"].pct_change().fillna(0) * 100
        low_52 = low.rolling(252, min_periods=50).min()
        high_52 = high.rolling(252, min_periods=50).max()
        features["position_52_week"] = (close - low_52) / (high_52 - low_52)
        if benchmark is not None and not benchmark.empty:
            bench = benchmark.sort_index()["Close"].reindex(data.index).ffill()
            features["relative_strength"] = close.pct_change(20) - bench.pct_change(20)
        else:
            features["relative_strength"] = 0.0
        features["news_sentiment_score"] = news_sentiment
        features["sector_strength"] = sector_strength
        features["market_trend"] = market_trend
        features["volatility_index"] = volatility_index if volatility_index is not None else features["rolling_volatility_20"].rolling(20).mean()
        return features.replace([float("inf"), float("-inf")], pd.NA).dropna()

    def _rsi(self, close: pd.Series, period: int = 14) -> pd.Series:
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = -delta.clip(upper=0).rolling(period).mean()
        return 100 - (100 / (1 + gain / loss.replace(0, pd.NA)))

    def _macd(self, close: pd.Series) -> tuple[pd.Series, pd.Series]:
        line = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        return line, line.ewm(span=9, adjust=False).mean()

    def _atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        ranges = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1)
        return ranges.max(axis=1).rolling(period).mean()

    def _adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        atr = self._atr(high, low, close, period)
        plus_di = 100 * high.diff().clip(lower=0).ewm(alpha=1 / period).mean() / atr
        minus_di = 100 * (-low.diff()).clip(lower=0).ewm(alpha=1 / period).mean() / atr
        return (100 * (plus_di - minus_di).abs() / (plus_di + minus_di)).ewm(alpha=1 / period).mean()
