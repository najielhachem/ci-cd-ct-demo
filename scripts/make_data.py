"""Writes a dummy training set and holdout set.

Class 0 has `x` around `shift`, class 1 around `shift + 3`. A larger `shift`
is the drift that new data brings.
"""

import argparse
import csv
import random
from pathlib import Path


def sample(n_rows: int, shift: float, seed: int) -> list[tuple[float, int]]:
    rng = random.Random(seed)
    rows = []
    for _ in range(n_rows):
        y = rng.randint(0, 1)
        rows.append((round(rng.gauss(shift + 3 * y, 1.0), 3), y))
    return rows


def process(out_dir: Path, shift: float, seed: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    splits = {"train.csv": (200, seed), "holdout.csv": (100, seed + 1)}
    for name, (n_rows, split_seed) in splits.items():
        with open(out_dir / name, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["x", "y"])
            writer.writerows(sample(n_rows, shift, split_seed))
        print(f"wrote {out_dir / name}: {n_rows} rows, shift {shift}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path("datasets"))
    parser.add_argument("--shift", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    process(args.out_dir, args.shift, args.seed)


if __name__ == "__main__":
    main()
