"""A dummy model: one feature `x`, and a threshold above which it predicts 1."""

import csv
from pathlib import Path


def load_rows(path: Path) -> list[tuple[float, int]]:
    """Reads a CSV with the columns `x` and `y`."""
    with open(path, newline="") as f:
        return [(float(row["x"]), int(row["y"])) for row in csv.DictReader(f)]


def fit(rows: list[tuple[float, int]]) -> float:
    """Returns the threshold halfway between the mean `x` of each class."""
    mean_0 = sum(x for x, y in rows if y == 0) / sum(1 for _, y in rows if y == 0)
    mean_1 = sum(x for x, y in rows if y == 1) / sum(1 for _, y in rows if y == 1)
    return (mean_0 + mean_1) / 2


def predict(threshold: float, x: float) -> int:
    return 1 if x >= threshold else 0


def accuracy(threshold: float, rows: list[tuple[float, int]]) -> float:
    return sum(predict(threshold, x) == y for x, y in rows) / len(rows)
