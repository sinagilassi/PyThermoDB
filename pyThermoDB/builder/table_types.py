"""Shared type definitions for component table building and exporting."""

from typing import Any, TypeAlias

from ..core import (
    TableConstants,
    TableData,
    TableDataset,
    TableEquation,
    TableInteractionData,
    TableMatrixData,
    TableMatrixEquation,
)


TablePropertyValue: TypeAlias = (
    TableData
    | dict[Any, Any]
    | TableMatrixData
    | TableInteractionData
    | TableConstants
    | TableDataset
)
"""A supported non-equation property value."""

TableEquationValue: TypeAlias = TableEquation | TableMatrixEquation
"""A supported equation/function value."""

TableValue: TypeAlias = TablePropertyValue | TableEquationValue
"""A supported value in a component table store."""

TableStore: TypeAlias = dict[str, TableValue]
"""A mapping of table names to supported component table values."""
