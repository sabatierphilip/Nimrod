from dataclasses import dataclass
from time import perf_counter
from typing import Any
from app.ml.config import ModelSpec


@dataclass
class TrainedModel:
    name: str
    estimator: Any
    feature_names: list[str]
    training_time_seconds: float
    prediction_speed_rows_per_second: float = 0.0


class ModelRegistry:
    """Builds pluggable, sklearn-compatible model pipelines when libraries are available."""

    def build(self, spec: ModelSpec, random_seed: int) -> Any:
        try:
            from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import StandardScaler
            from sklearn.tree import DecisionTreeClassifier
        except ModuleNotFoundError as exc:
            raise RuntimeError("scikit-learn is required for ML training. Install backend requirements first.") from exc
        name = spec.name
        params = {**spec.parameters}
        if name == "random_forest":
            estimator = RandomForestClassifier(n_estimators=int(params.pop("n_estimators", 120)), random_state=random_seed, class_weight="balanced", **params)
            return Pipeline([("model", estimator)])
        if name == "logistic_regression":
            estimator = LogisticRegression(max_iter=int(params.pop("max_iter", 1000)), class_weight="balanced", random_state=random_seed, **params)
            return Pipeline([("scaler", StandardScaler()), ("model", estimator)])
        if name == "gradient_boosting":
            return Pipeline([("model", GradientBoostingClassifier(random_state=random_seed, **params))])
        if name == "extra_trees":
            estimator = ExtraTreesClassifier(n_estimators=int(params.pop("n_estimators", 160)), random_state=random_seed, class_weight="balanced", **params)
            return Pipeline([("model", estimator)])
        if name == "decision_tree":
            return Pipeline([("model", DecisionTreeClassifier(random_state=random_seed, class_weight="balanced", **params))])
        if name == "xgboost":
            try:
                from xgboost import XGBClassifier
            except ModuleNotFoundError as exc:
                raise RuntimeError("xgboost is enabled but not installed") from exc
            return Pipeline([("model", XGBClassifier(random_state=random_seed, eval_metric="logloss", **params))])
        if name == "lightgbm":
            try:
                from lightgbm import LGBMClassifier
            except ModuleNotFoundError as exc:
                raise RuntimeError("lightgbm is enabled but not installed") from exc
            return Pipeline([("model", LGBMClassifier(random_state=random_seed, **params))])
        raise ValueError(f"Unknown model: {name}")

    def fit(self, name: str, estimator: Any, x_train: Any, y_train: Any, feature_names: list[str]) -> TrainedModel:
        start = perf_counter()
        estimator.fit(x_train, y_train)
        return TrainedModel(name=name, estimator=estimator, feature_names=feature_names, training_time_seconds=perf_counter() - start)
