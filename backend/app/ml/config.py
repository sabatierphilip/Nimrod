from dataclasses import dataclass, field
from typing import Literal

ValidationStrategy = Literal["expanding", "rolling", "walk_forward", "blocked"]
TargetType = Literal["next_day_return", "return", "positive_return", "outperform_market", "binary_direction", "multiclass_direction"]
EnsembleMethod = Literal["majority_voting", "weighted_voting", "probability_averaging"]


@dataclass(frozen=True)
class ModelSpec:
    name: str
    enabled: bool = True
    parameters: dict[str, int | float | str | bool | None] = field(default_factory=dict)


@dataclass(frozen=True)
class TrainingConfig:
    tickers: list[str]
    start_date: str
    end_date: str
    prediction_horizon: int = 1
    holding_period: int = 1
    target: TargetType = "positive_return"
    validation: ValidationStrategy = "walk_forward"
    feature_set: list[str] | None = None
    random_seed: int = 42
    models: list[ModelSpec] = field(default_factory=lambda: [ModelSpec("random_forest"), ModelSpec("logistic_regression"), ModelSpec("gradient_boosting"), ModelSpec("extra_trees"), ModelSpec("decision_tree"), ModelSpec("xgboost", enabled=False), ModelSpec("lightgbm", enabled=False)])


@dataclass(frozen=True)
class SimulationConfig:
    capital: float = 10_000
    max_allocation_per_stock: float = 0.2
    max_open_positions: int = 5
    risk_percent: float = 1.0
    stop_loss_percent: float = 3.0
    target_percent: float = 6.0
    transaction_cost_percent: float = 0.05
    brokerage: float = 0.0
    taxes_percent: float = 0.0
    slippage_percent: float = 0.05
    spread_percent: float = 0.02
    dp_charges: float = 0.0
    rebalance_frequency: int = 1
