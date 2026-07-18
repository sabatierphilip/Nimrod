from dataclasses import dataclass, field
import pandas as pd
from app.ml.config import SimulationConfig, TrainingConfig
from app.ml.training import MLEngineTrainer


@dataclass
class SimulatedTrade:
    date: str
    symbol: str
    entry: float
    exit: float
    quantity: int
    gross_return_percent: float
    net_return_percent: float
    probability: float


@dataclass
class SimulationResult:
    equity_curve: list[float]
    trades: list[SimulatedTrade]
    warnings: list[str] = field(default_factory=list)


class HistoricalSimulator:
    """Sequential live-like historical simulation; future candles are inaccessible."""

    def __init__(self, trainer: MLEngineTrainer | None = None) -> None:
        self.trainer = trainer or MLEngineTrainer()

    def run_single_symbol(self, symbol: str, frame: pd.DataFrame, training_config: TrainingConfig, simulation_config: SimulationConfig) -> SimulationResult:
        data = frame.sort_index()
        capital = simulation_config.capital
        equity = [capital]
        trades: list[SimulatedTrade] = []
        warnings: list[str] = []
        min_history = 90
        for position in range(min_history, len(data) - training_config.prediction_horizon, simulation_config.rebalance_frequency):
            today_frame = data.iloc[: position + 1]
            tomorrow = data.iloc[position + training_config.prediction_horizon]
            try:
                result = self.trainer.train(today_frame, training_config)
                if not result.models:
                    warnings.append(f"{data.index[position].date()}: no trainable model available")
                    continue
                x_live, _ = self.trainer.prepare_dataset(today_frame, training_config)
                model = result.models[0].estimator
                probability = float(model.predict_proba(x_live.tail(1))[:, -1][0]) if hasattr(model, "predict_proba") else float(model.predict(x_live.tail(1))[0])
            except Exception as exc:
                warnings.append(f"{data.index[position].date()}: skipped due to {exc}")
                continue
            if probability < 0.55:
                equity.append(capital)
                continue
            entry = float(today_frame["Close"].iloc[-1]) * (1 + simulation_config.slippage_percent / 100 + simulation_config.spread_percent / 100)
            allocation = min(capital * simulation_config.max_allocation_per_stock, capital)
            quantity = int(allocation // entry)
            if quantity <= 0:
                equity.append(capital)
                continue
            raw_exit = float(tomorrow["Close"])
            stop = entry * (1 - simulation_config.stop_loss_percent / 100)
            target = entry * (1 + simulation_config.target_percent / 100)
            exit_price = min(max(raw_exit, stop), target)
            gross = exit_price / entry - 1
            fees = simulation_config.transaction_cost_percent / 100 + simulation_config.taxes_percent / 100 + simulation_config.slippage_percent / 100 + simulation_config.spread_percent / 100
            net = gross - fees
            pnl = quantity * entry * net - simulation_config.brokerage - simulation_config.dp_charges
            capital += pnl
            equity.append(capital)
            trades.append(SimulatedTrade(str(data.index[position].date()), symbol, round(entry, 4), round(exit_price, 4), quantity, round(gross * 100, 4), round(net * 100, 4), round(probability, 4)))
        return SimulationResult(equity, trades, warnings)
