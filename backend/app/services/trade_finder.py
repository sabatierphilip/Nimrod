from __future__ import annotations

from datetime import date, timedelta
import math
import pandas as pd
from app.ml.config import ModelSpec, TrainingConfig
from app.ml.features import FeatureEngineer
from app.ml.training import MLEngineTrainer
from app.schemas.api import PortfolioMetrics, RecommendRequest, RecommendResponse, TradeRecommendation
from app.services.india_market import INDIAN_MARKET_HOLIDAYS_2025_2026, IndianBrokerageCalculator, NSE_BENCHMARKS, is_indian_trading_day, market_cutoff
from app.services.market_data import MarketDataService

DISCLAIMER = "Research only. Recommendations are deterministic ML rankings, not financial advice or automated trading instructions."


class AITradeFinderService:
    """India-first ML ranking and historical replay service with point-in-time data cuts."""

    def __init__(self, market_data: MarketDataService) -> None:
        self.market_data = market_data
        self.features = FeatureEngineer()
        self.trainer = MLEngineTrainer()
        self.costs = IndianBrokerageCalculator()

    def recommend(self, request: RecommendRequest) -> RecommendResponse:
        buy = date.fromisoformat(request.buy_date)
        sell = date.fromisoformat(request.sell_date)
        if sell <= buy:
            raise ValueError("sell_date must be after buy_date")
        if request.capital <= 0 or request.number_of_stocks <= 0:
            raise ValueError("capital and number_of_stocks must be positive")
        today = date.today()
        mode = "live" if buy >= today else "historical_replay"
        warnings = self._calendar_warnings(buy, sell)
        lookback_start = (buy - timedelta(days=520)).isoformat()
        data_end = (buy + timedelta(days=1)).isoformat()
        benchmark_symbol = NSE_BENCHMARKS.get(request.market, "^NSEI")
        benchmark = self.market_data.history(benchmark_symbol, start=lookback_start, end=data_end)
        candidates: list[TradeRecommendation] = []
        trade_rows: list[dict[str, float | int | str]] = []
        for symbol in self.market_data.screen_universe(market=request.market):
            frame = self.market_data.history(symbol, start=lookback_start, end=data_end)
            frame = self._point_in_time(frame, buy)
            if len(frame) < 90:
                continue
            buy_price = float(frame["Close"].iloc[-1])
            if buy_price > request.capital:
                continue
            rec = self._score_symbol(symbol, frame, benchmark, buy_price, request, len(candidates) + 1)
            if rec:
                candidates.append(rec)
        ranked = sorted(candidates, key=lambda item: (-item.final_opportunity_score, item.symbol))[: request.number_of_stocks]
        ranked = self._allocate(ranked, request.capital)
        for idx, rec in enumerate(ranked, 1):
            rec.rank = idx
        metrics = self._portfolio_metrics(ranked, request.capital, request.risk_level)
        if mode == "historical_replay" and ranked:
            actual = self._replay(ranked, sell, request.capital, metrics.estimated_costs, benchmark_symbol)
            trade_rows = actual["trade_log"]
            metrics.actual_return = actual["actual_return"]
            metrics.profit_loss = actual["profit_loss"]
            metrics.win_rate = actual["win_rate"]
            metrics.benchmark_return = actual["benchmark_return"]
            metrics.drawdown = actual["drawdown"]
            metrics.equity_curve = actual["equity_curve"]
        if len(ranked) < request.number_of_stocks:
            warnings.append("Requested stock count exceeded affordable/high-quality eligible NSE opportunities; returned fewer picks.")
        return RecommendResponse(disclaimer=DISCLAIMER, mode=mode, as_of=market_cutoff(buy).isoformat(), recommendations=ranked, portfolio_metrics=metrics, trade_log=trade_rows, model_confidence=round(sum(r.probability for r in ranked) / max(len(ranked), 1), 3), reasoning=["All ranks are produced by deterministic in-house ML models and point-in-time technical features.", "The LLM layer is not used to select securities; it may only explain the returned facts."], warnings=warnings)

    def _score_symbol(self, symbol: str, frame: pd.DataFrame, benchmark: pd.DataFrame, buy_price: float, request: RecommendRequest, rank: int) -> TradeRecommendation | None:
        horizon = max((date.fromisoformat(request.sell_date) - date.fromisoformat(request.buy_date)).days, 1)
        config = TrainingConfig(tickers=[symbol], start_date=str(frame.index.min().date()), end_date=request.buy_date, prediction_horizon=horizon, holding_period=horizon, models=[ModelSpec("logistic_regression"), ModelSpec("random_forest", parameters={"n_estimators": 60}), ModelSpec("extra_trees", parameters={"n_estimators": 80})], random_seed=42)
        result = self.trainer.train(frame, config, benchmark)
        if not result.models:
            return None
        features = self.features.build(frame, benchmark).tail(1)[result.feature_names]
        probabilities = [self.trainer._positive_probability(model.estimator, features)[0] for model in result.models]
        probability = float(sum(probabilities) / len(probabilities))
        daily_vol = float(frame["Close"].pct_change().tail(20).std() or 0.02)
        momentum = float(frame["Close"].pct_change(10).iloc[-1] or 0)
        trend = float(frame["Close"].iloc[-1] / frame["Close"].rolling(50).mean().iloc[-1] - 1)
        liquidity = min(float(frame["Volume"].tail(20).mean() * buy_price / 10_000_000), 100.0)
        expected = (probability - 0.5) * max(0.02, daily_vol * math.sqrt(config.prediction_horizon)) * 2
        risk_score = min(daily_vol * 1000, 100.0)
        final = probability * 55 + max(momentum, -0.1) * 150 + max(trend, -0.1) * 100 + liquidity * 0.15 - risk_score * 0.12
        confidence = "High" if probability >= 0.7 and len(result.models) >= 2 else "Medium" if probability >= 0.58 else "Low"
        reasons = [f"Model vote probability of positive return is {probability:.0%}.", f"10-session momentum is {momentum:.2%} and trend versus 50-DMA is {trend:.2%}.", f"Liquidity score supports small retail execution: {liquidity:.1f}/100."]
        return TradeRecommendation(rank=rank, symbol=symbol.replace(".NS", ""), buy_price=round(buy_price, 2), expected_return=round(expected * 100, 2), probability=round(probability, 3), confidence=confidence, risk_score=round(risk_score, 2), liquidity_score=round(liquidity, 2), momentum_score=round(momentum * 100, 2), trend_score=round(trend * 100, 2), volatility_score=round(daily_vol * 100, 2), final_opportunity_score=round(final, 2), quantity=0, allocated_capital=0, reasons=reasons)

    def _allocate(self, ranked: list[TradeRecommendation], capital: float) -> list[TradeRecommendation]:
        remaining = capital
        for rec in ranked:
            target = capital / max(len(ranked), 1)
            qty = max(1, int(min(target, remaining) // rec.buy_price)) if remaining >= rec.buy_price else 0
            rec.quantity = qty
            rec.allocated_capital = round(qty * rec.buy_price, 2)
            remaining -= rec.allocated_capital
        return [r for r in ranked if r.quantity > 0]

    def _portfolio_metrics(self, ranked: list[TradeRecommendation], capital: float, risk: str) -> PortfolioMetrics:
        allocated = sum(r.allocated_capital for r in ranked)
        gross_sell = sum(r.allocated_capital * (1 + r.expected_return / 100) for r in ranked)
        costs = self.costs.estimate_delivery(allocated, gross_sell).total if allocated else 0.0
        expected = ((gross_sell - costs + (capital - allocated)) / capital - 1) * 100 if capital else 0.0
        return PortfolioMetrics(expected_portfolio_return=round(expected, 2), risk_rating=risk, diversification=f"{len(ranked)} NSE positions selected with capital-aware affordability filters.", suggested_allocation={r.symbol: r.allocated_capital for r in ranked}, total_allocated=round(allocated, 2), cash_remaining=round(capital - allocated, 2), estimated_costs=costs)

    def _replay(self, ranked: list[TradeRecommendation], sell: date, capital: float, expected_costs: float, benchmark_symbol: str) -> dict[str, object]:
        sells = []
        for rec in ranked:
            symbol = rec.symbol + ".NS"
            data = self.market_data.history(symbol, start=(sell - timedelta(days=7)).isoformat(), end=(sell + timedelta(days=3)).isoformat())
            data = data[data.index.date >= sell]
            sell_price = float(data["Close"].iloc[0]) if not data.empty else rec.buy_price
            pnl = (sell_price - rec.buy_price) * rec.quantity
            sells.append({"symbol": rec.symbol, "quantity": rec.quantity, "buy_price": rec.buy_price, "sell_price": round(sell_price, 2), "profit_loss": round(pnl, 2), "return_percent": round((sell_price / rec.buy_price - 1) * 100, 2)})
        gross = sum(row["sell_price"] * row["quantity"] for row in sells)
        invested = sum(r.allocated_capital for r in ranked)
        costs = self.costs.estimate_delivery(invested, gross).total
        final_value = capital - invested + gross - costs
        profit = final_value - capital
        bench = self.market_data.history(benchmark_symbol, start=(sell - timedelta(days=10)).isoformat(), end=(sell + timedelta(days=3)).isoformat())
        benchmark_return = 0.0 if len(bench) < 2 else float((bench["Close"].iloc[-1] / bench["Close"].iloc[0] - 1) * 100)
        equity = [{"date": "buy", "value": round(capital - expected_costs, 2)}, {"date": sell.isoformat(), "value": round(final_value, 2)}]
        return {"trade_log": sells, "actual_return": round(profit / capital * 100, 2), "profit_loss": round(profit, 2), "win_rate": round(sum(1 for row in sells if row["profit_loss"] > 0) / max(len(sells), 1) * 100, 2), "benchmark_return": round(benchmark_return, 2), "drawdown": round(min(0, (final_value / capital - 1) * 100), 2), "equity_curve": equity}

    def _point_in_time(self, frame: pd.DataFrame, buy: date) -> pd.DataFrame:
        return frame[frame.index.date <= buy].copy().sort_index()

    def _calendar_warnings(self, buy: date, sell: date) -> list[str]:
        warnings = []
        if not is_indian_trading_day(buy):
            warnings.append(f"Buy date {buy.isoformat()} is not a regular Indian trading day; replay uses the latest candle available before the cutoff.")
        if not is_indian_trading_day(sell):
            warnings.append(f"Sell date {sell.isoformat()} is not a regular Indian trading day; replay exits on the next available candle.")
        if buy in INDIAN_MARKET_HOLIDAYS_2025_2026 or sell in INDIAN_MARKET_HOLIDAYS_2025_2026:
            warnings.append("Indian exchange holiday calendar was applied.")
        return warnings
