"""Public configuration API for EAR-RAG."""

from .loader import (
    get_config_value,
    get_config_path,
    get_default_top_k,
    get_max_top_k,
    get_project_name,
    get_project_version,
    get_sufficient_threshold,
    get_uncertain_threshold,
    load_config,
)

__all__ = [
    "get_config_value",
    "get_config_path",
    "get_default_top_k",
    "get_max_top_k",
    "get_project_name",
    "get_project_version",
    "get_sufficient_threshold",
    "get_uncertain_threshold",
    "load_config",
]
