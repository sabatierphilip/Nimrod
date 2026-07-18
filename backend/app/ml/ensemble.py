from dataclasses import dataclass
import numpy as np
from app.ml.config import EnsembleMethod


@dataclass
class EnsemblePrediction:
    probability: float
    method: EnsembleMethod
    model_probabilities: dict[str, float]
    weights: dict[str, float]


class EnsembleEngine:
    def combine(self, probabilities: dict[str, float], method: EnsembleMethod = "probability_averaging", performance_weights: dict[str, float] | None = None) -> EnsemblePrediction:
        weights = performance_weights or {name: 1.0 for name in probabilities}
        total_weight = sum(max(weights.get(name, 0.0), 0.0) for name in probabilities) or 1.0
        if method == "majority_voting":
            votes = [1 if probability >= 0.5 else 0 for probability in probabilities.values()]
            probability = sum(votes) / max(len(votes), 1)
        elif method == "weighted_voting":
            probability = sum((1 if probabilities[name] >= 0.5 else 0) * weights.get(name, 1.0) for name in probabilities) / total_weight
        else:
            probability = sum(probabilities[name] * weights.get(name, 1.0) for name in probabilities) / total_weight
        return EnsemblePrediction(float(np.clip(probability, 0.0, 1.0)), method, probabilities, weights)
