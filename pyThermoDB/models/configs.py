# import libs
from typing_extensions import TypedDict


class ComponentConfig(TypedDict, total=False):
    """Component configuration model"""
    databook: str
    table: str
    mode: str
    label: str  # optional
    labels: dict[str, str]  # optional
