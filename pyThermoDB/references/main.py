# import libs
import logging
from typing import (
    Dict,
    Union,
    Any
)
# local
from .checker import ReferenceChecker


def check_custom_reference(
    custom_reference: Union[Dict[str, Any], str]
):
    """
    Check the custom reference and return a summary of databook.

    Parameters
    ----------
    custom_reference : str
        The custom reference as a string.

    Returns
    -------
    Dict[str, Any] | None
        A dictionary containing the custom reference if it exists, otherwise None.
    """
    try:
        # NOTE: check if custom_reference is a dict
        if not isinstance(custom_reference, (dict, str)):
            raise TypeError("custom_reference must be a dictionary or string.")

        # SECTION: create ReferenceChecker instance
        ReferenceChecker_ = ReferenceChecker(custom_reference)

        # reference
        reference = ReferenceChecker_.reference

        return reference
    except (TypeError, KeyError) as e:
        logging.error(f"Error checking custom reference: {e}")
        raise
