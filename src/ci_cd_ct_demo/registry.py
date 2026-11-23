"""A dummy model registry: a JSON file of versions and aliases.

It stands in for the MLflow registry of the session-20 lab. Each version stores
the model itself (its threshold), so no artifact store is needed.
"""

import json
from pathlib import Path


def load(path: Path) -> dict:
    if not path.exists():
        return {"versions": {}, "aliases": {}}
    return json.loads(path.read_text())


def save(registry: dict, path: Path) -> None:
    path.write_text(json.dumps(registry, indent=2) + "\n")


def register(registry: dict, threshold: float, trained_on: str) -> str:
    """Adds a version and returns its number."""
    version = str(len(registry["versions"]) + 1)
    registry["versions"][version] = {
        "threshold": round(threshold, 4),
        "trained_on": trained_on,
    }
    return version


def set_alias(registry: dict, alias: str, version: str) -> None:
    registry["aliases"][alias] = version


def get_by_alias(registry: dict, alias: str) -> tuple[str, dict] | None:
    """Returns the version an alias points to and its entry, or None."""
    version = registry["aliases"].get(alias)
    if version is None:
        return None
    return version, registry["versions"][version]
