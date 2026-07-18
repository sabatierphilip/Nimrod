from dataclasses import dataclass
from time import perf_counter
import pandas as pd
from app.ml.config import TrainingConfig
from app.ml.ensemble import EnsembleEngine
from app.ml.features import FeatureEngineer
from app.ml.labels import LabelGenerator
from app.ml.leakage import DataLeakageGuard
from app.ml.models import ModelRegistry, TrainedModel
from app.ml.validation import TimeSeriesValidator


@dataclass
class TrainingResult:
    models: list[TrainedModel]
    feature_names: list[str]
    validation_scores: dict[str, float]
    skipped_models: dict[str, str]
    random_seed: int
    training_dates: tuple[str, str]
    prediction_horizon: int


class MLEngineTrainer:
    """Coordinates point-in-time feature generation, leakage checks, and model fitting."""

    def __init__(self) -> None:
        self.features = FeatureEngineer()
        self.labels = LabelGenerator()
        self.guard = DataLeakageGuard()
        self.validation = TimeSeriesValidator()
        self.registry = ModelRegistry()
        self.ensemble = EnsembleEngine()

    def prepare_dataset(self, frame: pd.DataFrame, config: TrainingConfig, benchmark: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.Series]:
        feature_frame = self.features.build(frame, benchmark)
        labels = self.labels.generate(frame.sort_index()["Close"], config.prediction_horizon, config.target, benchmark["Close"] if benchmark is not None and not benchmark.empty else None)
        dataset = feature_frame.join(labels, how="inner").dropna()
        y = dataset.iloc[:, -1]
        x = dataset.drop(columns=[y.name])
        if config.feature_set:
            x = x[[name for name in config.feature_set if name in x.columns]]
        return x, y

    def train(self, frame: pd.DataFrame, config: TrainingConfig, benchmark: pd.DataFrame | None = None) -> TrainingResult:
        x, y = self.prepare_dataset(frame, config, benchmark)
        train_end = max(int(len(x) * 0.8) - 1, 1)
        self.guard.validate(x, y, config.prediction_horizon, train_end)
        x_train, y_train = x.iloc[: train_end + 1], y.iloc[: train_end + 1]
        x_val, y_val = x.iloc[train_end + 1 :], y.iloc[train_end + 1 :]
        trained: list[TrainedModel] = []
        scores: dict[str, float] = {}
        skipped: dict[str, str] = {}
        for spec in config.models:
            if not spec.enabled:
                skipped[spec.name] = "disabled"
                continue
            try:
                estimator = self.registry.build(spec, config.random_seed)
                model = self.registry.fit(spec.name, estimator, x_train, y_train, list(x.columns))
                start = perf_counter()
                probabilities = self._positive_probability(model.estimator, x_val)
                elapsed = max(perf_counter() - start, 1e-9)
                model.prediction_speed_rows_per_second = len(x_val) / elapsed
                scores[spec.name] = float(((probabilities >= 0.5).astype(int) == y_val.astype(int).to_numpy()).mean()) if len(y_val) else 0.0
                trained.append(model)
            except Exception as exc:  # model availability/configuration is reported, not hidden
                skipped[spec.name] = str(exc)
        return TrainingResult(trained, list(x.columns), scores, skipped, config.random_seed, (config.start_date, config.end_date), config.prediction_horizon)

    def _positive_probability(self, estimator: object, x: pd.DataFrame):
        if hasattr(estimator, "predict_proba"):
            return estimator.predict_proba(x)[:, -1]
        return estimator.predict(x)
