# import libs
from typing import Literal, Optional
from dataclasses import dataclass
# locals
from ..models.configs import BuildType


@dataclass
class AppConfig:
    # ! whether to include data tables in TableData
    include_data: bool = True

    # ! build type
    build_type: Optional[BuildType] = None

    # ! component identifiers
    component_name: Optional[str] = None
    component_formula: Optional[str] = None
    component_state: Optional[str] = None


# this is like get_settings() in FastAPI
_current_config: AppConfig | None = None


def set_config(cfg: AppConfig) -> None:
    # ! set global config
    global _current_config
    _current_config = cfg


def get_config() -> AppConfig:
    if _current_config is None:
        # default config if not set
        return AppConfig()
    return _current_config
