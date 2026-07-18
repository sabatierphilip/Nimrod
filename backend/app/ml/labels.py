import pandas as pd
from app.ml.config import TargetType


class LabelGenerator:
    """Creates labels by shifting future returns only by the chosen horizon."""

    def generate(self, prices: pd.Series, horizon: int, target: TargetType, benchmark: pd.Series | None = None) -> pd.Series:
        future_return = prices.shift(-horizon) / prices - 1
        if target in {"next_day_return", "return"}:
            return future_return.rename("target_return")
        if target in {"positive_return", "binary_direction"}:
            return (future_return > 0).astype(int).rename("target_positive")
        if target == "outperform_market":
            if benchmark is None:
                raise ValueError("benchmark is required for outperform_market target")
            benchmark_return = benchmark.reindex(prices.index).ffill().shift(-horizon) / benchmark.reindex(prices.index).ffill() - 1
            return (future_return > benchmark_return).astype(int).rename("target_outperform")
        if target == "multiclass_direction":
            return future_return.apply(lambda value: 2 if value > 0.01 else 0 if value < -0.01 else 1).rename("target_class")
        raise ValueError(f"Unsupported target: {target}")
