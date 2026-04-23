# import libs
import logging
from typing import Dict, Any, Union
# locals
from .checker import ReferenceChecker

# NOTE: setup logger
logger = logging.getLogger(__name__)


class ReferenceMaker(ReferenceChecker):
    """
    A class to load a custom reference and insert data to each table.
    """

    def __init__(
        self,
        custom_reference: Union[Dict[str, Any], str]
    ):
        """
        Initialize the ReferenceMaker class.

        Parameters
        ----------
        custom_reference : Dict[str, Any] | str
            The custom reference as a dictionary or string.
        """
        try:
            # NOTE: check if custom_reference is a dict
            if not isinstance(custom_reference, (dict, str)):
                raise TypeError(
                    "custom_reference must be a dictionary or string.")

            # NOTE: create ReferenceChecker instance
            super().__init__(custom_reference)
        except (TypeError, KeyError) as e:
            logging.error(f"Error checking custom reference: {e}")
            raise

    def build_yaml_reference(self):
        """
        Build the YAML reference content and return a dictionary.

        Returns
        -------
        Dict[str, Any] | None
            A dictionary containing the YAML reference content if it exists, otherwise None.
        """
        try:
            # NOTE: build YAML reference content
            return None
        except Exception as e:
            logging.error(f"Error building YAML reference: {e}")
            raise
