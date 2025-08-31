# import libs
from typing import (
    Any,
    List,
    Literal,
    Dict,
    Optional
)
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator
)


class Component(BaseModel):
    """Component model for input validation"""
    name: str = Field(..., description="Name of the component")
    formula: str = Field(..., description="Chemical formula of the component")
    state: str = Field(
        ...,
        description="State of the component: 'g' for gas, 'l' for liquid, 's' for solid"
    )
    mole_fraction: float = Field(
        default=1.0,
        description="Mole fraction of the component in a mixture, if applicable"
    )
