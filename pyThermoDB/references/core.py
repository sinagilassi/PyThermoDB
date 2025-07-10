# import libs
from typing import (
    Dict,
    Any,
    List,
    Optional
)
# locals
from .databook import ThermoDatabook


class ReferenceCore:
    """
    ReferenceCore class serves as a base class for building references in the pyThermoDB package.
    """
    # NOTE: attributes
    # databook id
    databook_id: int = 0

    def __init__(self):
        # NOTE: set
        # databook
        self.databook: Dict[str, ThermoDatabook] = {}
        # databook id

    def create_databook(
        self,
        databook_name: str
    ):
        """
        Creates a databook for the reference.

        Parameters
        ----------
        databook_name : str
            The name of the databook to be created.
        """
        if databook_name not in self.databook:
            self.databook[databook_name] = ThermoDatabook()

            # increment databook id
            self.databook_id += 1
            # set databook id
            self.databook[databook_name].set_databook_id(self.databook_id)
        else:
            raise ValueError(f"Databook '{databook_name}' already exists.")

    def add_description(
        self,
        databook_name: str,
        description: str
    ):
        """
        Adds a description to the specified databook.

        Parameters
        ----------
        databook_name : str
            The name of the databook to which the description will be added.
        description : str
            The description to be added to the databook.
        """
        if databook_name in self.databook:
            self.databook[databook_name].set_description(description)
        else:
            raise ValueError(f"Databook '{databook_name}' does not exist.")
