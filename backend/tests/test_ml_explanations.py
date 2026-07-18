from app.ml.explanations import MLExplanationService


def test_ml_explanation_redacts_and_bounds_large_payload() -> None:
    payload = {"equity_curve": list(range(20)), "trades": [{"id": index} for index in range(20)], "groq_api_key": "secret"}
    bounded = MLExplanationService()._redact_and_bound(payload)
    assert "groq_api_key" not in bounded
    assert bounded["equity_curve"][-1] == "..."
    assert len(bounded["trades"]) == 10


def test_local_explanation_never_claims_guaranteed_profit() -> None:
    explanation = MLExplanationService().local_explanation({"trained_models": ["random_forest"], "skipped_models": {}})
    assert "do not guarantee profit" in explanation.lower()
