# import packages/modules
from enum import Enum


class TableTypes(Enum):
    """
    Enum class for table types

    Attributes
    ----------
    EQUATIONS : str
        Table type for equations
    DATA : str
        Table type for data
    MATRIX_EQUATIONS : str
        Table type for matrix equations
    MATRIX_DATA : str
        Table type for matrix data
    INTERACTION_DATA : str
        Table type for interaction data
    CONSTANTS : str
        Table type for constants
    DATASET : str
        Table type for dataset
    """
    EQUATIONS = "equations"
    DATA = "data"
    MATRIX_EQUATIONS = "matrix_equations"
    MATRIX_DATA = "matrix_data"
    INTERACTION_DATA = "interaction_data"
    CONSTANTS = "constants"
    DATASET = "dataset"
