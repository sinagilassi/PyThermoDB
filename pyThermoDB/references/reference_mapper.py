# import libs
import logging
from typing import (
    Literal,
    Dict,
    List,
    Optional,
    Union,
    Any,
)
# local
from .checker import ReferenceChecker
from ..models import Component, ComponentReferenceThermoDB

# NOTE: set logger
logger = logging.getLogger(__name__)


def component_reference_mapper(
    component: Component,
    reference_content: str,
    component_key: Literal[
        'Name-State', 'Formula-State'
    ] = 'Formula-State',
    add_label: Optional[bool] = True,
    check_labels: Optional[bool] = True,
    **kwargs
) -> ComponentReferenceThermoDB:
    '''
    Build component thermodynamic databook (thermodb) including data and equations.

    Parameters
    ----------
    component : Component
        An instance of the Component model containing details about the component.
    reference_content : str
        String content of the reference (YAML format) containing databook and tables.
    component_key : Literal['Name-State', 'Formula-State'], optional
        Key to identify the component in the reference content, by default 'Formula-State'
    add_label : Optional[bool], optional
        Whether to add labels to the component reference config, by default True
    check_labels : Optional[bool], optional
        Whether to check labels in the component reference config, by default True
    **kwargs
        Additional keyword arguments.
        - ignore_state_props: Optional[List[str]]
            List of property names to ignore state during the build. By default, None.

    Returns
    -------
    ComponentReferenceThermoDB
        An instance of ComponentReferenceThermoDB containing the built thermodynamic databook and reference details.

    Notes
    -----
    - The `reference_content` should be a valid YAML string containing the necessary databook and table information.
    - The function utilizes the `ReferenceChecker` class to parse and validate the reference content.
    - The built `ComponentThermoDB` object includes the component details, the thermodynamic databook, and the reference configuration used.
    - The `add_label` and `check_labels` parameters help in managing the reference configuration for the component. In this context, labels defined in the reference are compared with the PyThermoDB labels (symbols) to ensure consistency.
    '''
    try:
        # NOTE: kwargs
        ignore_state_props: Optional[List[str]] = kwargs.get(
            'ignore_state_props', None
        )
        # set default if None
        if ignore_state_props is None:
            ignore_state_props = []

        # NOTE: check inputs
        if not isinstance(component, Component):
            raise TypeError("component must be an instance of Component")

        if not isinstance(reference_content, str) or not reference_content.strip():
            raise ValueError("reference_content must be a non-empty string")

        # SECTION: extract component details
        component_name = component.name.strip()
        component_formula = component.formula.strip()
        component_state = component.state.strip()

        # NOTE: check component_state
        # component_state = cast(DEFAULT_COMPONENT_STATES, component_state)

        # SECTION: create ReferenceChecker instance
        ReferenceChecker_ = ReferenceChecker(reference_content)

        # NOTE: load all databooks
        databooks: List[str] = ReferenceChecker_.get_databook_names()

        # check databooks
        if not isinstance(databooks, list) or not databooks:
            raise ValueError("No databooks found in the reference content.")

        # NOTE: component reference config
        component_reference_configs = ReferenceChecker_.get_component_reference_configs(
            component_name=component_name,
            component_formula=component_formula,
            component_state=component_state,
            add_label=add_label,
            check_labels=check_labels,
            component_key=component_key
        )

        # NOTE: check if reference_config is a dict
        if not isinstance(component_reference_configs, dict) or not component_reference_configs:
            raise ValueError(
                f"No reference config found for component '{component_name}' in the provided reference content."
            )

        # SECTION: generate reference rules
        reference_rules = ReferenceChecker_.generate_reference_rules(
            reference_configs=component_reference_configs
        )

        # SECTION: check component_reference_configs
        # labels
        labels = []

        # SECTION: check both databook and table
        for prop_name, prop_idx in component_reference_configs.items():
            # property name
            prop_name = prop_name.strip()

            # ! databook
            databook_ = prop_idx.get('databook', None)
            if databook_ is None:
                raise ValueError(
                    f"Databook for property '{prop_name}' is not specified.")

            # ! table
            table_ = prop_idx.get('table', None)
            if table_ is None:
                raise ValueError(
                    f"Table for property '{prop_name}' is not specified.")

            # ! label/labels
            # >> check label
            label_ = prop_idx.get('label', None)
            if label_:
                # append to labels
                labels.append(str(label_))

            # >> check labels
            labels_ = prop_idx.get('labels', None)
            if labels_ and isinstance(labels_, dict):
                # extract labels
                for lbl_key, lbl_val in labels_.items():
                    if lbl_val and isinstance(lbl_val, str):
                        # append to labels
                        labels.append(str(lbl_val))

        # SECTION: return result
        return ComponentReferenceThermoDB(
            component=component,
            reference_content=[reference_content],
            reference_configs=component_reference_configs,
            reference_rules=reference_rules,
            labels=labels
        )
    except Exception as e:
        raise Exception(f"Building {component_name} thermodb failed! {e}")
