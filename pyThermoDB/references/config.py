# import libs
from typing import Dict, List, Any, Union, Optional
# local
from ..utils import Convertor


class ReferenceConfig:
    """
    Configuration for references in pyThermoDB.
    """

    def __init__(self):
        # NOTE: init Convertor
        self.Convertor_ = Convertor()

    def set_reference_config(
        self,
        reference_config: str
    ) -> Dict[str, Any]:
        """
        Convert a string reference config to a dictionary.

        Parameters
        ----------
        reference_config : str
            The reference configuration as a string.

        Returns
        -------
        dict
            The reference configuration as a dictionary.
        """
        try:
            return self.Convertor_.str_to_dict(reference_config)
        except Exception as e:
            raise Exception(f"Error converting reference config: {e}") from e
