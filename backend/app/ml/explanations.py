from __future__ import annotations

import json
from typing import Any

from app.services.llm import GroqLLMService


class MLExplanationService:
    """Uses Groq only to explain deterministic ML artifacts, never to predict prices or scores."""

    def __init__(self, llm: GroqLLMService | None = None) -> None:
        self.llm = llm or GroqLLMService()

    async def explain(self, api_key: str, model: str, artifact: dict[str, Any], question: str = "Explain this ML research result.") -> str:
        safe_artifact = self._redact_and_bound(artifact)
        context = (
            "The following JSON was produced by Nimrod's deterministic ML engine. "
            "Do not create new predictions, prices, probabilities, scores, or financial advice. "
            "Explain uncertainty, leakage controls, model limitations, risk, and how to interpret the metrics.\n"
            f"{json.dumps(safe_artifact, default=str)}"
        )
        return await self.llm.complete(api_key, model, question, context)

    def local_explanation(self, artifact: dict[str, Any]) -> str:
        models = artifact.get("trained_models") or []
        skipped = artifact.get("skipped_models") or {}
        return (
            "The ML engine generated this result with deterministic features and time-series leakage checks. "
            f"Trained models: {', '.join(models) if models else 'none'}. "
            f"Skipped models: {len(skipped)}. Interpret all scores as experimental and uncertain; they do not guarantee profit."
        )

    def _redact_and_bound(self, artifact: dict[str, Any]) -> dict[str, Any]:
        allowed = {"disclaimer", "trained_models", "skipped_models", "validation_scores", "feature_importance", "reproducibility", "equity_curve", "trades", "warnings"}
        redacted = {key: value for key, value in artifact.items() if key in allowed}
        if isinstance(redacted.get("equity_curve"), list):
            curve = redacted["equity_curve"]
            redacted["equity_curve"] = curve[:10] + (["..."] if len(curve) > 10 else [])
        if isinstance(redacted.get("trades"), list):
            redacted["trades"] = redacted["trades"][:10]
        return redacted
