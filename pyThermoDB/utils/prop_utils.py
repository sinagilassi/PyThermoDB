# import libs
import logging
from typing import Any, Dict, List, Literal, Optional, Union
# local

# NOTE: logger
logger = logging.getLogger(__name__)


def ignore_state_in_prop(
    prop_name: str,
    ignore_state_props: Optional[List[str]] = None
) -> bool:
    """Check if the property name should ignore state based on the provided list.

    Parameters
    ----------
    prop_name : str
        The name of the property to check.
    ignore_state_props : Optional[List[str]], optional
        List of property names that should ignore state, by default None.

    Returns
    -------
    bool
        True if the property should ignore state, False otherwise.
    """
    try:
        if ignore_state_props is None:
            return False
        if not isinstance(ignore_state_props, list):
            raise TypeError("ignore_state_props must be a list or None")
        if not all(isinstance(item, str) for item in ignore_state_props):
            raise ValueError("All items in ignore_state_props must be strings")
        if len(ignore_state_props) == 0:
            return False

        # lowercase comparison for case-insensitivity
        ignore_state_props = [item.lower() for item in ignore_state_props]

        # return check result
        return prop_name.lower() in ignore_state_props
    except Exception as e:
        logger.error(f"Error in ignore_state_in_prop: {e}")
        raise
