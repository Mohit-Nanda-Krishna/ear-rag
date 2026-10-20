"""Smoke test to verify the EAR-RAG project can be imported successfully."""

import os
from pathlib import Path
import subprocess
import sys

def test_package_importable():
    """Verify that the ear_rag package can be imported."""
    import ear_rag
    assert ear_rag.__version__ == "0.1.0"
    assert Path(ear_rag.__file__).resolve() == (
        Path(__file__).resolve().parents[1] / "src" / "ear_rag" / "__init__.py"
    )


def test_installed_package_imports_outside_repository(tmp_path):
    """Editable installation must work without pytest or PYTHONPATH helping it."""
    result = subprocess.run(
        [sys.executable, "-I", "-c",
         "import ear_rag, ear_rag.data, ear_rag.demo; "
         "from ear_rag.config import load_config; "
         "assert load_config()['project']['name'] == 'EAR-RAG'; "
         "print(ear_rag.__file__)"],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    expected = Path(__file__).resolve().parents[1] / "src" / "ear_rag" / "__init__.py"
    assert Path(result.stdout.strip()).resolve() == expected


def test_config_exists():
    """Verify that the configuration file exists."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "config.yaml")
    assert os.path.exists(config_path)
