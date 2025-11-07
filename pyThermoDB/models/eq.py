# import libs
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict  # only in v2


class VariableMeta(BaseModel):
    """
    Variable Metadata Definition

    Attributes
    ----------
    name : str
        Name of the variable.
    symbol : str
        Symbol of the variable.
    unit : str
        Unit of the variable.
    """
    name: str
    symbol: str
    unit: str


class EquationDefinition(BaseModel):
    """
    Equation Definition Model

    Attributes
    ----------
    id : int
        Unique identifier for the equation.
    args : Dict[str, VariableMeta]
        Dictionary of argument variable metadata.
    parms : Dict[str, VariableMeta]
        Dictionary of parameter variable metadata.
    body : List[str]
        List of strings representing the body of the equation.
    returns : Dict[str, VariableMeta]
        Dictionary of return variable metadata.
    """
    id: int = Field(alias='id')
    args: Optional[Dict[str, VariableMeta]] = Field(
        default=None,
        description="Dictionary of argument variable metadata.",
        alias='args'
    )
    parms: Optional[Dict[str, VariableMeta]] = Field(
        default=None,
        description="Dictionary of parameter variable metadata.",
        alias='parms'
    )
    body: List[str] = Field(
        default_factory=list,
        description="List of strings representing the body of the equation.",
        alias='body'
    )
    returns: Optional[Dict[str, VariableMeta]] = Field(
        default=None,
        description="Dictionary of return variable metadata.",
        alias='returns'
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="allow"
    )
