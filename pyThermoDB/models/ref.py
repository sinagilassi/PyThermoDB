# import packages/modules
from typing import TypedDict, List, Optional


class DataBookTableTypes(TypedDict):
    """Databook Table Types Definition"""
    table: str
    equations: Optional[List[str]]
    data: Optional[List[str]]
    matrix_equations: Optional[List[str]]
    matrix_data: Optional[List[str]]


class PayLoadType(TypedDict):
    """PayLoad Type Definition"""
    header: List
    symbol: List
    unit: List
    records: List


class MatrixDataType(TypedDict):
    """Matrix Data Definition"""
    COLUMNS: List[str]
    SYMBOL: List[str]
    UNIT: Optional[List[str | int]]
    CONVERSION: Optional[List[str | int]]


class DataResultType(TypedDict):
    """Data Result Type Definition"""
    value: Optional[str | float]
    unit: Optional[str | float]
    symbol: Optional[str | float]
