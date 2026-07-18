from app.models.market import SimpleModeRequest, StockRecommendation
from app.services.indicators import TechnicalIndicatorService
from app.services.market_data import MarketDataService
from app.services.scoring import ScoringEngine


class RecommendationService:
    def __init__(self, market_data: MarketDataService) -> None:
        self.market_data = market_data
        self.indicators = TechnicalIndicatorService()
        self.scoring = ScoringEngine()

    def simple(self, request: SimpleModeRequest) -> list[StockRecommendation]:
        results: list[StockRecommendation] = []
        benchmark = self.market_data.history("SPY")
        for symbol in self.market_data.screen_universe(request.max_stock_price):
            frame = self.market_data.history(symbol, period="6mo")
            indicator_set = self.indicators.calculate(frame, benchmark)
            opportunity, confidence = self.scoring.score(indicator_set)
            price = float(frame["Close"].iloc[-1])
            atr = indicator_set.atr or price * 0.03
            stop = round(price - atr * (1.2 if request.risk_level == "Conservative" else 1.8), 2)
            target = round(price + atr * (1.8 if request.risk_level == "Conservative" else 2.8), 2)
            results.append(StockRecommendation(symbol=symbol, company_name=symbol, current_price=round(price, 2), opportunity_score=opportunity, confidence_score=confidence, suggested_entry=round(price, 2), suggested_stop_loss=stop, suggested_target=target, expected_holding_time=request.holding_period, ai_explanation="Ranked by deterministic momentum, trend, volume, risk, and sentiment factors. Outcomes are uncertain and should be validated before any trade.", risk_summary="Risk includes market volatility, gaps, liquidity, news shocks, and model limitations. Use position sizing and stops; profits are not guaranteed.", indicators=indicator_set))
        return sorted(results, key=lambda item: item.opportunity_score, reverse=True)[:5]
