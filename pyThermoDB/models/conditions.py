# import libs
from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)


class Temperature(BaseModel):
    """Temperature model for input validation"""
    value: float = Field(..., description="Temperature value")
    unit: str = Field(..., description="Temperature unit, e.g., 'K', 'C', 'F'")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class Pressure(BaseModel):
    """Pressure model for input validation"""
    value: float = Field(..., description="Pressure value")
    unit: str = Field(
        ...,
        description="Pressure unit, e.g., 'bar', 'atm', 'Pa'"
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
