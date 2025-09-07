# import libs
import logging
from typing import Any, Dict, List, Literal, Optional, Union
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
        k.lower(): v for k, v in reference_config.items()}
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
