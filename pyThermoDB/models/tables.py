# import libs
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# SECTION: Define Table Models
# NOTE: Table Equation Block


class TableEquationBlock(BaseModel):
    """
    Table Equation Block Model Definition

    Attributes
    ----------
    id : int
        Equation ID (zero-based) which is unique within the table structure.
    body : List[str]
        Equation Body as List of Strings.
    args : Dict[str, Any]
        Equation Arguments defined as a dictionary including name, symbol, unit.
    parms : Dict[str, Any]
        Equation Parameters defined as a dictionary including name, symbol, unit.
    returns : Dict[str, Any]
        Equation Return Values defined as a dictionary including name, symbol, unit.
    body_integral : Optional[List[str]]
        Equation Body Integral as List of Strings.
    body_first_derivative : Optional[List[str]]
        Equation Body First Derivative as List of Strings.
    body_second_derivative : Optional[List[str]]
        Equation Body Second Derivative as List of Strings.
    """
    id: int = Field(
        ...,
        description="Equation ID (zero-based) which is unique within the table structure"
    )
    body: List[str] = Field(
        ...,
        description="Equation Body as List of Strings"
    )
    args: Dict[str, Any] = Field(
        default_factory=dict,
        description="Equation Arguments defined as a dictionary including name, symbol, unit"
    )
    parms: Dict[str, Any] = Field(
        default_factory=dict,
        description="Equation Parameters defined as a dictionary including name, symbol, unit"
    )
    returns: Dict[str, Any] = Field(
        default_factory=dict,
        description="Equation Return Values defined as a dictionary including name, symbol, unit"
    )
    body_integral: Optional[List[str]] = Field(
        None,
        description="Equation Body Integral as List of Strings"
    )
    body_first_derivative: Optional[List[str]] = Field(
        None,
        description="Equation Body First Derivative as List of Strings"
    )
    body_second_derivative: Optional[List[str]] = Field(
        None,
        description="Equation Body Second Derivative as List of Strings"
    )
