import numpy as np
import pandas as pd
from app.models.market import IndicatorSet


class TechnicalIndicatorService:
    """Deterministically calculates indicators; the LLM is never used here."""

    def calculate(self, frame: pd.DataFrame, benchmark: pd.DataFrame | None = None) -> IndicatorSet:
        data = frame.copy().dropna()
        close = data["Close"]
        high = data["High"]
        low = data["Low"]
        volume = data["Volume"]
        ema_20 = close.ewm(span=20, adjust=False).mean()
        sma_20 = close.rolling(20).mean()
        sma_50 = close.rolling(50).mean()
        rsi = self._rsi(close)
        macd_line, signal = self._macd(close)
        atr = self._atr(high, low, close)
        adx = self._adx(high, low, close)
        std = close.rolling(20).std()
        vwap = ((data["Close"] * volume).cumsum() / volume.cumsum()).iloc[-1]
        support = low.tail(30).min()
        resistance = high.tail(30).max()
        relative_strength = None
        if benchmark is not None and not benchmark.empty:
            relative_strength = float((close.iloc[-1] / close.iloc[0]) / (benchmark["Close"].iloc[-1] / benchmark["Close"].iloc[0]) * 100)
        trend = "uptrend" if close.iloc[-1] > ema_20.iloc[-1] > sma_50.iloc[-1] else "downtrend" if close.iloc[-1] < ema_20.iloc[-1] < sma_50.iloc[-1] else "sideways"
        crossover = "bullish" if ema_20.iloc[-1] > sma_50.iloc[-1] and ema_20.iloc[-2] <= sma_50.iloc[-2] else "bearish" if ema_20.iloc[-1] < sma_50.iloc[-1] and ema_20.iloc[-2] >= sma_50.iloc[-2] else "none"
        gap_percent = ((data["Open"].iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100 if len(close) > 1 else 0
        vol_trend = "rising" if volume.tail(5).mean() > volume.tail(20).mean() else "falling"
        return IndicatorSet(
            rsi=self._last(rsi), macd=self._last(macd_line), macd_signal=self._last(signal), ema_20=self._last(ema_20),
            sma_50=self._last(sma_50), atr=self._last(atr), adx=self._last(adx), vwap=float(vwap),
            bollinger_upper=self._last(sma_20 + 2 * std), bollinger_lower=self._last(sma_20 - 2 * std),
            volume_trend=vol_trend, support=float(support), resistance=float(resistance), trend_direction=trend,
            gap_percent=float(gap_percent), relative_strength=relative_strength, moving_average_crossover=crossover,
        )

    def _last(self, series: pd.Series) -> float | None:
        value = series.dropna().iloc[-1] if not series.dropna().empty else np.nan
        return None if pd.isna(value) else float(value)

    def _rsi(self, close: pd.Series, period: int = 14) -> pd.Series:
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = -delta.clip(upper=0).rolling(period).mean()
        return 100 - (100 / (1 + gain / loss.replace(0, np.nan)))

    def _macd(self, close: pd.Series) -> tuple[pd.Series, pd.Series]:
        line = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        return line, line.ewm(span=9, adjust=False).mean()

    def _atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        ranges = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1)
        return ranges.max(axis=1).rolling(period).mean()

    def _adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        plus_dm = high.diff().clip(lower=0)
        minus_dm = (-low.diff()).clip(lower=0)
        atr = self._atr(high, low, close, period)
        plus_di = 100 * plus_dm.ewm(alpha=1 / period).mean() / atr
        minus_di = 100 * minus_dm.ewm(alpha=1 / period).mean() / atr
        return (100 * (plus_di - minus_di).abs() / (plus_di + minus_di)).ewm(alpha=1 / period).mean()
