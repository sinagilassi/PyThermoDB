# import libs
import logging
from typing import Any, Dict, List, Optional, Union
# locals

# NOTE: logger setup
logger = logging.getLogger(__name__)


class TableConstants:
    def __init__(
        self,
        databook_name,
        table_name,
        table_data,
        table_values: Optional[List | Dict] = None,
        table_structure: Optional[Dict[str, Any]] = None
    ):
        # NOTE: set
        self.databook_name = databook_name
        self.table_name = table_name
        self.table_data = table_data
        self.table_values = table_values
        self.table_structure = table_structure
