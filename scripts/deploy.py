"""A dummy deployment: says what it would deploy, and which model would serve.

A real CD job would push an image and restart a service. The model is not part
of the build: the service resolves `champion` in the registry when it starts.
So a new build is deployed with `--wheel`, and a new champion without it, by
restarting the build already running.
"""

import argparse
from pathlib import Path

from ci_cd_ct_demo import registry


def process(wheel_path: Path | None, registry_path: Path, environment: str) -> None:
    if wheel_path is None:
        print(f"no new build: restarting the running build in {environment}")
    else:
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
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--registry", type=Path, default=Path("registry.json"))
    parser.add_argument("--environment", default="production")
    args = parser.parse_args()
    process(args.wheel, args.registry, args.environment)


if __name__ == "__main__":
    main()
