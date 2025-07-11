# import libs
import logging
import yaml
from typing import (
    Dict,
    Literal,
    Any,
    List,
    Optional
)
# locals
from .databook import ThermoDatabook


class ThermoReference:
    """
    ThermoReference class serves as a base class for building references in the pyThermoDB package.
    """
    # NOTE: attributes
    # databook id
    _databook_id: int = 1
    # databook# databook
    _databook: Dict[str, ThermoDatabook] = {}

    # references
    _references = {}

    def __init__(self):
        """
        Initialize the ThermoReference instance.
        """
        # NOTE: set
        # databook
        self._databook: Dict[str, ThermoDatabook] = {}
        # databook id
        self._databook_id = 1

    @property
    def references(self) -> Dict[str, Any]:
        """
        Get the references dictionary.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing references.
        """
        return self._references

    def get_references(
        self,
        res_format: Literal['dict', 'yml']
    ) -> Dict[str, Any] | str:
        """
        Get the references dictionary.

        Parameters
        ----------
        res_format : Literal['dict', 'yml']
            The format of the result, either 'dict' or 'yml'.

        Returns
        -------
        Dict[str, Any] | str
            A dictionary containing references or a string in YAML format.
        """
        if res_format == 'dict':
            return self._references
        elif res_format == 'yml':
            # convert references to YAML format
            return yaml.safe_dump(
                self._references,
                sort_keys=False,
                default_flow_style=False
            )
        else:
            raise ValueError("Invalid format. Use 'dict' or 'yml'.")

    def create_databook(
        self,
        databook_name: str,
        description: Optional[str] = None
    ) -> None:
        """
        Create a new ThermoDatabook instance.

        Parameters
        ----------
        databook_name : str
            Name of the databook.
        description : Optional[str], optional
            Description of the databook, by default None

        Returns
        -------
        None
        """
        try:
            # check if databook already exists
            if databook_name in self._databook:
                raise ValueError(f"Databook '{databook_name}' already exists.")

            # create a new databook instance
            databook = ThermoDatabook(databook_name, description)
            # add to the databook dict
            self._databook[databook_name] = databook

            # increment databook id
            self._databook_id += 1

            # log the creation
            logging.info(
                f"Databook '{databook_name}' created with ID: {self._databook_id - 1}")

        except Exception as e:
            logging.error(f"Error creating databook: {e}")
            raise e

    def add_databook(
        self,
        databook: ThermoDatabook
    ):
        """
        Add an existing ThermoDatabook instance to the references.

        Parameters
        ----------
        databook : ThermoDatabook
            An instance of ThermoDatabook to be added.

        Returns
        -------
        None
        """
        try:
            # check if databook already exists
            if databook.name in self._databook:
                raise ValueError(f"Databook '{databook.name}' already exists.")

            # add the databook to the dict
            self._databook[databook.name] = databook

            # increment databook id
            self._databook_id += 1

            logging.info(
                f"Databook '{databook.name}' added with ID: {self._databook_id - 1}")

        except Exception as e:
            logging.error(f"Error adding databook: {e}")
            raise e

    def remove_databook(
        self,
        databook_name: str
    ) -> None:
        """
        Remove a ThermoDatabook instance from the references.

        Parameters
        ----------
        databook_name : str
            Name of the databook to be removed.

        Returns
        -------
        None
        """
        try:
            # check if databook exists
            if databook_name not in self._databook:
                raise ValueError(f"Databook '{databook_name}' does not exist.")

            # NOTE: remove the databook
            del self._databook[databook_name]
            logging.info(f"Databook '{databook_name}' removed successfully.")

            # NOTE: reset databook ids
            self._reset_databook_ids()

        except Exception as e:
            logging.error(f"Error removing databook: {e}")
            raise e

    def _reset_databook_ids(self):
        """
        Check all databooks ids and reset them to start from 1.

        Returns
        -------
        None
        """
        try:
            # reset databook ids
            for i, databook in enumerate(self._databook.values(), start=1):
                databook.databook_id = i

            self._databook_id = len(self._databook) + 1

            logging.info("Databook IDs reset successfully.")

        except Exception as e:
            logging.error(f"Error resetting databook IDs: {e}")
            raise e

    def get_databook(
        self,
        databook_name: str
    ) -> ThermoDatabook:
        """
        Get a ThermoDatabook instance by its name.

        Parameters
        ----------
        databook_name : str
            Name of the databook to retrieve.

        Returns
        -------
        ThermoDatabook
            The ThermoDatabook instance.
        """
        try:
            # check if databook exists
            if databook_name not in self._databook:
                raise ValueError(f"Databook '{databook_name}' does not exist.")

            # return the databook instance
            return self._databook[databook_name]

        except Exception as e:
            logging.error(f"Error retrieving databook: {e}")
            raise e

    def get_all_databooks(self) -> Dict[str, ThermoDatabook]:
        """
        Get all ThermoDatabook instances.

        Returns
        -------
        Dict[str, ThermoDatabook]
            A dictionary of all ThermoDatabook instances.
        """
        return self._databook.copy()

    def remove_all_databooks(self) -> None:
        """
        Remove all ThermoDatabook instances from the references.

        Returns
        -------
        None
        """
        try:
            self._databook.clear()
            self._databook_id = 1
            logging.info("All databooks removed successfully.")

        except Exception as e:
            logging.error(f"Error removing all databooks: {e}")
            raise e

    def build_references(
        self,
    ):
        """
        Build all references in the databook.

        Parameters
        ----------
        res_format : Literal['yml', 'dict'], optional
            The format of the result, by default 'dict'.

        Returns
        -------
        None
        """
        try:
            # NOTE: initialize references
            self._references = {}
            # create a dictionary to hold references
            references = {}
            # add references
            references['REFERENCES'] = {}

            # NOTE: iterate through all databooks
            for databook in self._databook.values():
                databook.build()
                logging.info(f"Databook '{databook.name}' built successfully.")

                # get the contents of the databook
                contents = databook.get_contents(res_format='dict')

                # add to references
                references['REFERENCES'][databook.name] = contents

            # NOTE: set references
            self._references = references

        except Exception as e:
            logging.error(f"Error building references: {e}")
            raise e
