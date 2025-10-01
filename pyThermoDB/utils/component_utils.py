# import libs
import logging
from typing import List, Literal, Dict
from pythermodb_settings.models import Component
# local
from ..config import DEFAULT_COMPONENT_STATES

# NOTE: set logger
logger = logging.getLogger(__name__)


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


def validate_component_state(
    state: str,
    valid_states: List[str]
) -> tuple[bool, str]:
    """Validate if the provided state is in the list of valid states.

    Parameters
    ----------
    state : str
        The state to validate (e.g., 's', 'l', 'g', 'aq').
    valid_states : Optional[List[str]], optional
        List of valid states, by default None which uses DEFAULT_COMPONENT_STATES.

    Returns
    -------
    tuple[bool, str]
        A tuple containing a boolean indicating if the state is valid and the normalized state string.
    """
    try:
        # NOTE: default valid states
        if valid_states is None:
            valid_states = DEFAULT_COMPONENT_STATES

        # NOTE: validate inputs
        if not isinstance(state, str):
            raise TypeError("state must be a string")
        if not isinstance(valid_states, list) or not all(isinstance(s, str) for s in valid_states):
            raise TypeError("valid_states must be a list of strings")

        # NOTE: state
        state = state.strip().lower()

        # NOTE: case insensitive comparison
        lookup_res = state in [s.lower() for s in valid_states]

        return lookup_res, state

    except Exception as e:
        logging.error(f"Error in validate_component_state: {e}")
        return False, ''


def create_binary_mixture_id(
    component_1: Component,
    component_2: Component,
    mixture_key: Literal[
        'Name', 'Formula'
    ] = 'Name',
    delimiter: str = "|"
) -> str:
    """Create a unique binary mixture ID based on two components.

    Parameters
    ----------
    component1 : Component
        The first component in the mixture.
    component2 : Component
        The second component in the mixture.
    component_key : Literal['Name', 'Formula'], optional
        The key to use for identifying the components, by default 'Name'.
    delimiter : str, optional
        Delimiter to separate the two components in the ID, by default "|".

    Returns
    -------
    str
        A unique binary mixture ID.

    Raises
    ------
    ValueError
        If the component_key is not recognized.
    """
    try:
        # SECTION: validate inputs
        if not isinstance(component_1, Component) or not isinstance(component_2, Component):
            raise TypeError(
                "Both component1 and component2 must be instances of Component")
        # check delimiter
        if not isinstance(delimiter, str):
            raise TypeError("delimiter must be a string")

        # SECTION: get component IDs
        if mixture_key == 'Name':
            comp1_id = component_1.name.strip()
            comp2_id = component_2.name.strip()
        elif mixture_key == 'Formula':
            comp1_id = component_1.formula.strip()
            comp2_id = component_2.formula.strip()
        else:
            raise ValueError(
                "component_key must be 'Name-State', 'Formula-State', 'Name', or 'Formula'")

        # SECTION: create unique mixture ID (sorted to ensure uniqueness)
        mixture_id = delimiter.join(sorted([comp1_id, comp2_id]))

        return mixture_id

    except Exception as e:
        logging.error(f"Error in create_binary_mixture_id: {e}")
        raise


def create_mixture_ids(
    components: List[Component],
    mixture_key: Literal[
        'Name', 'Formula'
    ] = 'Name',
    delimiter: str = "|"
) -> List[str]:
    """Create unique mixture IDs for all binary combinations of the provided components.

    Parameters
    ----------
    components : List[Component]
        List of components to create mixtures from.
    mixture_key : Literal['Name', 'Formula'], optional
        The key to use for identifying the components, by default 'Name'.
    delimiter : str, optional
        Delimiter to separate the two components in the ID, by default "|".

    Returns
    -------
    List[str]
        A list of unique binary mixture IDs.

    Raises
    ------
    ValueError
        If the component_key is not recognized.
    """
    try:
        # SECTION: validate inputs
        if not isinstance(components, list) or not all(isinstance(c, Component) for c in components):
            raise TypeError("components must be a list of Component instances")
        if not isinstance(delimiter, str):
            raise TypeError("delimiter must be a string")

        # SECTION: create mixture IDs
        mixture_ids = set()
        num_components = len(components)

        for i in range(num_components):
            for j in range(i + 1, num_components):
                mix_id = create_binary_mixture_id(
                    components[i],
                    components[j],
                    mixture_key=mixture_key,
                    delimiter=delimiter
                )
                mixture_ids.add(mix_id)

        return list(mixture_ids)

    except Exception as e:
        logging.error(f"Error in create_mixture_ids: {e}")
        raise


def create_mixtures(
    components: List[Component],
    mixture_key: Literal[
        'Name', 'Formula'
    ] = 'Name',
    delimiter: str = "|"
) -> Dict[str, Dict[str, str]]:
    """
    Create unique mixture IDs for all binary combinations of the provided components.

    Parameters
    ----------
    components : List[Component]
        List of components to create mixtures from.
    mixture_key : Literal['Name', 'Formula'], optional
        The key to use for identifying the components, by default 'Name'.
    delimiter : str, optional
        Delimiter to separate the two components in the ID, by default "|".

    Returns
    -------
    Dict[str, Dict[str, str]]
        A dictionary where keys are unique binary mixture IDs and values are dictionaries

    Raises
    ------
    ValueError
        If the component_key is not recognized.
    """
    try:
        # SECTION: validate inputs
        if not isinstance(components, list) or not all(isinstance(c, Component) for c in components):
            raise TypeError("components must be a list of Component instances")
        if not isinstance(delimiter, str):
            raise TypeError("delimiter must be a string")

        # SECTION: create mixture IDs
        mixture_ids = {}
        num_components = len(components)

        for i in range(num_components):
            for j in range(i + 1, num_components):
                mix_id = create_binary_mixture_id(
                    components[i],
                    components[j],
                    mixture_key=mixture_key,
                    delimiter=delimiter
                )
                mixture_ids[mix_id] = {
                    'component_1': components[i].name.strip() if mixture_key == 'Name'
                    else components[i].formula.strip(),
                    'component_2': components[j].name.strip() if mixture_key == 'Name'
                    else components[j].formula.strip()
                }

        return mixture_ids

    except Exception as e:
        logging.error(f"Error in create_mixture_ids: {e}")
        raise
