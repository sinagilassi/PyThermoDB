# import libs
from typing import (
    Literal,
    Dict,
    List,
    Optional,
    Any,
)
from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)


class Component(BaseModel):
    """Component model for input validation"""
    name: str = Field(..., description="Name of the component")
    formula: str = Field(..., description="Chemical formula of the component")
    state: Literal['g', 'l', 's', 'aq'] = Field(
        ...,
        description="State of the component: 'g' for gas, 'l' for liquid, 's' for solid, 'aq' for aqueous"
    )
    mole_fraction: float = Field(
        default=1.0,
        description="Mole fraction of the component in a mixture, if applicable"
    )


class ComponentReferenceThermoDB(BaseModel):
    """
    Model for component thermodynamic database (ThermoDB).

    Attributes
    ----------
    component : Component
        The component for which the thermodynamic database is built.
    reference_content : List[str]
        List of reference contents (YAML format) used for building the thermodynamic database.
    reference_configs : Dict[str, Any]
        Reference configuration used for building the thermodynamic database.
    reference_rules : Dict[str, Dict[str, str]]
        Reference rules generated from the reference configuration.
    labels : Optional[List[str]]
        List of labels used in the reference config.

    Notes
    -----
    - The `reference_configs` attribute holds the configuration details that guide how the thermodynamic data is structured and referenced.
    - The `reference_rules` attribute contains rules derived from the reference configurations, which may include mappings or transformations applied to the data.
    - The `labels` attribute is optional and can be used to tag or categorize the reference configurations for easier identification and retrieval.
    """
    component: Component = Field(
        ...,
        description="The component for which the thermodynamic database is built."
    )
    reference_content: List[str] = Field(
        ...,
        description="List of reference contents (YAML format) used for building the thermodynamic database."
    )
    reference_configs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Reference configuration used for building the thermodynamic database."
    )
    reference_rules: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Reference rules generated from the reference configuration."
    )
    labels: Optional[List[str]] = Field(
        default_factory=list,
        description="List of labels used in the reference config."
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
