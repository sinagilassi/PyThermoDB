"""TableMatrixData-specific exceptions."""

from __future__ import annotations

from .table_errors import (
    TableConversionError,
    TableLookupError,
    TableMatrixDataError,
    TableStructureError,
    TableValidationError,
)


class TableMatrixDataStructureError(TableMatrixDataError, TableStructureError):
    """The matrix-data table structure is missing or malformed."""

    default_message = "Invalid matrix data table structure"


class TableMatrixDataDefinitionError(TableMatrixDataError, TableValidationError):
    """A matrix-data definition, mode, or option is invalid."""

    default_message = "Invalid matrix data definition"


class TableMatrixDataLookupError(TableMatrixDataError, TableLookupError):
    """A matrix-data component, mixture, property, or record was not found."""

    default_message = "Matrix data item was not found"


class TableMatrixDataFormatError(TableMatrixDataDefinitionError):
    """A matrix-data property name, symbol, or output format is invalid."""

    default_message = "Invalid matrix data format"


class TableMatrixDataFrameError(TableMatrixDataError):
    """The matrix data source is not a valid pandas DataFrame."""

    default_message = "Matrix data source is invalid"


class TableMatrixDataGenerationError(TableMatrixDataError):
    """Generating matrix-data derived records failed."""

    default_message = "Matrix data generation failed"


class TableMatrixDataConversionError(TableMatrixDataError, TableConversionError):
    """Converting or serializing matrix-data content failed."""

    default_message = "Matrix data conversion failed"


__all__ = [
    "TableMatrixDataStructureError",
    "TableMatrixDataDefinitionError",
    "TableMatrixDataLookupError",
    "TableMatrixDataFormatError",
    "TableMatrixDataFrameError",
    "TableMatrixDataGenerationError",
    "TableMatrixDataConversionError",
]
