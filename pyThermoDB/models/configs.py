# import libs
from typing_extensions import TypedDict
from typing import Literal, Optional


# SECTION: component configuration
class ComponentConfig(TypedDict, total=False):
    """Component configuration model"""
    databook: str
    table: str
    mode: str
    label: str  # optional
    labels: dict[str, str]  # optional


# SECTION: Constants Configuration
# ! move to pythermodb_settings
class ConstantsConfig(TypedDict, total=False):
    """Constants configuration model"""
    databook: str
    table: str
    mode: str
    label: str  # optional
    labels: dict[str, str]  # optional


# SECTION: App config configuration
BuildType = Literal['single', 'mixture', 'constants']
