# import libs
import logging
from typing import Optional, Dict, List, Any
from ..docs import CustomRef
# locals


class ReferenceChecker:
    """
    ReferenceChecker class to check custom references in the databook.
    """
    # NOTE: attribute
    # reference
    _reference = None

    def __init__(
        self,
        custom_reference:
        Dict[str, List[str | Dict[str, Any]]]
    ):
        """
        Initialize the ReferenceChecker with a custom reference.

        Parameters
        ----------
        custom_reference : Dict[str, List[str | Dict[str, Any]]]
            A dictionary containing custom references, where the key is 'reference'
        """
        # NOTE: set custom reference
        self.custom_reference = custom_reference

        # SECTION: initialize CustomRef
        CustomRef_ = CustomRef(self.custom_reference)
        # check ref
        check_ref = CustomRef_.init_ref()

        # NOTE: check if custom reference is valid
        if check_ref:
            # load custom reference
            self._reference = CustomRef_.load_ref()

    @property
    def reference(self):
        """
        Get the custom reference.

        Returns
        -------
        Optional[Dict[str, List[str | Dict[str, Any]]]]
            The custom reference if it exists, otherwise None.
        """
        return self._reference
