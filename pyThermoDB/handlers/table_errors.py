"""Table-specific exceptions for pyThermoDB core table objects."""

from __future__ import annotations

from typing import Any, Mapping

from .errors import PyThermoDBError


class TableError(PyThermoDBError):
    """Base exception for pyThermoDB table operations."""

    default_message = "Table operation failed"

    def __init__(
        self,
        message: str | None = None,
        *,
        table_name: str | int | None = None,
        databook_name: str | int | None = None,
        code: str | int | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        table_context = dict(context or {})
        if databook_name is not None:
            table_context.setdefault("databook_name", databook_name)
        if table_name is not None:
            table_context.setdefault("table_name", table_name)
        super().__init__(message, code=code, context=table_context)


class TableStructureError(TableError):
    """A table declaration is missing required structure or has invalid shape."""

    default_message = "Invalid table structure"


class TableColumnError(TableStructureError, KeyError):
    """A required table column declaration or column value is missing."""

    default_message = "Table column was not found"


class TableSymbolError(TableStructureError):
    """A required table symbol declaration or symbol lookup failed."""

    default_message = "Table symbol operation failed"


class TableUnitError(TableStructureError):
    """A required table unit declaration or unit lookup failed."""

    default_message = "Table unit operation failed"


class TableValidationError(TableError, ValueError):
    """A table input, option, or value is invalid."""

    default_message = "Table validation failed"


class TableLookupError(TableError, LookupError):
    """A requested table item, property, component, or equation was not found."""

    default_message = "Table item was not found"


class TableDataError(TableError):
    """TableData operation failed."""

    default_message = "Table data operation failed"


class TableEquationError(TableError):
    """TableEquation operation failed."""

    default_message = "Table equation operation failed"


class TableMatrixDataError(TableDataError):
    """TableMatrixData operation failed."""

    default_message = "Table matrix data operation failed"


class TableMatrixEquationError(TableEquationError):
    """TableMatrixEquation operation failed."""

    default_message = "Table matrix equation operation failed"


class TableConstantsError(TableError):
    """TableConstants operation failed."""

    default_message = "Table constants operation failed"


class TableUtilError(TableError):
    """Table utility operation failed."""

    default_message = "Table utility operation failed"


class TableCalculationError(TableError):
    """A table equation calculation, integral, or derivative failed."""

    default_message = "Table calculation failed"


class TableParameterError(TableError):
    """Equation or matrix-equation parameters are missing or invalid."""

    default_message = "Table parameters are invalid"


class TableConversionError(TableError):
    """A table conversion or serialization operation failed."""

    default_message = "Table conversion failed"


__all__ = [
    "TableError",
    "TableStructureError",
    "TableColumnError",
    "TableSymbolError",
    "TableUnitError",
    "TableValidationError",
    "TableLookupError",
    "TableDataError",
    "TableEquationError",
    "TableMatrixDataError",
    "TableMatrixEquationError",
    "TableConstantsError",
    "TableUtilError",
    "TableCalculationError",
    "TableParameterError",
    "TableConversionError",
]
