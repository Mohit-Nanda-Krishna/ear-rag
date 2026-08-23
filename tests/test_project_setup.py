"""Smoke test to verify the EAR-RAG project can be imported successfully."""

import sys
import os

def test_package_importable():
    """Verify that the ear_rag package can be imported."""
    # Add src to path
    src_path = os.path.join(os.path.dirname(__file__), "..", "src")
    sys.path.insert(0, os.path.abspath(src_path))

    import ear_rag
    assert ear_rag.__version__ == "0.1.0"


def test_config_exists():
    """Verify that the configuration file exists."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "config.yaml")
    assert os.path.exists(config_path)