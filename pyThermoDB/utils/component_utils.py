# import libs
import logging
from typing import Any, Dict, List, Literal, Optional, Union
# local
from ..models import Component


def set_component_id(
    component: Component,
    component_key: Literal['Name-State', 'Formula-State'] = 'Formula-State'
):
    """Set component ID based on the specified key.

    Parameters
    ----------
    component : Component
        Component object containing name, formula, and state.
    component_key : Literal['Name-State', 'Formula-State'], optional
        Key to identify the component, by default 'Formula-State'

    Returns
    -------
    str
        Component ID based on the specified key.

    Raises
    ------
    ValueError
        If the component_key is not recognized.
    """
    try:
        if not isinstance(component, Component):
            raise TypeError("component must be an instance of Component")
        if component_key not in ['Name-State', 'Formula-State']:
            raise ValueError(
                "component_key must be either 'Name-State' or 'Formula-State'")

        if component_key == 'Name-State':
            return f"{component.name.strip()}-{component.state.strip()}"
        elif component_key == 'Formula-State':
            return f"{component.formula.strip()}-{component.state.strip()}"
        else:
            raise ValueError(
                "component_key must be either 'Name-State' or 'Formula-State'")
    except Exception as e:
        logging.error(f"Error in set_component_id: {e}")
        raise


def set_component_query(
    component: Component,
    component_key: Literal[
        'Name-State', 'Formula-State'
    ] = 'Formula-State'
) -> str:
    """Set component query dictionary based on the specified key.

    Parameters
    ----------
    component : Component
        Component object containing name, formula, and state.
    component_key : Literal['Name-State', 'Formula-State'], optional
        Key to identify the component, by default 'Formula-State'

    Returns
    -------
    str
        Query string based on the specified key.

    Raises
    ------
    ValueError
        If the component_key is not recognized.
    """
    try:
        # SECTION: validate inputs
        if not isinstance(component, Component):
            raise TypeError("component must be an instance of Component")
        if component_key not in ['Name-State', 'Formula-State']:
            raise ValueError(
                "component_key must be either 'Name-State' or 'Formula-State'")

        # SECTION: set query based on key
        if component_key == 'Name-State':
            query = f"Name.str.lower() == '{component.name.strip().lower()}' and State.str.lower() == '{component.state.strip().lower()}'"
        elif component_key == 'Formula-State':
            query = f"Formula.str.lower() == '{component.formula.strip().lower()}' and State.str.lower() == '{component.state.strip().lower()}'"
        else:
            raise ValueError(
                "component_key must be either 'Name-State' or 'Formula-State'")

        return query

    except Exception as e:
        logging.error(f"Error in set_component_query: {e}")
        raise
