"""Shared type definitions for component table building and exporting."""

from typing import Any, TypeAlias

from ..core import (
    TableConstants,
    TableData,
    TableEquation,
    TableInteractionData,
    TableMatrixData,
    TableMatrixEquation,
)


TableValue: TypeAlias = (
    TableData
    | TableEquation
    | dict[Any, Any]
    | TableMatrixData
    | TableInteractionData
    | TableMatrixEquation
    | TableConstants
)
"""A supported value in a component table store."""

TableStore: TypeAlias = dict[str, TableValue]
"""A mapping of table names to supported component table values."""
