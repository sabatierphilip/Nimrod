import pandas as pd


class DataLeakageError(RuntimeError):
    pass


class DataLeakageGuard:
    """Validates chronological splits and target horizon alignment before training."""

    def validate(self, features: pd.DataFrame, labels: pd.Series, horizon: int, train_end_position: int) -> None:
        if not features.index.is_monotonic_increasing or not labels.index.is_monotonic_increasing:
            raise DataLeakageError("features and labels must be sorted chronologically")
        if not features.index.equals(labels.index):
            raise DataLeakageError("features and labels must share identical point-in-time indices")
        if horizon < 1:
            raise DataLeakageError("prediction horizon must be at least one period")
        if train_end_position >= len(features) - horizon:
            raise DataLeakageError("training split overlaps with future labels required by the prediction horizon")
        if features.iloc[: train_end_position + 1].isna().any().any():
            raise DataLeakageError("training features contain missing values that could trigger unsafe imputation")
