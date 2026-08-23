"""Configuration loading utilities for EAR-RAG.

The loader reads the repository's YAML configuration without downloading models,
datasets, or adding runtime dependencies beyond PyYAML.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_DEFAULT_CONFIG_RELATIVE_PATH = Path("configs") / "config.yaml"
_CONFIG_PATH = _PROJECT_ROOT / _DEFAULT_CONFIG_RELATIVE_PATH


def _validate_config_path(config_path: Path) -> None:
    """Raise an informative error when a requested configuration is absent."""
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")


def get_config_path() -> Path:
    """Return the repository-relative default configuration as an absolute path."""
    return _CONFIG_PATH


def load_config(custom_path: str | Path | None = None) -> dict[str, Any]:
    """Load the default YAML configuration or a caller-supplied configuration."""
    path = Path(custom_path) if custom_path is not None else _CONFIG_PATH
    _validate_config_path(path)

    with path.open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    if config is None:
        return {}
    if not isinstance(config, dict):
        raise ValueError(f"Configuration root must be a mapping: {path}")
    return config


def get_config_value(
    config: dict[str, Any],
    key: str,
    default: Any = None,
) -> Any:
    """Return a value addressed by a dotted key, or ``default`` if absent."""
    value: Any = config
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value


def get_project_name() -> str:
    """Return the configured project name."""
    return str(get_config_value(load_config(), "project.name", "EAR-RAG"))


def get_project_version() -> str:
    """Return the configured project version."""
    return str(get_config_value(load_config(), "project.version", "0.1.0"))


def get_default_top_k() -> int:
    """Return the configured default retrieval depth."""
    return int(get_config_value(load_config(), "retrieval.default_top_k", 5))


def get_max_top_k() -> int:
    """Return the configured maximum retrieval depth."""
    return int(get_config_value(load_config(), "retrieval.max_top_k", 20))


def get_sufficient_threshold() -> float:
    """Return the evidence-sufficiency threshold, using its documented default."""
    return float(
        get_config_value(load_config(), "evidence_assessment.sufficient_threshold", 0.7)
    )


def get_uncertain_threshold() -> float:
    """Return the evidence-uncertainty threshold, using its documented default."""
    return float(
        get_config_value(load_config(), "evidence_assessment.uncertain_threshold", 0.4)
    )
