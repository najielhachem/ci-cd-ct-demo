"""Trains a model and registers it with the alias `challenger`."""

import argparse
from pathlib import Path

from ci_cd_ct_demo import model, registry


def process(data_path: Path, registry_path: Path) -> None:
    rows = model.load_rows(data_path)
    threshold = model.fit(rows)

    reg = registry.load(registry_path)
    version = registry.register(reg, threshold, trained_on=str(data_path))
    registry.set_alias(reg, "challenger", version)
    registry.save(reg, registry_path)

    print(f"trained on {len(rows)} rows: threshold {threshold:.3f}")
    print(f"registered v{version} as challenger")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("datasets/train.csv"))
    parser.add_argument("--registry", type=Path, default=Path("registry.json"))
    args = parser.parse_args()
    process(args.data, args.registry)


if __name__ == "__main__":
    main()
