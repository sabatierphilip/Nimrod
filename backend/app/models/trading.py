from datetime import datetime
from pydantic import BaseModel, Field


class RiskPlan(BaseModel):
    capital: float
    max_risk: float
    position_size: int
    risk_reward_ratio: float
    stop_loss: float
    target_price: float
    potential_gain: float
    potential_loss: float


class JournalEntry(BaseModel):
    id: str
    symbol: str
    entry: float
    exit: float | None = None
    reason: str
    confidence: float = Field(ge=0, le=100)
    profit_loss: float | None = None
    emotion: str
    notes: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PaperTrade(BaseModel):
    id: str
    symbol: str
    side: str
    quantity: int
    entry_price: float
    exit_price: float | None = None
    status: str = "open"
