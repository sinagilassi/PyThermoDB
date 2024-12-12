# import packages/modules
from typing import TypedDict, List, Optional


class DataBookTableTypes(TypedDict):
    """Databook Table Types Definition"""
    table: str
    equations: Optional[List[str]]
    data: Optional[List[str]]
    matrix_equations: Optional[List[str]]
    matrix_data: Optional[List[str]]
