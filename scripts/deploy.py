"""A dummy deployment: says what it would deploy, and which model would serve.

A real CD job would push an image and restart a service. The model is not part
of what is deployed: the service resolves `champion` in the registry when it
starts.
"""

import argparse
from pathlib import Path

from ci_cd_ct_demo import registry


def process(wheel_path: Path, registry_path: Path, environment: str) -> None:
    print(f"deploying {wheel_path.name} to {environment}")
    champion = registry.get_by_alias(registry.load(registry_path), "champion")
    if champion is None:
        print("no champion in the registry: the service has no model to load")
        return
    version, entry = champion
    print(f"at startup the service loads champion -> v{version}")
    print(f"(threshold {entry['threshold']}, trained on {entry['trained_on']})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=Path("registry.json"))
    parser.add_argument("--environment", default="production")
    args = parser.parse_args()
    process(args.wheel, args.registry, args.environment)


if __name__ == "__main__":
    main()
