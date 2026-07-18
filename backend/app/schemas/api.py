from pydantic import BaseModel
from app.models.market import StockRecommendation


class ApiMessage(BaseModel):
    message: str


class SimpleModeResponse(BaseModel):
    disclaimer: str
    recommendations: list[StockRecommendation]


class ChatRequest(BaseModel):
    message: str
    groq_api_key: str
    context_symbols: list[str] = []


class ChatResponse(BaseModel):
    answer: str
    interpreted_filters: dict[str, str | float | int | None] = {}


class MLTrainingRequest(BaseModel):
    tickers: list[str]
    start_date: str
    end_date: str
    prediction_horizon: int = 1
    holding_period: int = 1
    target: str = "positive_return"
    enabled_models: list[str] = ["random_forest", "logistic_regression", "gradient_boosting", "extra_trees", "decision_tree"]
    random_seed: int = 42
    groq_api_key: str | None = None
    include_llm_explanation: bool = False


class MLSimulationRequest(MLTrainingRequest):
    capital: float = 10000
    max_allocation_per_stock: float = 0.2
    max_open_positions: int = 5
    stop_loss_percent: float = 3.0
    target_percent: float = 6.0

class RecommendRequest(BaseModel):
    buy_date: str
    sell_date: str
    capital: float
    number_of_stocks: int
    market: str = "NSE"
    risk_level: str = "Medium"


class TradeRecommendation(BaseModel):
    rank: int
    symbol: str
    buy_price: float
    expected_return: float
    probability: float
    confidence: str
    risk_score: float
    liquidity_score: float
    momentum_score: float
    trend_score: float
    volatility_score: float
    final_opportunity_score: float
    quantity: int
    allocated_capital: float
    reasons: list[str]


class PortfolioMetrics(BaseModel):
    expected_portfolio_return: float
    risk_rating: str
    diversification: str
    suggested_allocation: dict[str, float]
    total_allocated: float
    cash_remaining: float
    estimated_costs: float
    actual_return: float | None = None
    profit_loss: float | None = None
    win_rate: float | None = None
    benchmark_return: float | None = None
    drawdown: float | None = None
    equity_curve: list[dict[str, float | str]] = []


class RecommendResponse(BaseModel):
    disclaimer: str
    mode: str
    as_of: str
    recommendations: list[TradeRecommendation]
    portfolio_metrics: PortfolioMetrics
    trade_log: list[dict[str, float | int | str]]
    model_confidence: float
    reasoning: list[str]
    warnings: list[str]
