# import libs
import logging
from typing import Any, Dict, List, Optional, Literal
from pythermodb_settings.models import Component
# locals
from ..config import REFERENCE_CONFIG_KEYS

# NOTE: logger
logger = logging.getLogger(__name__)


def look_up_component_reference_config(
    component_id: str,
    reference_config: Dict[str, Any],
    reference_config_default_check: Optional[bool] = True
) -> Dict[str, Any]:
    '''
    Look up the reference configuration for a given component ID.

    Parameters
    ----------
    component_id : str
        The ID of the component to look up.
    reference_config : Dict[str, Any]
        A dictionary containing reference configurations for components.
    reference_config_default_check : Optional[bool], optional
        Whether to perform default checks on the reference configuration, by default True

    Returns
    -------
    Dict[str, Any]
        The reference configuration for the specified component.

    Raises
    ------
    ValueError
        If no reference configuration is found for the specified component.
    '''
    # Convert all keys to lowercase for case-insensitive lookup
    reference_config_lower = {
        k.lower(): v for k, v in reference_config.items()
    }
    # Lowercase component_id for case-insensitive lookup
    component_id_lower = component_id.lower()

    # Extract component reference config
    component_reference_config = reference_config_lower.get(
        component_id_lower,
        {}
    )

    # Check if reference_config is empty
    if not component_reference_config:
        # Check default
        if reference_config_default_check:
            for key in REFERENCE_CONFIG_KEYS:
                key_lower = key.lower()
                if key_lower in reference_config_lower:
                    component_reference_config = reference_config_lower[key_lower]
                    break

    if not component_reference_config:
        raise ValueError(
            f"No reference config found for component '{component_id}' in the provided reference config."
        )

    return component_reference_config


def look_up_binary_mixture_reference_config(
        component_id_1: str,
        component_id_2: str,
        reference_config: Dict[str, Any],
        reference_config_default_check: Optional[bool] = True,
        delimiter: str = '|'
) -> Dict[str, Any]:
    '''
    Look up the reference configuration for a given binary mixture of two components.

    Parameters
    ----------
    component_id_1 : str
        The ID of the first component in the mixture.
    component_id_2 : str
        The ID of the second component in the mixture.
    reference_config : Dict[str, Any]
        A dictionary containing reference configurations for components and mixtures.
    reference_config_default_check : Optional[bool], optional
        Whether to perform default checks on the reference configuration, by default True
    delimiter : str, optional
        Delimiter to separate component identifiers in the mixture, by default '|'

    Returns
    -------
    Dict[str, Any]
        The reference configuration for the specified binary mixture.

    Raises
    ------
    ValueError
        If no reference configuration is found for the specified binary mixture.
    '''
    # Create possible mixture IDs (both orders)
    mixture_id_1 = f"{component_id_1.strip().lower()}{delimiter}{component_id_2.strip().lower()}"
    mixture_id_2 = f"{component_id_2.strip().lower()}{delimiter}{component_id_1.strip().lower()}"

    # Convert all keys to lowercase for case-insensitive lookup
    reference_config_lower = {
        k.lower(): v for k, v in reference_config.items()
    }

    # NOTE: Extract binary mixture reference config
    binary_mixture_reference_config = reference_config_lower.get(
        mixture_id_1,
        reference_config_lower.get(mixture_id_2, {})
    )

    # NOTE: Check if reference_config is empty
    if not binary_mixture_reference_config:
        # Check default
        if reference_config_default_check:
            for key in REFERENCE_CONFIG_KEYS:
                key_lower = key.lower()
                if key_lower in reference_config_lower:
                    binary_mixture_reference_config = reference_config_lower[key_lower]
                    break

    if not binary_mixture_reference_config:
        raise ValueError(
            f"No reference config found for binary mixture '{component_id_1}' and '{component_id_2}' in the provided reference config."
        )

    return binary_mixture_reference_config


def look_up_mixture_reference_config(
        components: List[Component],
        reference_config: Dict[str, Any],
        reference_config_default_check: Optional[bool] = True,
        mixture_key: Literal['Name', 'Formula'] = 'Name',
        delimiter: str = '|'
) -> Dict[str, Any]:
    '''
    Look up the reference configuration for a given mixture of components.

    Parameters
    ----------
    components : List[Component]
        A list of Component objects representing the components in the mixture.
    reference_config : Dict[str, Any]
        A dictionary containing reference configurations for components and mixtures.
    reference_config_default_check : Optional[bool], optional
        Whether to perform default checks on the reference configuration, by default True
    mixture_key : Literal['Name', 'Formula'], optional
        Key to identify the component in the reference content, by default 'Name'
    delimiter : str, optional
        Delimiter to separate component identifiers in the mixture, by default '|'

    Returns
    -------
    Dict[str, Any]
        The reference configuration for the specified mixture.

    Raises
    ------
    ValueError
        If no reference configuration is found for the specified mixture.
    '''
    if len(components) < 2:
        raise ValueError(
            "At least two components are required to form a mixture.")

    # Generate mixture ID based on component_key
    if mixture_key == 'Name':
        component_ids = [
            comp.name.strip() for comp in components
        ]
    elif mixture_key == 'Formula':
        component_ids = [
            comp.formula.strip() for comp in components
        ]
    else:
        raise ValueError(
            "Invalid component_key. Must be 'Name-State' or 'Formula-State'.")

    # NOTE: Create mixture ID by sorting component IDs to ensure order-independence
    mixture_id = delimiter.join(sorted([cid.lower() for cid in component_ids]))

    # NOTE: Normalize reference_config keys: split, strip, lowercase, sort, join
    reference_config_normalized = {
        delimiter.join(sorted([part.strip().lower() for part in k.split(delimiter)])): v
        for k, v in reference_config.items() if delimiter in k
    }

    # NOTE: Extract mixture reference config
    mixture_reference_config = reference_config_normalized.get(
        mixture_id,
        {}
    )

    # NOTE: Check if reference_config is empty
    if not mixture_reference_config:
        # Check default (only for mixture keys)
        if reference_config_default_check:
            for key in REFERENCE_CONFIG_KEYS:
                key_lower = key.lower()
                if key_lower in reference_config_normalized:
                    mixture_reference_config = reference_config_normalized[key_lower]
                    break

    if not mixture_reference_config:
        raise ValueError(
            f"No reference config found for mixture '{mixture_id}' in the provided reference config."
        )

    # return mixture reference config
    return mixture_reference_config


def is_table_available(
        table_name: str,
        tables: List[str]
):
    '''
    Check if a table name is available in the list of tables.

    Parameters
    ----------
    table_name : str
        The name of the table to check.
    tables : List[str]
        A list of available table names.

    Returns
    -------
    bool
        True if the table name is available, False otherwise.

    Notes
    -----
    - The comparison is case-insensitive and ignores leading/trailing whitespace.
    '''
    try:
        # Normalize table name for comparison
        normalized_table_name = table_name.strip().lower()
        normalized_tables = [t.strip().lower() for t in tables]

        return normalized_table_name in normalized_tables
    except Exception as e:
        logger.error(f"Error checking table availability: {e}")
        return False


def is_databook_available(
        databook_name: str,
        databooks: List[str]
):
    '''
    Check if a databook name is available in the list of databooks.

    Parameters
    ----------
    databook_name : str
        The name of the databook to check.
    databooks : List[str]
        A list of available databook names.

    Returns
    -------
    bool
        True if the databook name is available, False otherwise.

    Notes
    -----
    - The comparison is case-insensitive and ignores leading/trailing whitespace.
    '''
    try:
        # Normalize databook name for comparison
        normalized_databook_name = databook_name.strip().lower()
        normalized_databooks = [d.strip().lower() for d in databooks]

        return normalized_databook_name in normalized_databooks
    except Exception as e:
        logger.error(f"Error checking databook availability: {e}")
        return False
