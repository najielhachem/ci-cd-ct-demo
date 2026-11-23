"""The offline promotion gate.

Scores `champion` and `challenger` on the same holdout set, and moves
`champion` to the challenger only if it wins by at least `min_gain`.
"""

import argparse
from pathlib import Path

from ci_cd_ct_demo import model, registry


def process(holdout_path: Path, registry_path: Path, min_gain: float) -> None:
    rows = model.load_rows(holdout_path)
    reg = registry.load(registry_path)
    challenger_version, challenger = registry.get_by_alias(reg, "challenger")
    challenger_score = model.accuracy(challenger["threshold"], rows)
    print(f"challenger v{challenger_version}: accuracy {challenger_score:.3f}")

    champion = registry.get_by_alias(reg, "champion")
    if champion is None:
        print("no champion yet: promoting the challenger")
    else:
        champion_version, champion_entry = champion
        champion_score = model.accuracy(champion_entry["threshold"], rows)
        print(f"champion   v{champion_version}: accuracy {champion_score:.3f}")
        if challenger_score - champion_score < min_gain:
            print(f"gain below {min_gain}: champion stays v{champion_version}")
            return

    registry.set_alias(reg, "champion", challenger_version)
    registry.save(reg, registry_path)
    print(f"champion -> v{challenger_version}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--holdout", type=Path, default=Path("datasets/holdout.csv"))
    parser.add_argument("--registry", type=Path, default=Path("registry.json"))
    parser.add_argument("--min-gain", type=float, default=0.02)
    args = parser.parse_args()
    process(args.holdout, args.registry, args.min_gain)


if __name__ == "__main__":
    main()
