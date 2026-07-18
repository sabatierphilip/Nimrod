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
