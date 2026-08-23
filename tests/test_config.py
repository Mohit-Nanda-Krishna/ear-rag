"""Tests for EAR-RAG configuration loader.

Verifies that config.yaml can be loaded and that required sections and
values exist with expected types.
"""

import pytest

from ear_rag.config.loader import (
    load_config, get_config_value, get_project_name, get_project_version,
    get_default_top_k, get_max_top_k, get_sufficient_threshold,
    get_uncertain_threshold,
)


def test_config_file_loads():
    """config.yaml can be loaded."""
    config = load_config()
    assert config is not None
    assert isinstance(config, dict)


def test_project_name():
    """Configuration has project name."""
    name = get_project_name()
    assert name == "EAR-RAG"


def test_project_version():
    """Configuration has project version."""
    version = get_project_version()
    assert version == "0.1.0"


def test_default_top_k():
    """Retrieval default_top_k has expected type."""
    k = get_default_top_k()
    assert isinstance(k, int)
    assert k > 0


def test_max_top_k():
    """Retrieval max_top_k has expected type."""
    k = get_max_top_k()
    assert isinstance(k, int)
    assert k > 0


def test_sufficient_threshold():
    """Evidence assessment sufficient_threshold has expected type."""
    t = get_sufficient_threshold()
    assert isinstance(t, float)
    assert 0.0 <= t <= 1.0


def test_uncertain_threshold():
    """Evidence assessment uncertain_threshold has expected type."""
    t = get_uncertain_threshold()
    assert isinstance(t, float)
    assert 0.0 <= t <= 1.0


def test_config_has_required_sections():
    """Configuration has required top-level sections."""
    config = load_config()
    required_sections = [
        "project", "data", "retrieval", "models", "evaluation", "logging"
    ]
    for section in required_sections:
        assert section in config, f"Missing config section: {section}"


def test_retrieval_section_has_top_k():
    """Retrieval section has top_k configuration."""
    config = load_config()
    assert "default_top_k" in config.get("retrieval", {})
    assert "max_top_k" in config.get("retrieval", {})