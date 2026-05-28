"""TableEquation-specific exceptions."""

from __future__ import annotations

from .table_errors import (
    TableCalculationError,
    TableEquationError,
    TableLookupError,
    TableParameterError,
    TableStructureError,
    TableValidationError,
)


class TableEquationStructureError(TableEquationError, TableStructureError):
    """The equation table structure is missing or malformed."""

    default_message = "Invalid equation table structure"


class TableEquationDefinitionError(TableEquationError, TableValidationError):
    """An equation definition is missing required fields or has invalid shape."""

    default_message = "Invalid equation definition"


class TableEquationLookupError(TableEquationError, TableLookupError):
    """A requested equation, argument, return, or custom integral was not found."""

    default_message = "Equation item was not found"


class TableEquationBodyError(TableEquationDefinitionError):
    """The equation body is missing or invalid."""

    default_message = "Equation body is invalid"


class TableEquationSymbolError(TableEquationDefinitionError):
    """Equation argument, parameter, or return symbols are invalid."""

    default_message = "Equation symbols are invalid"


class TableEquationParameterError(TableEquationError, TableParameterError):
    """Equation parameters are missing or invalid."""

    default_message = "Equation parameters are invalid"


class TableEquationCalculationError(TableEquationError, TableCalculationError):
    """Equation calculation failed."""

    default_message = "Equation calculation failed"


class TableEquationRangeError(TableEquationCalculationError):
    """Equation range calculation failed."""

    default_message = "Equation range calculation failed"


class TableEquationIntegralError(TableEquationCalculationError):
    """Equation integral calculation failed."""

    default_message = "Equation integral calculation failed"


class TableEquationDerivativeError(TableEquationCalculationError):
    """Equation derivative calculation failed."""

    default_message = "Equation derivative calculation failed"


__all__ = [
    "TableEquationStructureError",
    "TableEquationDefinitionError",
    "TableEquationLookupError",
    "TableEquationBodyError",
    "TableEquationSymbolError",
    "TableEquationParameterError",
    "TableEquationCalculationError",
    "TableEquationRangeError",
    "TableEquationIntegralError",
    "TableEquationDerivativeError",
]
