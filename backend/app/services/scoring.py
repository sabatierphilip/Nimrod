from app.models.market import IndicatorSet


class ScoringEngine:
    """Weighted non-LLM opportunity scoring engine normalized to 0-100."""

    weights = {"momentum": 0.22, "volume": 0.14, "technical": 0.22, "news": 0.10, "fundamental": 0.12, "volatility": 0.10, "risk": 0.10}

    def score(self, indicators: IndicatorSet, news_sentiment: float = 50, fundamental: float = 50) -> tuple[float, float]:
        momentum = self._bounded((indicators.rsi or 50) + (10 if (indicators.macd or 0) > (indicators.macd_signal or 0) else -5))
        volume = 70 if indicators.volume_trend == "rising" else 40
        technical = 75 if indicators.trend_direction == "uptrend" else 35 if indicators.trend_direction == "downtrend" else 55
        volatility = self._bounded(70 - abs(indicators.gap_percent or 0) * 3)
        risk = self._bounded(75 - ((indicators.atr or 0) / max(indicators.support or 1, 1)) * 100)
        raw = {"momentum": momentum, "volume": volume, "technical": technical, "news": news_sentiment, "fundamental": fundamental, "volatility": volatility, "risk": risk}
        opportunity = sum(raw[key] * weight for key, weight in self.weights.items())
        confidence = min(95, max(15, 45 + abs(opportunity - 50) * 0.7 + (10 if indicators.relative_strength else 0)))
        return round(opportunity, 2), round(confidence, 2)

    def _bounded(self, value: float) -> float:
        return max(0, min(100, value))
