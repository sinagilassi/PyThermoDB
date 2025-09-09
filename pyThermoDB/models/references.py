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


class ReferenceThermoDB(BaseModel):
    """
    Model for reference thermodynamic database (ThermoDB).

    Attributes
    ----------
    reference : Dict[str, List[str]]
        Dictionary of references with their associated contents.
    contents : List[str]
        List of reference contents used for building the thermodynamic database.
    configs : Dict[str, Any]
        Reference configuration used for building the thermodynamic database.
    rules : Dict[str, Any]
        Reference rules generated from the reference configuration.
    labels : Optional[List[str]]
        List of labels used in the reference config.

    Notes
    -----
    - The `reference_configs` attribute holds the configuration details that guide how the thermodynamic data is structured and referenced.
    - The `reference_rules` attribute contains rules derived from the reference configurations, which may include mappings or transformations applied to the data.
    - The `labels` attribute is optional and can be used to tag or categorize the reference configurations for easier identification and retrieval.
    """
    reference: Dict[str, List[str]] = Field(
        ...,
        description="Dictionary of references with their associated contents."
    )
    contents: List[str] = Field(
        ...,
        description="List of reference contents used for building the thermodynamic database."
    )
    configs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Reference configuration used for building the thermodynamic database."
    )
    rules: Dict[str, Any] = Field(
        default_factory=dict,
        description="Reference rules generated from the reference configuration."
    )
    labels: Optional[List[str]] = Field(
        default_factory=list,
        description="List of labels used in the reference config."
    )
    ignore_labels: Optional[List[str]] = Field(
        default_factory=list,
        description="List of property labels to ignore state during the build."
    )
    ignore_props: Optional[List[str]] = Field(
        default_factory=list,
        description="List of property names to ignore state during the build."
    )


class ComponentReferenceThermoDB(BaseModel):
    """
    Model for component thermodynamic database (ThermoDB).

    Attributes
    ----------
    component : Component
        The component for which the thermodynamic database is built.
    reference_thermodb : ReferenceThermoDB
        Reference thermodynamic database.
    component_key : Literal['Name-State', 'Formula-State', 'Name', 'Formula', 'Name-Formula-State'], optional
        Key to identify the component in the reference content, by default 'Name-State'.
    """
    component: Component = Field(
        ...,
        description="The component for which the thermodynamic database is built."
    )
    reference_thermodb: ReferenceThermoDB = Field(
        ..., description="Reference thermodynamic database."
    )
    component_key: Literal[
        'Name-State', 'Formula-State', 'Name', 'Formula', 'Name-Formula-State'
    ] = Field(
        default='Name-State',
        description="Key to identify the component in the reference content."
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
