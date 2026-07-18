import pytest
from app.ml.scenarios import DEFAULT_MARKET_SCENARIOS
from app.ml.validation import TimeSeriesValidator


def test_default_scenarios_include_crash_and_recovery() -> None:
    names = {scenario.name for scenario in DEFAULT_MARKET_SCENARIOS}
    assert "COVID Crash" in names
    assert "Recovery Period" in names


def test_time_series_validator_preserves_ordered_splits() -> None:
    splits = TimeSeriesValidator().walk_forward(size=120, min_train=60, validation_size=10)
    assert splits
    for split in splits:
        assert split.train_start <= split.train_end < split.validation_start <= split.validation_end


def test_random_kfold_is_not_supported() -> None:
    validator = TimeSeriesValidator()
    with pytest.raises(AttributeError):
        getattr(validator, "random_kfold")
