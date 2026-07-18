from dataclasses import dataclass
from math import sqrt
import numpy as np


@dataclass
class EvaluationMetrics:
    prediction_accuracy: float
    directional_accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float | None
    log_loss: float | None
    confusion_matrix: list[list[int]]
    calibration_error: float
    brier_score: float
    top_1_accuracy: float
    top_5_accuracy: float


@dataclass
class ProfitabilityMetrics:
    net_profit_percent: float
    annual_return_percent: float
    monthly_return_percent: float
    daily_return_percent: float
    profit_factor: float
    win_rate_percent: float
    average_profit_percent: float
    average_loss_percent: float
    maximum_drawdown_percent: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    risk_reward_ratio: float
    profit_after_fees_percent: float
    profit_before_fees_percent: float
    capital_growth_percent: float
    probability_of_profit: float
    probability_of_ruin: float


class ModelEvaluator:
    def classification(self, truth: list[int], probabilities: list[float]) -> EvaluationMetrics:
        y = np.array(truth)
        p = np.array(probabilities)
        pred = (p >= 0.5).astype(int)
        tp = int(((pred == 1) & (y == 1)).sum())
        tn = int(((pred == 0) & (y == 0)).sum())
        fp = int(((pred == 1) & (y == 0)).sum())
        fn = int(((pred == 0) & (y == 1)).sum())
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-12)
        brier = float(np.mean((p - y) ** 2)) if len(y) else 0.0
        log_loss = float(-np.mean(y * np.log(np.clip(p, 1e-9, 1)) + (1 - y) * np.log(np.clip(1 - p, 1e-9, 1)))) if len(y) else None
        return EvaluationMetrics(float((pred == y).mean()) if len(y) else 0.0, float((pred == y).mean()) if len(y) else 0.0, precision, recall, f1, self._roc_auc(y, p), log_loss, [[tn, fp], [fn, tp]], self._calibration_error(y, p), brier, float(pred[0] == y[0]) if len(y) else 0.0, float((pred[:5] == y[:5]).mean()) if len(y) else 0.0)

    def profitability(self, equity_curve: list[float], trade_returns: list[float], fees_percent: float = 0.0) -> ProfitabilityMetrics:
        if len(equity_curve) < 2:
            return ProfitabilityMetrics(*([0.0] * 19))
        start, end = equity_curve[0], equity_curve[-1]
        net = (end / start - 1) * 100
        returns = np.array(trade_returns or [0.0])
        wins = returns[returns > 0]
        losses = returns[returns < 0]
        drawdown = self._max_drawdown(equity_curve)
        sharpe = float(returns.mean() / max(returns.std(), 1e-9) * sqrt(252))
        downside = losses.std() if len(losses) else 0.0
        sortino = float(returns.mean() / max(downside, 1e-9) * sqrt(252))
        return ProfitabilityMetrics(net, net, net / 12, net / max(len(equity_curve), 1), abs(wins.sum() / min(losses.sum(), -1e-9)) if len(losses) else float("inf"), len(wins) / max(len(returns), 1) * 100, float(wins.mean() * 100) if len(wins) else 0.0, float(losses.mean() * 100) if len(losses) else 0.0, drawdown, sharpe, sortino, net / max(abs(drawdown), 1e-9), abs((wins.mean() if len(wins) else 0) / min(losses.mean() if len(losses) else -1e-9, -1e-9)), net, net + fees_percent, net, len(wins) / max(len(returns), 1), float((np.array(equity_curve) <= start * 0.5).mean()))

    def _roc_auc(self, y: np.ndarray, p: np.ndarray) -> float | None:
        positives = p[y == 1]
        negatives = p[y == 0]
        if not len(positives) or not len(negatives):
            return None
        return float(sum((pos > negatives).sum() + 0.5 * (pos == negatives).sum() for pos in positives) / (len(positives) * len(negatives)))

    def _calibration_error(self, y: np.ndarray, p: np.ndarray, bins: int = 10) -> float:
        if not len(y):
            return 0.0
        total = 0.0
        for bucket in range(bins):
            lower, upper = bucket / bins, (bucket + 1) / bins
            mask = (p >= lower) & (p < upper if bucket < bins - 1 else p <= upper)
            if mask.any():
                total += abs(float(y[mask].mean()) - float(p[mask].mean())) * float(mask.mean())
        return total

    def _max_drawdown(self, equity_curve: list[float]) -> float:
        peak = equity_curve[0]
        worst = 0.0
        for value in equity_curve:
            peak = max(peak, value)
            worst = min(worst, (value / peak - 1) * 100)
        return abs(worst)
