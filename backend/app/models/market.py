from pydantic import BaseModel, Field


class OHLCV(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class IndicatorSet(BaseModel):
    rsi: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    ema_20: float | None = None
    sma_50: float | None = None
    atr: float | None = None
    adx: float | None = None
    vwap: float | None = None
    bollinger_upper: float | None = None
    bollinger_lower: float | None = None
    volume_trend: str = "unknown"
    support: float | None = None
    resistance: float | None = None
    trend_direction: str = "sideways"
    gap_percent: float | None = None
    relative_strength: float | None = None
    moving_average_crossover: str = "none"


class StockRecommendation(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    opportunity_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    suggested_entry: float
    suggested_stop_loss: float
    suggested_target: float
    expected_holding_time: str
    ai_explanation: str
    risk_summary: str
    indicators: IndicatorSet


class SimpleModeRequest(BaseModel):
    investment_amount: float = Field(gt=0)
    holding_period: str
    risk_level: str
    max_stock_price: float | None = None
    preferred_sector: str | None = None
