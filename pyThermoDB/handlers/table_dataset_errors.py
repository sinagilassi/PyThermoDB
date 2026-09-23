"""Dataset-specific exceptions for :mod:`pyThermoDB.core.tabledataset`."""

from .table_errors import (
    TableConversionError,
    TableDatasetError,
    TableLookupError,
    TableStructureError,
    TableValidationError,
)


class TableDatasetStructureError(TableDatasetError, TableStructureError):
    """The dataset schema is missing or structurally invalid."""


class TableDatasetDefinitionError(TableDatasetError, TableValidationError):
    """The dataset metadata or values are inconsistent."""


class TableDatasetFormatError(TableDatasetDefinitionError):
    """A dataset value uses an unsupported source format."""


class TableDatasetLookupError(TableDatasetError, TableLookupError):
    """A requested dataset column, symbol, or identifier was not found."""


class TableDatasetConversionError(TableDatasetError, TableConversionError):
    """A dataset conversion operation failed."""


class TableDatasetFrameError(TableDatasetError):
    """A supplied or generated dataset DataFrame is invalid."""


__all__ = [
    "TableDatasetStructureError",
    "TableDatasetDefinitionError",
    "TableDatasetFormatError",
    "TableDatasetLookupError",
    "TableDatasetConversionError",
    "TableDatasetFrameError",
]
