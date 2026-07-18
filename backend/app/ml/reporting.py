from dataclasses import asdict, dataclass
from app.ml.evaluation import EvaluationMetrics, ProfitabilityMetrics
from app.ml.simulation import SimulationResult
from app.ml.training import TrainingResult


@dataclass
class ExperimentReport:
    disclaimer: str
    model_ranking: list[dict[str, float | str]]
    feature_importance: list[dict[str, float | str]]
    improvement_suggestions: list[str]
    reproducibility: dict[str, object]
    simulation: dict[str, object] | None = None
    evaluation: dict[str, object] | None = None
    profitability: dict[str, object] | None = None


class ReportGenerator:
    disclaimer = "Experimental ML research only. Scores and simulations are uncertain, may be wrong, and never guarantee returns."

    def generate(self, training: TrainingResult, simulation: SimulationResult | None = None, evaluation: EvaluationMetrics | None = None, profitability: ProfitabilityMetrics | None = None) -> ExperimentReport:
        ranking = sorted(({"model": name, "validation_score": score} for name, score in training.validation_scores.items()), key=lambda row: float(row["validation_score"]), reverse=True)
        importances = self._feature_importance(training)
        suggestions = ["Rank models by profit after fees, not raw accuracy.", "Compare feature subsets with walk-forward validation.", "Review drawdowns and calibration before trusting scores."]
        return ExperimentReport(self.disclaimer, ranking, importances, suggestions, {"random_seed": training.random_seed, "training_dates": training.training_dates, "feature_set": training.feature_names, "prediction_horizon": training.prediction_horizon, "model_parameters": [model.name for model in training.models]}, asdict(simulation) if simulation else None, asdict(evaluation) if evaluation else None, asdict(profitability) if profitability else None)

    def _feature_importance(self, training: TrainingResult) -> list[dict[str, float | str]]:
        rows: list[dict[str, float | str]] = []
        if not training.models:
            return rows
        estimator = training.models[0].estimator
        model = estimator.named_steps.get("model") if hasattr(estimator, "named_steps") else estimator
        values = getattr(model, "feature_importances_", None)
        if values is None:
            return [{"feature": name, "importance": 0.0} for name in training.feature_names]
        return sorted(({"feature": name, "importance": float(value)} for name, value in zip(training.feature_names, values, strict=False)), key=lambda row: float(row["importance"]), reverse=True)
