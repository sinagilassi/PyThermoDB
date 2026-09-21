"""TableInteractionData-specific exceptions."""
from __future__ import annotations
from .table_errors import TableConversionError, TableInteractionDataError, TableLookupError, TableStructureError, TableValidationError

class TableInteractionDataStructureError(TableInteractionDataError, TableStructureError):
    default_message = "Invalid interaction-data table structure"
class TableInteractionDataDefinitionError(TableInteractionDataError, TableValidationError):
    default_message = "Invalid interaction-data definition"
class TableInteractionDataLookupError(TableInteractionDataError, TableLookupError):
    default_message = "Interaction-data item was not found"
class TableInteractionDataFormatError(TableInteractionDataDefinitionError):
    default_message = "Invalid interaction-data format"
class TableInteractionDataFrameError(TableInteractionDataError):
    default_message = "Interaction-data source is not a valid pandas DataFrame"
class TableInteractionDataGenerationError(TableInteractionDataError):
    default_message = "Interaction-data generation failed"
class TableInteractionDataConversionError(TableInteractionDataError, TableConversionError):
    default_message = "Interaction-data conversion failed"

__all__ = ["TableInteractionDataStructureError", "TableInteractionDataDefinitionError", "TableInteractionDataLookupError", "TableInteractionDataFormatError", "TableInteractionDataFrameError", "TableInteractionDataGenerationError", "TableInteractionDataConversionError"]