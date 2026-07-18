from dataclasses import dataclass


@dataclass(frozen=True)
class TimeSeriesSplit:
    train_start: int
    train_end: int
    validation_start: int
    validation_end: int


class TimeSeriesValidator:
    """Provides time-series validation. Random K-Fold is intentionally unsupported."""

    def expanding_window(self, size: int, min_train: int, validation_size: int, step: int) -> list[TimeSeriesSplit]:
        splits: list[TimeSeriesSplit] = []
        train_end = min_train - 1
        while train_end + validation_size < size:
            splits.append(TimeSeriesSplit(0, train_end, train_end + 1, train_end + validation_size))
            train_end += step
        return splits

    def rolling_window(self, size: int, train_size: int, validation_size: int, step: int) -> list[TimeSeriesSplit]:
        splits: list[TimeSeriesSplit] = []
        start = 0
        while start + train_size + validation_size <= size:
            splits.append(TimeSeriesSplit(start, start + train_size - 1, start + train_size, start + train_size + validation_size - 1))
            start += step
        return splits

    def walk_forward(self, size: int, min_train: int, validation_size: int) -> list[TimeSeriesSplit]:
        return self.expanding_window(size, min_train, validation_size, validation_size)

    def blocked(self, size: int, blocks: int = 5) -> list[TimeSeriesSplit]:
        block_size = max(size // blocks, 1)
        splits: list[TimeSeriesSplit] = []
        for block in range(1, blocks):
            validation_start = block * block_size
            validation_end = min(validation_start + block_size - 1, size - 1)
            splits.append(TimeSeriesSplit(0, validation_start - 1, validation_start, validation_end))
        return splits
