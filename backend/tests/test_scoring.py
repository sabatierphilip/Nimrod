import pytest

pytest.importorskip("pydantic")

from app.models.market import IndicatorSet
from app.services.scoring import ScoringEngine


def test_score_is_normalized() -> None:
    score, confidence = ScoringEngine().score(IndicatorSet(rsi=62, macd=2, macd_signal=1, volume_trend="rising", trend_direction="uptrend", gap_percent=1, atr=2, support=100))
    assert 0 <= score <= 100
    assert 0 <= confidence <= 100
