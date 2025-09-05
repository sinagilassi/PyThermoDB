# import libs
import logging
from typing import List, Optional

# NOTE: logger
logger = logging.getLogger(__name__)


def has_prop_nested(d: dict, prop_name: str) -> bool:
    '''
    Check if a property exists in a nested dictionary

    Parameters
    ----------
    d : dict
        The dictionary to search
    prop_name : str
        The property name to search for

    Returns
    -------
    bool
        True if the property exists, False otherwise
    '''
    try:
        if not isinstance(d, dict):
            logger.error("Input is not a dictionary")
            return False

        # check if the property exists at the current level
        if prop_name in d:
            return True

        # recursively check nested dictionaries
        for value in d.values():
            if isinstance(value, dict):
                if has_prop_nested(value, prop_name):
                    return True

        # property not found
        return False

    except Exception as e:
        logger.error(f"Error in has_prop_nested: {e}")
        return False
