from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.models.market import SimpleModeRequest
from app.models.trading import JournalEntry, PaperTrade
from app.schemas.api import ApiMessage, ChatRequest, ChatResponse, MLTrainingRequest, MLSimulationRequest, RecommendRequest, RecommendResponse, SimpleModeResponse
from app.services.llm import GroqLLMService
from app.services.market_data import MarketDataService
from app.services.news import NewsService
from app.services.recommendations import RecommendationService
from app.services.risk import RiskManagementService
from app.services.trade_finder import AITradeFinderService
from app.ml.config import ModelSpec, SimulationConfig, TrainingConfig
from app.ml.explanations import MLExplanationService
from app.ml.reporting import ReportGenerator
from app.ml.scenarios import DEFAULT_MARKET_SCENARIOS
from app.ml.simulation import HistoricalSimulator
from app.ml.training import MLEngineTrainer

DISCLAIMER = "This software provides market research and educational analysis only. It does not guarantee profits and should not be considered financial advice."
settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_methods=["*"], allow_headers=["*"])
market_data = MarketDataService(settings.cache_ttl_seconds)
recommendations = RecommendationService(market_data)
trade_finder = AITradeFinderService(market_data)
news = NewsService()
llm = GroqLLMService()
ml_explainer = MLExplanationService(llm)
journal: list[JournalEntry] = []
paper_trades: list[PaperTrade] = []


@app.get("/health", response_model=ApiMessage)
def health() -> ApiMessage:
    return ApiMessage(message="Nimrod API is running")


@app.get("/disclaimer", response_model=ApiMessage)
def disclaimer() -> ApiMessage:
    return ApiMessage(message=DISCLAIMER)


@app.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest) -> RecommendResponse:
    try:
        return trade_finder.recommend(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/simple", response_model=SimpleModeResponse)
def simple_mode(request: SimpleModeRequest) -> SimpleModeResponse:
    return SimpleModeResponse(disclaimer=DISCLAIMER, recommendations=recommendations.simple(request))


@app.get("/advanced/overview")
def advanced_overview() -> dict[str, object]:
    return {"watchlist": market_data.screen_universe()[:8], "sector_performance": [{"sector": "Technology", "change": 1.2}, {"sector": "Energy", "change": -0.3}], "volume_leaders": ["NVDA", "TSLA", "AMD"], "momentum_leaders": ["NVDA", "META", "AAPL"], "fifty_two_week": {"high": ["MSFT", "AMZN"], "low": ["XOM"]}, "economic_calendar": ["CPI", "FOMC Minutes"], "upcoming_earnings": ["AAPL", "MSFT"]}


@app.get("/news")
def latest_news() -> list[dict[str, str]]:
    return news.latest()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    filters = llm.interpret_filters(request.message)
    try:
        answer = await llm.complete(request.groq_api_key, settings.groq_model, request.message, str(filters))
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Groq request failed. Check the local API key and try again.") from exc
    return ChatResponse(answer=answer, interpreted_filters=filters)


@app.post("/risk-plan")
def risk_plan(capital: float, entry: float, stop_loss: float, target: float, risk_percent: float = 1.0):
    return RiskManagementService().build_plan(capital, entry, stop_loss, target, risk_percent)


@app.get("/journal")
def list_journal() -> list[JournalEntry]:
    return journal


@app.post("/journal")
def add_journal(entry: JournalEntry) -> JournalEntry:
    journal.append(entry)
    return entry


@app.get("/paper-trading")
def list_paper_trades() -> dict[str, object]:
    return {"balance": 100000, "open_trades": [trade for trade in paper_trades if trade.status == "open"], "closed_trades": [trade for trade in paper_trades if trade.status == "closed"], "performance": {"return_percent": 0, "drawdown": 0}, "leaderboard": []}


@app.post("/paper-trading")
def add_paper_trade(trade: PaperTrade) -> PaperTrade:
    paper_trades.append(trade)
    return trade


@app.get("/backtest")
def backtest(symbol: str, strategy: str, start: str, end: str) -> dict[str, object]:
    return {"symbol": symbol, "strategy": strategy, "date_range": [start, end], "win_rate": 0.0, "profit": 0.0, "loss": 0.0, "drawdown": 0.0, "sharpe_ratio": 0.0, "trades": [], "note": "Backtest endpoint scaffold; strategy execution remains deterministic and does not use the LLM."}


@app.get("/ml/scenarios")
def ml_scenarios() -> list[dict[str, str]]:
    return [scenario.__dict__ for scenario in DEFAULT_MARKET_SCENARIOS]


@app.post("/ml/train")
async def train_ml(request: MLTrainingRequest) -> dict[str, object]:
    ticker = request.tickers[0]
    frame = market_data.history(ticker, period="5y")
    config = TrainingConfig(tickers=request.tickers, start_date=request.start_date, end_date=request.end_date, prediction_horizon=request.prediction_horizon, holding_period=request.holding_period, target=request.target, random_seed=request.random_seed, models=[ModelSpec(name) for name in request.enabled_models])
    training = MLEngineTrainer().train(frame, config, market_data.history("SPY", period="5y"))
    report = ReportGenerator().generate(training)
    payload = {"disclaimer": report.disclaimer, "trained_models": [model.name for model in training.models], "skipped_models": training.skipped_models, "validation_scores": training.validation_scores, "feature_importance": report.feature_importance, "reproducibility": report.reproducibility}
    payload["llm_explanation"] = await ml_explainer.explain(request.groq_api_key, settings.groq_model, payload) if request.include_llm_explanation and request.groq_api_key else ml_explainer.local_explanation(payload)
    return payload


@app.post("/ml/simulate")
async def simulate_ml(request: MLSimulationRequest) -> dict[str, object]:
    ticker = request.tickers[0]
    frame = market_data.history(ticker, period="5y")
    training_config = TrainingConfig(tickers=request.tickers, start_date=request.start_date, end_date=request.end_date, prediction_horizon=request.prediction_horizon, holding_period=request.holding_period, target=request.target, random_seed=request.random_seed, models=[ModelSpec(name) for name in request.enabled_models])
    simulation_config = SimulationConfig(capital=request.capital, max_allocation_per_stock=request.max_allocation_per_stock, max_open_positions=request.max_open_positions, stop_loss_percent=request.stop_loss_percent, target_percent=request.target_percent)
    result = HistoricalSimulator().run_single_symbol(ticker, frame, training_config, simulation_config)
    payload = {"disclaimer": ReportGenerator.disclaimer, "equity_curve": result.equity_curve, "trades": [trade.__dict__ for trade in result.trades], "warnings": result.warnings}
    payload["llm_explanation"] = await ml_explainer.explain(request.groq_api_key, settings.groq_model, payload, "Explain this historical ML simulation with risk and uncertainty.") if request.include_llm_explanation and request.groq_api_key else ml_explainer.local_explanation(payload)
    return payload
