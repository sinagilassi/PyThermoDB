# import packages/modules
from enum import Enum


class TableTypes(Enum):
    """Enum class for table types"""
    EQUATIONS = "equations"
    DATA = "data"
    MATRIX_EQUATIONS = "matrix_equations"
    MATRIX_DATA = "matrix_data"
