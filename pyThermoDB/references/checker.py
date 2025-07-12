# import libs
import logging
from typing import (
    Union,
    Optional,
    Dict,
    List,
    Any
)
from ..docs import CustomRef
# locals


class ReferenceChecker:
    """
    ReferenceChecker class to check custom references in the databook.
    """
    # NOTE: attribute
    # reference
    _reference = None
    # databooks
    _databooks = []
    # databook names
    _databook_names = []

    def __init__(
        self,
        custom_reference:
        Union[Dict[str, List[str | Dict[str, Any]]], str]
    ):
        """
        Initialize the ReferenceChecker with a custom reference.

        Parameters
        ----------
        custom_reference : Dict[str, List[str | Dict[str, Any]]]
            A dictionary containing custom references, where the key is 'reference'
        """
        # NOTE: set custom reference
        # check if custom_reference is a string
        if isinstance(custom_reference, str):
            self.custom_reference = {'reference': [custom_reference]}
        elif isinstance(custom_reference, dict):
            # check if 'reference' key exists
            if 'reference' not in custom_reference:
                logging.error(
                    "'reference' key is missing in custom_reference.")
                raise KeyError(
                    "'reference' key is missing in custom_reference.")

            # set custom reference
            self.custom_reference = custom_reference
        else:
            logging.error("custom_reference must be a dictionary or a string.")
            raise TypeError(
                "custom_reference must be a dictionary or a string.")

        # SECTION: load reference
        self.load_reference()

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

    def load_reference(self) -> Optional[Dict[str, List[str | Dict[str, Any]]]]:
        """
        Load the custom reference.

        Returns
        -------
        Optional[Dict[str, List[str | Dict[str, Any]]]]
            The custom reference if it exists, otherwise None.
        """
        try:
            # SECTION: initialize CustomRef
            CustomRef_ = CustomRef(self.custom_reference)
            # check ref
            check_ref = CustomRef_.init_ref()

            # NOTE: check if custom reference is valid
            if check_ref:
                # load custom reference
                self._reference = CustomRef_.load_ref()
        except Exception as e:
            logging.error(f"Error loading custom reference: {e}")
            return None

    def get_databook(self, databook_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a databook from the custom reference.
        """
        try:
            # NOTE: check if reference is loaded
            if self._reference is None:
                logging.error("Reference is not loaded.")
                return None

            # NOTE: check if databook_name exists in reference
            if databook_name in self._reference:
                return self._reference[databook_name]
            else:
                logging.error(
                    "Databook name not found in reference."
                )
                return None

        except Exception as e:
            logging.error(f"Error getting databooks: {e}")
            return None

    def get_databook_names(self) -> List[str]:
        """
        Get the names of all databooks in the custom reference.

        Returns
        -------
        List[str]
            A list of databook names.
        """
        try:
            # NOTE: check if reference is loaded
            if self._reference is None:
                logging.error("Reference is not loaded.")
                return []

            # get databook names
            self._databook_names = list(self._reference.keys())
            return self._databook_names

        except Exception as e:
            logging.error(f"Error getting databook names: {e}")
            return []

    def get_databook_tables(
        self,
        databook_name: str
    ) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Get the tables of a specific databook.

        Parameters
        ----------
        databook_name : str
            The name of the databook.

        Returns
        -------
        Optional[List[Dict[str, Any]]]
            A list of tables in the databook if it exists, otherwise None.
        """
        try:
            # get databook
            databook = self.get_databook(databook_name)
            if databook is not None:
                return databook.get('TABLES', {})
            else:
                return None
        except Exception as e:
            logging.error(f"Error getting databook tables: {e}")
            return None

    def get_databook_table_names(self, databook_name: str) -> List[str]:
        """
        Get the names of all tables in a specific databook.

        Parameters
        ----------
        databook_name : str
            The name of the databook.

        Returns
        -------
        List[str]
            A list of table names in the databook.
        """
        try:
            # get databook tables
            tables = self.get_databook_tables(databook_name)

            if tables is None:
                logging.error(f"No tables found for databook: {databook_name}")
                return []

            # extract table names
            table_names = list(tables.keys()) if isinstance(
                tables, dict) else []

            return table_names
        except Exception as e:
            logging.error(f"Error getting databook table names: {e}")
            return []

    def get_databook_table(
        self,
        databook_name: str,
        table_name: str
    ):
        """
        Get the table for a given databook.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        table_name : str
            The name of the table.

        Returns
        -------
        Optional[Dict[str, Any]]
            A list of dictionaries containing the table values if it exists, otherwise None.
        """
        try:
            # check if reference is loaded
            if self._reference is None:
                logging.error("Reference is not loaded.")
                return None

            # table name must be a string
            if not isinstance(table_name, str):
                logging.error("table_name must be a string.")
                return None

            # get databook tables
            tables = self.get_databook_tables(databook_name)

            if tables is None:
                logging.error(
                    f"Tables not found for databook: {databook_name}")
                return None

            # NOTE: check if table_name exists in tables
            if table_name not in tables.keys():
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return None

            # return the table
            return tables[table_name]
        except Exception as e:
            logging.error(f"Error getting table values: {e}")
            return None

    def get_table_values(
        self,
        databook_name: str,
        table_name: str
    ) -> Optional[List[List[str | float | int]]]:
        """
        Get the values of a specific table in a databook.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        table_name : str
            The name of the table.

        Returns
        -------
        Optional[List[List[str| float| int]]]
            A list of values from the table if it exists, otherwise None.
        """
        try:
            # get table values
            table = self.get_databook_table(databook_name, table_name)

            if table is None:
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return None

            # check if table has 'VALUES' key
            if not isinstance(table, dict) or 'VALUES' not in table:
                logging.error(
                    f"Table '{table_name}' does not contain 'VALUES' key.")
                return None

            # values
            return table['VALUES']
        except Exception as e:
            logging.error(f"Error getting table values: {e}")
            return None

    def get_table_structure(
            self,
            databook_name: str,
            table_name: str):
        """
        Get the structure of a specific table in a databook.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        table_name : str
            The name of the table.

        Returns
        -------
        Optional[Dict[str, Any]]
            A dictionary containing the structure of the table if it exists, otherwise None.
        """
        try:
            # get table
            table = self.get_databook_table(databook_name, table_name)

            if table is None:
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return None

            # check if table has 'STRUCTURE' key
            if not isinstance(table, dict) or 'STRUCTURE' not in table:
                logging.error(
                    f"Table '{table_name}' does not contain 'STRUCTURE' key.")
                return None

            # return the structure
            return table['STRUCTURE']
        except Exception as e:
            logging.error(f"Error getting table structure: {e}")
            return None

    def get_table_components(
        self,
        databook_name: str,
        table_name: str,
        column_names: List[str] = ['Name', 'Formula', 'State']
    ):
        """
        Get the components registered in a specific table in a databook.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        table_name : str
            The name of the table.
        column_names : List[str], optional
            The names of the columns to extract from the table, by default ['Name', 'Formula', 'State'].

        Returns
        -------

        """
        try:
            # NOTE: get table values
            table_values = self.get_table_values(
                databook_name,
                table_name
            )

            # NOTE: get table structure
            table_structure = self.get_table_structure(
                databook_name,
                table_name
            )

            # check if table values are valid
            if table_values is None:
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return None

            # check if table structure is valid
            if table_structure is None:
                logging.error(
                    f"Table '{table_name}' does not contain 'STRUCTURE' key.")
                return None

            # NOTE: check if table values is a list
            if not isinstance(table_values, list):
                logging.error(
                    f"Table '{table_name}' values are not a list.")
                return None

            # SECTION: extract components
            # NOTE: init component source
            components = {}

            # ! header
            COLUMNS = table_structure.get('COLUMNS', [])
            if not isinstance(COLUMNS, list):
                logging.error("Table structure 'COLUMNS' must be a list.")
                return None

            # if empty COLUMNS, return empty components
            if not COLUMNS:
                logging.warning("Table structure 'COLUMNS' is empty.")
                return {}

            # NOTE: find column name indices in the table header
            column_indices = []
            if column_names is not None:
                # check if column_names is a list
                if not isinstance(column_names, list):
                    logging.error("column_names must be a list.")
                    return None

                # find indices of the specified columns
                for col_name in column_names:
                    if col_name in COLUMNS:
                        column_indices.append(COLUMNS.index(col_name))
                    else:
                        logging.warning(
                            f"Column '{col_name}' not found in table structure.")

            # SECTION: extract components from table values
            for row in table_values:
                # check if row is a list
                if not isinstance(row, list):
                    logging.error("Table values must be a list of lists.")
                    return None

                # extract components based on column indices
                # component name
                component_name = row[column_indices[0]
                                     ] if column_indices else None
                # component formula
                component_formula = row[column_indices[1]] if len(
                    column_indices) > 1 else None
                # component state
                component_state = row[column_indices[2]] if len(
                    column_indices) > 2 else None

                # add component to components dictionary
                components[component_name] = {
                    'Name': component_name,
                    'Formula': component_formula,
                    'State': component_state
                }

            return components
        except Exception as e:
            logging.error(f"Error getting table components: {e}")
            return None
