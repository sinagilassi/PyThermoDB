# import packages/modules
from typing import TypedDict, List, Optional, Union, Dict, Any
import numpy as np


class DataBookTableTypes(TypedDict):
    """Databook Table Types Definition"""
    table_id: Optional[int | str]
    table: str
    description: Optional[str]
    equations: Optional[List[str] | Dict[str, Any]]
    data: Optional[List[str] | Dict[str, Any]]
    matrix_equations: Optional[List[str] | Dict[str, Any]]
    matrix_data: Optional[List[str] | Dict[str, Any]]
    table_type: Optional[str]
    table_values: Optional[List[Any] | Dict[str, Any]]
    table_structure: Optional[Dict[str, Any]]


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


class DataResult(TypedDict):
    """Data Result Type Definition"""
    property_name: Optional[str]
    symbol: Optional[str]
    unit: Optional[str]
    value: Optional[Union[str, float]]
    message: Optional[str]
    databook_name: Optional[Union[str, int]]
    table_name: Optional[Union[str, int]]


class EquationResult(TypedDict):
    """Equation Result Type Definition"""
    equation_name: Optional[str]
    symbol: Optional[str]
    unit: Optional[str]
    value: Optional[Union[str, float, dict, np.ndarray]]
    message: Optional[str]
    databook_name: Optional[Union[str, int]]
    table_name: Optional[Union[str, int]]
