# import libs
import logging
import yaml
import json
from typing import (
    Dict,
    Any,
    List,
    Optional,
    Literal
)
# local
from .table import ThermoTable


class ThermoDatabook():
    """
    Databook class serves as a container for tables.
    """
    # NOTE: attributes
    # databook name
    _name: str = ""
    # tables
    _tables: Dict[str, ThermoTable] = {}
    # databook id
    _databook_id: int = 1
    # table id
    _table_id: int = 1
    # description
    _description: str = ""

    # NOTE: databook
    _contents: Dict[str, Any] = {}

    def __init__(
        self,
        databook_name: str,
        description: Optional[str] = None
    ):
        """
        Initializes the ThermoDatabook instance.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        description : Optional[str], optional
            The description of the databook, by default None.
        """
        # NOTE: set
        # databook name
        self._name = databook_name

        # SECTION: initialize the tables
        # initialize tables
        self._tables = {}

        # initialize databook id
        self._databook_id = 1
        # initialize table id
        self._table_id = 1
        # initialize description
        self._description = description if description else ""

    @property
    def name(self) -> str:
        """
        Returns the name of the databook.
        """
        return self._name

    @property
    def tables(self) -> Dict[str, ThermoTable]:
        """
        Returns the tables in the databook.
        """
        return self._tables

    @property
    def databook_id(self) -> int:
        """
        Returns the databook id.
        """
        return self._databook_id

    @property
    def description(self) -> str:
        """
        Returns the description of the databook.
        """
        return self._description

    def set_databook_id(self, databook_id: int):
        """
        Sets the databook id.
        """
        self._databook_id = databook_id

    def set_description(self, description: str):
        """
        Sets the description for the databook.
        """
        self._description = description

    def add_data_table(
        self,
        table_name: str,
        data: str,
        description: Optional[str] = None
    ):
        """
        Adds a data table to the databook.

        Parameters
        ----------
        table_name : str
            The name of the table to be added.
        data : str
            The data (csv format) to be added to the table.
        description : Optional[str], optional
            The description of the table, by default None.
        """
        try:
            # SECTION: validate inputs
            # check if table already exists
            if table_name in self._tables:
                raise ValueError(f"Table '{table_name}' already exists.")

            # check if data is valid
            if not data:
                raise ValueError("Data cannot be empty.")

            # SECTION: create a new table instance
            new_table = ThermoTable(
                name=table_name,
                data=data,
                id=self._table_id,
                types="data",
                description=description
            )

            # append the new table to the tables list
            self._tables[table_name] = new_table

            # increment table id
            self._table_id += 1

            # log success
            logging.info(f"Data table '{table_name}' added successfully.")
        except Exception as e:
            logging.error(f"Error adding data table '{table_name}': {e}")
            raise

    def add_equation_table(
        self,
        table_name: str,
        data: str,
        equations: str | List[str],
        description: Optional[str] = None
    ):
        """
        Adds an equation table to the databook.

        Parameters
        ----------
        table_name : str
            The name of the table to be added.
        data : str
            The data (csv format) to be added to the table.
        equations : str | List[str]
            The equation or list of equations associated with the table.
        description : Optional[str], optional
            The description of the table, by default None.
        """
        try:
            # SECTION: validate inputs
            # check if table already exists
            if table_name in self._tables:
                raise ValueError(
                    f"Equation table '{table_name}' already exists.")

            # check if data is valid
            if not data:
                raise ValueError("Data cannot be empty.")

            # equations must be a string or a list of strings
            if isinstance(equations, str):
                equations = [equations]
            elif (
                not isinstance(equations, list) or
                not all(isinstance(eq, str) for eq in equations)
            ):
                raise ValueError(
                    "Equations must be a string or a list of strings.")

            # SECTION: create a new table instance
            new_table = ThermoTable(
                name=table_name,
                data=data,
                id=self._table_id,
                types="equation",
                equations=equations,
                description=description
            )

            # append the new table to the tables list
            self._tables[table_name] = new_table

            # increment table id
            self._table_id += 1

            # log success
            logging.info(f"Equation table '{table_name}' added successfully.")
        except Exception as e:
            logging.error(f"Error adding equation table '{table_name}': {e}")
            raise

    def remove_table(self, table_name: str):
        """
        Removes a table from the databook.

        Parameters
        ----------
        table_name : str
            The name of the table to be removed.
        """
        try:
            # SECTION: validate inputs
            # check
            if table_name not in self._tables:
                raise KeyError(
                    f"Table '{table_name}' does not exist in the databook.")

            # NOTE: remove the table
            self._tables.pop(table_name, None)

            # log success
            logging.info(f"Table '{table_name}' removed successfully.")
        except KeyError:
            logging.error(
                f"Table '{table_name}' does not exist in the databook.")
            raise

    def update_table(
        self,
        table_name: str,
        new_data: str
    ):
        """
        Updates the data of an existing table in the databook.

        Parameters
        ----------
        table_name : str
            The name of the table to be updated.
        new_data : str
            The new data (csv format) to be set for the table.
        """
        try:
            # SECTION: validate inputs
            # check if table exists
            if table_name not in self._tables:
                raise KeyError(
                    f"Table '{table_name}' does not exist in the databook.")

            # check if new data is valid
            if not new_data:
                raise ValueError("New data cannot be empty.")

            # SECTION: update the table data
            for tb_name, tb in self._tables.items():
                # get the table by name
                if tb_name == table_name:
                    # update the data
                    tb.update_data(new_data)

                    # log success
                    logging.info(f"Table '{table_name}' updated successfully.")
                    return

            raise KeyError(
                f"Table '{table_name}' does not exist in the databook.")
        except KeyError:
            logging.error(
                f"Table '{table_name}' does not exist in the databook.")
            raise

    def update_table_description(
        self,
        table_name: str,
        description: str
    ):
        """
        Updates the description of an existing table in the databook.

        Parameters
        ----------
        table_name : str
            The name of the table to be updated.
        description : str
            The new description to be set for the table.
        """
        try:
            # SECTION: validate inputs
            # check if table exists
            if table_name not in self._tables:
                raise KeyError(
                    f"Table '{table_name}' does not exist in the databook.")

            # check if description is valid
            if not description:
                raise ValueError("Description cannot be empty.")

            # SECTION: update the table description
            for tb_name, tb in self._tables.items():
                # get the table by name
                if tb_name == table_name:
                    # update the description
                    tb._description = description

                    # log success
                    logging.info(
                        f"Description for table '{table_name}' updated successfully.")
                    return

            raise KeyError(
                f"Table '{table_name}' does not exist in the databook.")
        except KeyError:
            logging.error(
                f"Table '{table_name}' does not exist in the databook.")
            raise

    def build(self):
        """
        Build the databook by extracting data from the tables, and return a yml representation.
        """
        try:
            # NOTE: set the databook
            self._databook = {}
            # NOTE: databook tables
            sources: Dict[str, Any] = {}

            # SECTION: build each table
            for table_name, table in self._tables.items():
                # build the table
                table.build_table()

                # get source
                source = table.table

                # append the table to sources
                sources.update(source)

            # SECTION: build the databook
            _contents = {
                'DATABOOK-ID': self._databook_id,
                'DESCRIPTION': self._description,
                'TABLES': sources
            }

            # NOTE: set the databook
            self._contents = _contents

            # log success
            logging.info("Databook built successfully.")
        except Exception as e:
            logging.error(f"Error extracting table data: {e}")
            raise

    def get_contents(
        self,
        res_format: Literal[
            'dict', 'yml'
        ] = 'dict'
    ) -> Dict[str, Any] | str:
        """
        Returns the contents of the databook in the specified format.

        Parameters
        ----------
        res_format : Literal['dict', 'yml'], optional
            The format of the returned contents, by default 'dict'.

        Returns
        -------
        Dict[str, Any]
            The contents of the databook in the specified format.
        """
        try:
            # NOTE: check the format
            if res_format not in ['dict', 'yml']:
                raise ValueError("res_format must be 'dict' or 'yml'.")

            # return the contents in the specified format
            if res_format == 'yml':
                transformed_ = yaml.dump(self._contents, sort_keys=False)
                return transformed_
            elif res_format == 'dict':

                return self._contents
            else:
                raise ValueError("res_format must be 'dict' or 'yml'.")

        except Exception as e:
            logging.error(f"Error getting databook contents: {e}")
            raise

    def save_contents(
        self,
        file_path: str,
        res_format: Literal[
            'dict', 'yml'
        ] = 'dict'
    ):
        """
        Saves the contents of the databook to a file.

        Parameters
        ----------
        file_path : str
            The path to the file where the contents will be saved.
        res_format : Literal['dict', 'yml'], optional
            The format of the saved contents, by default 'dict'.
        """
        try:
            # NOTE: check the format
            if res_format not in ['dict', 'yml']:
                raise ValueError("res_format must be 'dict' or 'yml'.")

            # get the contents in the specified format
            contents = self.get_contents(res_format=res_format)

            # serialize if dict
            if res_format == 'dict':
                contents = json.dumps(contents, indent=2)

            # write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(contents))

            logging.info(
                f"Databook contents saved to {file_path} successfully.")
        except Exception as e:
            logging.error(f"Error saving databook contents: {e}")
            raise
