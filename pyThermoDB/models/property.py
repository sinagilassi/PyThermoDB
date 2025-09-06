# import libs
from typing import Literal, Optional, Union
from pydantic import BaseModel, Field, ConfigDict
# locals


class PropertyMatch(BaseModel):
    """
    Class to check the availability of a property in the table data.
    """

    prop_id: str = Field(..., description="Property identifier (ID).")
    availability: bool = Field(
        False, description="True if the property is available, False otherwise."
    )
    search_mode: Optional[str] = Field(
        None, description="Search mode: 'SYMBOL', 'COLUMN', 'BOTH'."
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True
    )
