# import libs
import logging
import pandas as pd

# Ensure there is no local DataFrame definition that could shadow pandas.DataFrame
from typing import (
    Union,
    Optional,
    Dict,
    List,
    Any,
    Literal,
    Tuple
)
from pythermodb_settings.models import (
    ComponentConfig,
    ComponentRule,
    CustomReference,
    Component
)
# locals
from ..loader import CustomRef
from .builder import TableBuilder
from .symbols_controller import SymbolController
from ..utils import ignore_state_in_prop, create_binary_mixture_id

# NOTE: logger
logger = logging.getLogger(__name__)


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
        CustomReference | str
    ):
        """
        Initialize the ReferenceChecker with a custom reference.

        Parameters
        ----------
        custom_reference : CustomReference | str
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
        load_reference_status = self.load_reference()
        # check load reference status
        if not load_reference_status:
            logging.error("Failed to load custom reference.")
            # set reference to None
            self._reference = None

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

    def check_reference_format(self):
        """
        Check the format of the custom reference. Tree Traversal, DFS and BFS
        """
        pass

    def load_reference(
        self
    ) -> bool:
        """
        Load the custom reference.

        Returns
        -------
        bool
            True if the reference is loaded successfully, otherwise False.
        """
        try:
            # SECTION: check format of custom_reference
            # REVIEW: check_reference_format

            # SECTION: initialize CustomRef
            CustomRef_ = CustomRef(self.custom_reference)
            # check ref
            check_ref = CustomRef_.init_ref()

            # NOTE: check if custom reference is valid
            if check_ref:
                # load custom reference
                self._reference = CustomRef_.load_ref()

            # return
            return True
        except Exception as e:
            logging.error(f"Error loading custom reference: {e}")
            return False

    def get_databook(
        self,
        databook_name: str
    ) -> Optional[Dict[str, Any]]:
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

    def get_databook_names(
        self
    ) -> List[str]:
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

    def get_databook_table_names(
        self,
        databook_name: str
    ) -> List[str]:
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

    def get_table_type(
        self,
        databook_name: str,
        table_name: str
    ):
        """
        Get the type of the table.

        Returns
        -------
        str
            The type of the table.

        Notes
        -----
        The table type can be 'DATA' or 'EQUATIONS'. For Matrix tables, the type is 'DATA'.
        """
        try:
            # get table
            table = self.get_databook_table(databook_name, table_name)

            if table is None:
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return None

            # SECTION: check table
            # NOTE: based on EQUATIONS
            if 'EQUATIONS' in table:
                return 'EQUATIONS'

            # NOTE: based on MATRIX-SYMBOLS
            if 'MATRIX-SYMBOL' in table:
                return 'DATA'

            if 'DATA' in table:
                return 'DATA'
        except Exception as e:
            logging.error(f"Error getting table type: {e}")
            return None

    def is_matrix_table(
        self,
        databook_name: str,
        table_name: str
    ) -> bool:
        """
        Check if the table is a matrix table.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        table_name : str
            The name of the table.

        Returns
        -------
        bool
            True if the table is a matrix table, otherwise False.
        """
        try:
            # get table
            table = self.get_databook_table(databook_name, table_name)

            if table is None:
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return False

            # check if table has 'MATRIX-SYMBOL' key
            if not isinstance(table, dict) or 'MATRIX-SYMBOL' not in table:
                return False

            # if 'MATRIX-SYMBOL' key exists, return True
            return True
        except Exception as e:
            logging.error(f"Error checking if table is matrix: {e}")
            return False

    def get_all_tables_types(
        self
    ) -> Optional[Dict[str, str]]:
        """
        Get the types of all tables in the reference.

        Returns
        -------
        Optional[Dict[str, str]]
            A dictionary containing table names as keys and their types as values if it exists, otherwise None.
        """
        try:
            # get databook names
            databook_names = self.get_databook_names()

            if not databook_names:
                logging.error("No databooks found in the reference.")
                return None

            # SECTION: get table types
            table_types = {}
            for databook_name in databook_names:
                tables = self.get_databook_tables(databook_name)
                if tables is None:
                    logging.error(
                        f"No tables found for databook: {databook_name}")
                    continue

                for table_name in tables.keys():
                    table_type = self.get_table_type(databook_name, table_name)
                    if table_type is not None:
                        table_types[f"{table_name}"] = table_type

            return table_types
        except Exception as e:
            logging.error(f"Error getting reference tables types: {e}")
            return None

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

    def get_databook_tables_types(
        self,
        databook_name: str
    ) -> Optional[Dict[str, str]]:
        """
        Get the types of all tables in a specific databook.

        Parameters
        ----------
        databook_name : str
            The name of the databook.

        Returns
        -------
        Optional[Dict[str, str]]
            A dictionary containing table names as keys and their types as values if it exists, otherwise None.
        """
        try:
            # get databook tables
            tables = self.get_databook_tables(databook_name)

            if tables is None:
                logging.error(f"No tables found for databook: {databook_name}")
                return None

            # SECTION: get table types
            table_types = {}
            for table_name in tables.keys():
                table_type = self.get_table_type(databook_name, table_name)
                if table_type is not None:
                    table_types[table_name] = table_type

            return table_types
        except Exception as e:
            logging.error(f"Error getting databook table types: {e}")
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

    def get_table_description(
        self,
        databook_name: str,
        table_name: str
    ) -> Optional[str]:
        """
        Get the description of a specific table in a databook.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        table_name : str
            The name of the table.

        Returns
        -------
        Optional[str]
            A string containing the description of the table if it exists, otherwise None.
        """
        try:
            # get table
            table = self.get_databook_table(databook_name, table_name)

            if table is None:
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return None

            # check if table has 'DESCRIPTION' key
            if not isinstance(table, dict) or 'DESCRIPTION' not in table:
                logging.error(
                    f"Table '{table_name}' does not contain 'DESCRIPTION' key.")
                return None

            # return the description
            return table['DESCRIPTION']
        except Exception as e:
            logging.error(f"Error getting table description: {e}")
            return None

    def get_table_structure(
            self,
            databook_name: str,
            table_name: str
    ) -> Optional[Dict[str, Any]]:
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

    def get_columns_from_structure(self, structure: Dict[str, Any]) -> List[str]:
        """
        Extract column names from the table structure.

        Parameters
        ----------
        structure : Dict[str, Any]
            The structure dictionary containing table metadata.

        Returns
        -------
        List[str]
            A list of column names.
        """
        try:
            # check if structure is a dictionary
            if not isinstance(structure, dict):
                logging.error("Structure must be a dictionary.")
                return []

            # check if 'COLUMNS' key exists in structure
            if 'COLUMNS' not in structure:
                logging.error("'COLUMNS' key is missing in structure.")
                return []

            # get columns
            columns = structure['COLUMNS']

            # check if columns is a list
            if not isinstance(columns, list):
                logging.error("'COLUMNS' must be a list.")
                return []

            return columns
        except Exception as e:
            logging.error(f"Error extracting columns from structure: {e}")
            return []

    def get_symbols_from_structure(self, structure: Dict[str, Any]) -> List[str]:
        """
        Extract symbols from the table structure.

        Parameters
        ----------
        structure : Dict[str, Any]
            The structure dictionary containing table metadata.

        Returns
        -------
        List[str]
            A list of symbols.
        """
        try:
            # check if structure is a dictionary
            if not isinstance(structure, dict):
                logging.error("Structure must be a dictionary.")
                return []

            # check if 'SYMBOL' key exists in structure
            if 'SYMBOL' not in structure:
                logging.error("'SYMBOL' key is missing in structure.")
                return []

            # get symbols
            symbols = structure['SYMBOL']

            # check if symbols is a list
            if not isinstance(symbols, list):
                logging.error("'SYMBOL' must be a list.")
                return []

            return symbols
        except Exception as e:
            logging.error(f"Error extracting symbols from structure: {e}")
            return []

    def get_matrix_table_symbols(self, databook_name: str, table_name: str):
        '''

        Get the matrix symbols from table `MATRIX-SYMBOL`

        Returns
        -------
        Dict[str, str] | None
            A list of matrix symbols if they exist, otherwise None.
        '''
        try:
            # NOTE: get table
            table = self.get_databook_table(databook_name, table_name)

            if table is None:
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return None

            # check if table has 'MATRIX-SYMBOL' key
            if not isinstance(table, dict) or 'MATRIX-SYMBOL' not in table:
                logging.error(
                    f"Table '{table_name}' does not contain 'MATRIX-SYMBOL' key.")
                return None

            # NOTE: get matrix symbols
            matrix_symbols = table['MATRIX-SYMBOL']

            # check if matrix_symbols is a list
            if not isinstance(matrix_symbols, list):
                logging.error("'MATRIX-SYMBOL' must be a list.")
                return None

            # NOTE: extract symbols from the list of dictionaries
            symbols = self._set_matrix_table_symbols(matrix_symbols)

            return symbols
        except Exception as e:
            logging.error(f"Error getting matrix symbols: {e}")
            return None

    def get_matrix_tables(
            self,
            databook_name: str
    ):
        """
        Get the names of all `matrix tables` in a specific databook.

        Parameters
        ----------
        databook_name : str
            The name of the databook.

        Returns
        -------
        List[dict]
            A list of matrix table names in the databook as:
            - databook name
            - table name
        """
        try:
            # get databook tables
            tables = self.get_databook_tables(databook_name)

            if tables is None:
                logging.error(f"No tables found for databook: {databook_name}")
                return []

            # SECTION: get matrix table names
            matrix_table_names = []
            for table_name in tables.keys():
                if self.is_matrix_table(databook_name, table_name):
                    matrix_table_names.append({
                        'Databook': databook_name,
                        'Table': table_name
                    })

            return matrix_table_names
        except Exception as e:
            logging.error(f"Error getting matrix table names: {e}")
            return []

    def get_all_matrix_tables(self):
        """
        Get the names of all `matrix tables` in all databooks.

        Returns
        -------
        List[dict]
            A list of matrix table names in all databooks as:
            - databook name
            - table name
        """
        try:
            # get databook names
            databook_names = self.get_databook_names()

            if not databook_names:
                logging.error("No databooks found in the reference.")
                return []

            # SECTION: get matrix table names
            all_matrix_table_names = []
            for databook_name in databook_names:
                matrix_tables = self.get_matrix_tables(databook_name)
                all_matrix_table_names.extend(matrix_tables)

            return all_matrix_table_names
        except Exception as e:
            logging.error(f"Error getting all matrix table names: {e}")
            return []

    def get_table_components(
        self,
        databook_name: str,
        table_name: str,
        column_names: List[str] = ['Name', 'Formula', 'State']
    ) -> Optional[Dict[str, Dict[str, Any]]]:
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
        Optional[Dict[str, Dict[str, Any]]]
            A dictionary containing the components if they exist, otherwise None.
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
                component_name = row[
                    column_indices[0]
                ] if column_indices else None
                # component formula
                component_formula = row[
                    column_indices[1]
                ] if len(
                    column_indices) > 1 else None
                # component state
                component_state = row[
                    column_indices[2]
                ] if len(
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

    def get_table_data(
        self,
        databook_name: str,
        table_name: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get the data of a specific table in a databook.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        table_name : str
            The name of the table.

        Returns
        -------
        Optional[List[Dict[str, Any]]]
            A list of dictionaries containing the table data if it exists, otherwise None.
        """
        try:
            # SECTION: get table values
            table_values = self.get_table_values(databook_name, table_name)

            if table_values is None:
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return None

            # SECTION: get table structure
            table_structure = self.get_table_structure(
                databook_name, table_name)

            if table_structure is None:
                logging.error(
                    f"Table '{table_name}' does not contain 'STRUCTURE' key.")
                return None

            # table header
            table_header = table_structure.get('COLUMNS', [])

            if not isinstance(table_header, list):
                logging.error("Table structure 'COLUMNS' must be a list.")
                return None

            # SECTION: convert table values to list of dictionaries
            table_data = []

            # iterate through each row in table_values
            for row in table_values:
                # check if row is a list
                if not isinstance(row, list):
                    logging.error("Table values must be a list of lists.")
                    return None

                # create a dictionary for each row
                row_data = {}
                for idx, value in enumerate(row):
                    # check if idx is within the bounds of table_header
                    if idx < len(table_header):
                        row_data[table_header[idx]] = value.strip(
                        ) if isinstance(value, str) else value

                # append the row data to table_data
                table_data.append(row_data)

            return table_data

        except Exception as e:
            logging.error(f"Error getting table data: {e}")
            return None

    def get_table_data_details(
        self,
        databook_name: str,
        table_name: str
    ):
        '''
        Get the data details (property name and symbols) of a specific table in a databook from the STRUCTURE.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        table_name : str
            The name of the table.

        Returns
        -------
        Optional[List[str]]
            A list containing the data symbols if they exist, otherwise None.
        '''
        try:
            # SECTION: get table structure
            table_structure = self.get_table_structure(
                databook_name,
                table_name
            )

            if table_structure is None:
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return None

            # SECTION: get table type
            table_type = self.get_table_type(databook_name, table_name)

            # check if table type is valid
            if table_type is None:
                logging.error(
                    f"Table '{table_name}' type not found in databook '{databook_name}'.")
                return None

            # check if table type is 'DATA' or 'EQUATIONS'
            if table_type != 'DATA':
                logging.error(
                    f"Table '{table_name}' is not of type 'DATA'.")
                return None

            # SECTION: check structure dict for COLUMNS and SYMBOL
            if not isinstance(table_structure, dict):
                logging.error("Table structure must be a dictionary.")
                return None

            if 'COLUMNS' not in table_structure or 'SYMBOL' not in table_structure:
                logging.error(
                    f"Table '{table_name}' structure must contain 'COLUMNS' and 'SYMBOL' keys.")
                return None

            # NOTE: symbol
            symbol = table_structure['SYMBOL']
            # check if symbol is a list
            if not isinstance(symbol, list):
                logging.error("Table structure 'SYMBOL' must be a list.")
                return None

            # NOTE: columns
            columns = table_structure['COLUMNS']
            # check if columns is a list
            if not isinstance(columns, list):
                logging.error("Table structure 'COLUMNS' must be a list.")
                return None

            # check if lengths of symbol and columns match
            if len(symbol) != len(columns):
                logging.error(
                    f"Table '{table_name}' structure 'SYMBOL' and 'COLUMNS' lengths do not match."
                )
                return None

            # NOTE: result init
            res = {}

            # iterate through columns and symbol
            for idx, col in enumerate(columns):
                # symbol at idx
                symbol_ = symbol[idx]
                if (
                    symbol_ is not None and
                    str(symbol_).strip() != '' and
                    str(symbol_).strip().lower() != 'none'
                ):
                    # set
                    res[col] = symbol_

            # check if res is empty
            if not res:
                logging.warning(
                    f"Table '{table_name}' structure 'SYMBOL' is empty."
                )
                return {}
            # return the symbols
            return res
        except Exception as e:
            logging.error(f"Error getting table data details: {e}")
            return None

    def get_table_equations(
        self,
        databook_name: str,
        table_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the equations of a specific table in a databook.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        table_name : str
            The name of the table.

        Returns
        -------
        Optional[Dict[str, Any]]
            A dictionary containing the equations of the table if it exists, otherwise None.
        """
        try:
            # get table
            table = self.get_databook_table(databook_name, table_name)

            if table is None:
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return None

            # check if table has 'EQUATIONS' key
            if not isinstance(table, dict) or 'EQUATIONS' not in table:
                logging.error(
                    f"Table '{table_name}' does not contain 'EQUATIONS' key.")
                return None

            # return the equations
            return table['EQUATIONS']
        except Exception as e:
            logging.error(f"Error getting table equations: {e}")
            return None

    def get_table_equation_details(
        self,
        databook_name: str,
        table_name: str
    ):
        """
        Get the equation details of a specific table in a databook from the STRUCTURE.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        table_name : str
            The name of the table.

        Returns
        -------
        Optional[str]
            A string containing the equation symbol if it exists, otherwise None.
        """
        try:
            # SECTION: get table structure
            table_structure = self.get_table_structure(
                databook_name, table_name)

            if table_structure is None:
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return None

            # SECTION: get table type
            table_type = self.get_table_type(databook_name, table_name)

            # check if table type is valid
            if table_type is None:
                logging.error(
                    f"Table '{table_name}' type not found in databook '{databook_name}'.")
                return None

            # check if table type is 'EQUATIONS'
            if table_type != 'EQUATIONS':
                logging.error(
                    f"Table '{table_name}' is not of type 'EQUATIONS'.")
                return None

            # SECTION: check structure dict for COLUMNS and SYMBOL
            if not isinstance(table_structure, dict):
                logging.error("Table structure must be a dictionary.")
                return None

            if 'COLUMNS' not in table_structure or 'SYMBOL' not in table_structure:
                logging.error(
                    f"Table '{table_name}' structure must contain 'COLUMNS' and 'SYMBOL' keys.")
                return None

            # NOTE: symbol
            symbol = table_structure['SYMBOL']
            # check if symbol is a list
            if not isinstance(symbol, list):
                logging.error("Table structure 'SYMBOL' must be a list.")
                return None

            # NOTE: columns
            columns = table_structure['COLUMNS']
            # check if columns is a list
            if not isinstance(columns, list):
                logging.error("Table structure 'COLUMNS' must be a list.")
                return None

            # find index where COLUMNS has 'Eq' or 'eq'
            if 'Eq' in columns:
                eq_index = columns.index('Eq')
            elif 'eq' in columns:
                eq_index = columns.index('eq')
            else:
                logging.error(
                    f"Table '{table_name}' structure 'COLUMNS' must contain 'Eq' or 'eq'.")
                return None

            # check if eq_index is within the bounds of symbol
            if eq_index >= len(symbol):
                logging.error(
                    f"Table '{table_name}' structure 'SYMBOL' does not have an entry for 'Eq' or 'eq'.")
                return None

            # get the symbol at eq_index
            table_equation_symbol = str(symbol[eq_index])

            # return the symbol
            return table_equation_symbol

        except Exception as e:
            logging.error(f"Error getting table equation symbol: {e}")
            return None

    def get_table_matrix_symbols(
        self,
        databook_name: str,
        table_name: str
    ) -> Optional[List[str]]:
        """
        Get the matrix symbols of a specific table in a databook.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        table_name : str
            The name of the table.

        Returns
        -------
        Optional[List[str]]
            A list of matrix symbols if they exist, otherwise None.
        """
        try:
            # get table
            table = self.get_databook_table(databook_name, table_name)

            if table is None:
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return None

            # check if table has 'MATRIX-SYMBOL' key
            if not isinstance(table, dict) or 'MATRIX-SYMBOL' not in table:
                logging.error(
                    f"Table '{table_name}' does not contain 'MATRIX-SYMBOL' key.")
                return None

            # return the matrix symbols
            return table['MATRIX-SYMBOL']
        except Exception as e:
            logging.error(f"Error getting table matrix symbols: {e}")
            return None

    def _set_matrix_table_symbols(
        self,
        matrix_symbols: List[str | Dict[str, str]],
    ) -> Dict[str, str]:
        '''
        Set the matrix symbols in the correct format.

        Parameters
        ----------
        matrix_symbols : List[str | Dict[str, str]]
            A list of matrix symbols as strings or dictionaries.

        Returns
        -------
        Dict[str, str]
            A list of matrix symbols as dictionaries.

        Notes
        -----
        The matrix symbols are stored in the `MATRIX-SYMBOL` key of the table as:

        ```yaml
        TABLE_NAME:
          MATRIX-SYMBOL:
            - Description1: Symbol1
            - Description2: Symbol2
            - Symbol3
            - Symbol4
        ```

        Then they are converted to a dictionary as:

        ```python
        {
            'Description1': 'Symbol1',
            'Description2': 'Symbol2',
            'Symbol3': 'Symbol3',
            'Symbol4': 'Symbol4'
        }
        ```
        '''
        try:
            # check if matrix_symbols is a list
            if not isinstance(matrix_symbols, list):
                logging.error("matrix_symbols must be a list.")
                return []

            # SECTION: convert matrix_symbols to list of dictionaries
            matrix_symbols_dict = {}
            for item in matrix_symbols:
                if isinstance(item, dict):
                    matrix_symbols_dict.update(item)
                elif isinstance(item, str):
                    matrix_symbols_dict[item] = item
                else:
                    logging.warning(
                        f"Invalid item in matrix_symbols: {item}. Must be a dictionary or string.")

            return matrix_symbols_dict
        except Exception as e:
            logging.error(f"Error setting matrix symbols: {e}")
            return {}

    def get_components_data(
        self,
        databook_name: str,
        table_name: str,
        component_key: Literal['Name-State', 'Formula-State'] = 'Name-State'
    ) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Get the components data from a specific table in a databook.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        table_name : str
            The name of the table.
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for the components, by default 'Name-State'.

        Returns
        -------

        """
        try:
            # SECTION: get table data
            table_data = self.get_table_data(databook_name, table_name)

            if table_data is None:
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return None

            # SECTION: build components data
            components_data = {}

            # iterate through each row in table_data
            for row in table_data:
                # check if row is a dictionary
                if not isinstance(row, dict):
                    logging.error("Table data must be a list of dictionaries.")
                    return None

                # check component_key
                if component_key == 'Name-State':
                    # key
                    key = f"{row.get('Name', '')}-{row.get('State', '')}".strip()
                    # values
                elif component_key == 'Formula-State':
                    # key
                    key = f"{row.get('Formula', '')}-{row.get('State', '')}".strip()
                else:
                    logging.error(
                        f"Invalid component_key: {component_key}. Must be 'Name-State' or 'Formula-State'.")
                    return None

                # save all values
                components_data[key] = row

            # return components data
            return components_data
        except Exception as e:
            logging.error(f"Error getting components data: {e}")
            return None

    def get_component_data(
        self,
        component_name: str,
        component_formula: str,
        component_state: str,
        databook_name: str,
        table_name: str,
        component_key: Literal['Name-State', 'Formula-State'] = 'Name-State'
    ):
        """
        Get the data of a specific component from a specific table in a databook.

        Parameters
        ----------
        component_name : str
            The name of the component.
        component_formula : str
            The formula of the component.
        component_state : str
            The state of the component.
        databook_name : str
            The name of the databook.
        table_name : str
            The name of the table.
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for the components, by default 'Name-State'.

        Returns
        -------
        Optional[Dict[str, Any]]
            A dictionary containing the component data if it exists, otherwise None.

        Notes
        -----
        The search is `case-insensitive` and ignores leading/trailing whitespace.
        """
        try:
            # SECTION: get table data
            table_data = self.get_table_data(databook_name, table_name)

            # check if table data is valid
            if table_data is None:
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return None

            # SECTION: find component data
            for row in table_data:
                # check if row is a dictionary
                if not isinstance(row, dict):
                    logging.error("Table data must be a list of dictionaries.")
                    return None

                # check component_key
                if component_key == 'Name-State':
                    # check if component matches
                    if (
                        row.get('Name', '').strip().lower() == component_name.strip().lower() and
                        row.get('State', '').strip().lower(
                        ) == component_state.strip().lower()
                    ):
                        return row
                elif component_key == 'Formula-State':
                    # check if component matches
                    if (
                        row.get('Formula', '').strip().lower() == component_formula.strip().lower() and
                        row.get('State', '').strip().lower(
                        ) == component_state.strip().lower()
                    ):
                        return row
                else:
                    logging.error(
                        f"Invalid component_key: {component_key}. Must be 'Name-State' or 'Formula-State'.")
                    return None

            # if component not found
            logging.warning(
                f"Component '{component_name}' with formula '{component_formula}' and state '{component_state}' not found in table '{table_name}'.")

            return None
        except Exception as e:
            logging.error(f"Error getting component data: {e}")
            return None

    def get_binary_matrix_data(
        self,
        components: List[Component],
        databook_name: str,
        table_name: str,
        column_name: str = 'Mixture',
        component_key: Literal[
            'Name-State', 'Formula-State'
        ] = 'Name-State',
        mixture_key: Literal[
            'Name', 'Formula'
        ] = 'Name',
        delimiter: str = '|',
        ignore_component_state: Optional[bool] = False,
    ):
        '''
        Get the matrix data for a binary mixture of components from a specific table in a databook.

        Parameters
        ----------
        components : List[Component]
            A list of Component objects (must be 2 components for binary mixture).
        databook_name : str
            The name of the databook.
        table_name : str
            The name of the table.
        column_name : str, optional
            The name of the column containing the mixture information, by default 'Mixture'.
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for the components, by default 'Name-State'.
        mixture_key : Literal['Name', 'Formula'], optional
            The key to use for the mixture components, by default 'Name'.
        delimiter : str, optional
            The delimiter used to separate component names/formulas in the mixture column, by default '|'.
        ignore_component_state : Optional[bool], optional
            Whether to ignore the state of the components when matching, by default False.

        Returns
        -------
        Optional[Dict[str, Any]]
            A dictionary containing the matrix data if it exists, otherwise None.

        Notes
        -----
        1- The search is `case-insensitive` and ignores leading/trailing whitespace.
        2- The searched table must have a 'MIXTURE' key in its structure.
        3- The 'MIXTURE' key must contain the names of the two components in the format 'Component1|Component2'.
        4- For each component, the 'Name' or 'Formula' and 'State' must match the provided components based on the component_key.
        '''
        try:
            # SECTION: check table
            is_matrix_table = self.is_matrix_table(
                databook_name=databook_name,
                table_name=table_name
            )
            if not is_matrix_table:
                logging.error(
                    f"Table '{table_name}' in databook '{databook_name}' is not a matrix table.")
                return None

            # SECTION: get table data
            table_data = self.get_table_data(databook_name, table_name)

            # check if table data is valid
            if table_data is None:
                logging.error(
                    f"Table '{table_name}' not found in databook '{databook_name}'.")
                return None

            # SECTION: check components
            if not isinstance(components, list) or len(components) != 2:
                logging.error("Exactly two components must be provided.")
                return None

            # unpack components
            component_1 = components[0]
            component_2 = components[1]

            # SECTION: construct mixture string
            binary_mixture_id = create_binary_mixture_id(
                component_1=component_1,
                component_2=component_2,
                mixture_key=mixture_key
            )

            if not binary_mixture_id:
                logging.error("Failed to create binary mixture ID.")
                return {"results": {'available': False, 'message': 'Failed to create binary mixture ID.'}}

            # >> standardize binary mixture id
            binary_mixture_id = binary_mixture_id.lower().strip()

            # SECTION: collect table data
            # NOTE: get table structure
            table_structure = self.get_table_structure(
                databook_name=databook_name,
                table_name=table_name
            )
            # >> check
            if table_structure is None:
                logging.error(
                    f"Table '{table_name}' structure not found in databook '{databook_name}'.")
                return None

            # NOTE: get columns
            columns = self.get_columns_from_structure(
                structure=table_structure
            )
            # >> check
            if not columns:
                logging.error(
                    f"Table '{table_name}' structure columns not found in databook '{databook_name}'.")
                return None

            # NOTE: normalize mixture id function

            def normalize_mixture_id(
                mixture: str,
                delimiter: str
            ) -> str:
                parts = mixture.lower().strip().split(delimiter)
                return delimiter.join(sorted(parts))

            # SECTION: search for the mixture in the table data
            # NOTE: build dataframe for easier searching
            df = pd.DataFrame(
                data=table_data,
                columns=columns
            )

            # NOTE: normalized dataframe
            # normalized column
            normalized_column_name = f'Normalized_{column_name}'

            # ! create normalized column
            df[normalized_column_name] = df[column_name].apply(
                lambda x: normalize_mixture_id(str(x).strip(), delimiter)
            )

            # SECTION: filter dataframe for the mixture
            # ! normalized binary mixture id
            normalized_binary_mixture_id = normalize_mixture_id(
                mixture=binary_mixture_id,
                delimiter=delimiter
            )

            # ! mask
            mask_ = df[normalized_column_name].str.strip(
            ) == normalized_binary_mixture_id
            # found rows
            mixture_df = df[mask_]
            # << log
            # print(mixture_df)

            # NOTE: initialize
            # count row
            available_count = 0
            # combined dataframe
            combined_df = pd.DataFrame()
            # component data
            component_data = {
                component_1.name: [],
                component_2.name: []
            }

            # NOTE: check availability
            if mixture_df.empty:
                all_available = False
            else:
                # SECTION: check component name/formula and state in each row
                mask_component_1 = None
                mask_component_2 = None

                if component_key == 'Name-State' and ignore_component_state is False:
                    mask_component_1 = (
                        (
                            mixture_df['Name'].str.lower().str.strip(
                            ) == component_1.name.lower().strip()
                        ) &
                        (
                            mixture_df['State'].str.lower().str.strip(
                            ) == component_1.state.lower().strip()
                        )
                    )
                    mask_component_2 = (
                        (
                            mixture_df['Name'].str.lower().str.strip(
                            ) == component_2.name.lower().strip()
                        ) &
                        (
                            mixture_df['State'].str.lower().str.strip()
                            == component_2.state.lower().strip()
                        )
                    )
                elif component_key == 'Formula-State' and ignore_component_state is False:
                    mask_component_1 = (
                        (
                            mixture_df['Formula'].str.lower().str.strip(
                            ) == component_1.formula.lower().strip()
                        ) &
                        (
                            mixture_df['State'].str.lower().str.strip()
                            == component_1.state.lower().strip()
                        )
                    )
                    mask_component_2 = (
                        (
                            mixture_df['Formula'].str.lower().str.strip(
                            ) == component_2.formula.lower().strip()
                        ) &
                        (
                            mixture_df['State'].str.lower().str.strip()
                            == component_2.state.lower().strip()
                        )
                    )
                elif ignore_component_state:
                    # NOTE: set Name for chosen Name-State
                    component_key_ = 'Name' if component_key == 'Name-State' else 'Formula'

                    # NOTE: compare
                    # >> component set id
                    component_1_id = component_1.name if component_key_ == 'Name' else component_1.formula
                    component_2_id = component_2.name if component_key_ == 'Name' else component_2.formula

                    # masks
                    mask_component_1 = (
                        mixture_df[component_key_].str.lower().str.strip()
                        == component_1_id.lower().strip()
                    )
                    mask_component_2 = (
                        mixture_df[component_key_].str.lower().str.strip()
                        == component_2_id.lower().strip()
                    )
                else:
                    raise ValueError(
                        "Invalid component_key or ignore_component_state configuration.")

                # NOTE: check
                if mask_component_1 is None or mask_component_2 is None:
                    raise ValueError(
                        "Component masks could not be determined.")
                # check if both components are found
                if not mixture_df[mask_component_1].empty and not mixture_df[mask_component_2].empty:
                    all_available = True
                    # count available rows containing the mixture
                    available_count = len(mixture_df)

                    # ! combine rows (series) to dataframe
                    combined_df = pd.concat(
                        [mixture_df[mask_component_1],
                            mixture_df[mask_component_2]]
                    ).drop_duplicates().reset_index(drop=True)
                else:
                    all_available = False
                    combined_df = pd.DataFrame()

            # NOTE: data
            if not combined_df.empty:
                # data as list of dict
                # data = combined_df.to_dict(orient='records')
                # component data first row data
                component_data_1_df = mixture_df[mask_component_1]
                # >> values
                component_data_1 = component_data_1_df.values.tolist()[
                    0
                ]
                # >> set
                component_data[component_1.name] = component_data_1

                # component data second row data
                component_data_2_df = mixture_df[mask_component_2]
                # >> values
                component_data_2 = component_data_2_df.values.tolist()[
                    0
                ]
                # >> set
                component_data[component_2.name] = component_data_2

            # SECTION: Format results
            res = {
                'databook_name': databook_name,
                'table_name': table_name,
                'mixture_name': binary_mixture_id,
                'availability': all_available,
                'available_count': available_count,
                'component_data': component_data,
            }

            # return
            return res
        except Exception as e:
            logging.error(f"Error getting components matrix data: {e}")
            return None

    def generate_property_mapping(
            self,
            databook_name: str,
            table_name: Optional[str] = None
    ) -> Dict[str, str]:
        '''
        Generate a property mapping for a given databook, this dictionary can be used to map property names to their symbols.

        Parameters
        ----------
        databook_name : str
            The name of the databook.

        Returns
        -------
        Dict[str, str]
            A dictionary mapping property names to their symbols as keys and values.

        Notes
        -----
        1- The property mapping is generated by iterating through each table in the databook and extracting the property names and symbols from the table structure.
        2- If a specific table name is provided, only that table is processed.
        3- The function handles different table types, including 'DATA' and 'EQUATIONS', and also considers matrix tables.
        4- The resulting dictionary contains unique property names and symbols, with no duplicates.

        Example
        -------
        >>> checker = DataChecker('path/to/databooks')
        >>> property_mapping = checker.generate_property_mapping('ExampleDatabook')
        >>> print(property_mapping)

        {
            'ideal-gas-heat-capacity': 'Cp_IG',
            'Molecular-Weight': 'MW',
            'Critical-Temperature': 'Tc',
            'Critical-Pressure': 'Pc',
            'Critical-Molar-Volume': 'Vc',
            'Critical-Compressibility-Factor': 'Zc',
            'Acentric-Factor': 'AcFa',
            'Enthalpy-of-Formation': 'EnFo',
            'Gibbs-Energy-of-Formation': 'GiEnFo',
            'vapor-pressure': 'VaPr',
            'a constant parameter': 'a',
            'b': 'b',
            'c': 'c',
            'alpha': 'alpha'
        }
        '''
        try:
            # SECTION: get tables
            tables = self.get_databook_tables(databook_name)

            if tables is None:
                logging.error(f"No tables found for databook: {databook_name}")
                return {}

            # NOTE: check if table_name is provided
            if table_name is not None:
                # strip table name
                table_name = table_name.strip()

                # check if table_name exists in tables
                if table_name not in tables.keys():
                    logging.error(
                        f"Table '{table_name}' not found in databook '{databook_name}'.")
                    return {}

                # init tables
                tables_ = {}
                # add to tables
                tables_[table_name] = tables[table_name]

                # update tables
                tables = tables_

            # SECTION: init property mapping
            property_mapping = {}
            # init matrix
            is_matrix: bool = False

            # iterate through each table
            for table_name, table in tables.items():
                # get table type
                table_type = self.get_table_type(databook_name, table_name)
                if table_type is None:
                    logging.error(f"Table type for '{table_name}' not found.")
                    continue

                # NOTE: check table type
                if table_type not in ['DATA', 'EQUATIONS']:
                    logging.warning(
                        f"Table '{table_name}' has unsupported type '{table_type}'. Skipping.")
                    continue

                # NOTE: check matrix
                is_matrix = self.is_matrix_table(
                    databook_name,
                    table_name
                )

                # NOTE: get table details
                if table_type == 'DATA' and not is_matrix:  # ! not matrix
                    table_details = self.get_table_data_details(
                        databook_name,
                        table_name
                    )
                    if table_details is None:
                        logging.error(
                            f"Table details for '{table_name}' not found.")
                        continue

                    # update property mapping
                    property_mapping.update(table_details)
                elif table_type == 'DATA' and is_matrix:  # ! matrix
                    matrix_symbols = self.get_matrix_table_symbols(
                        databook_name,
                        table_name
                    )
                    if matrix_symbols is None:
                        logging.error(
                            f"Matrix symbols for '{table_name}' not found.")
                        continue

                    # iterate through each matrix symbol
                    for symbol_description, symbol in matrix_symbols.items():
                        if symbol is not None and str(symbol).strip() not in ['None', '']:
                            # add to property mapping
                            property_mapping[symbol_description] = symbol
                elif table_type == 'EQUATIONS':  # ! equations
                    equation_symbol = self.get_table_equation_details(
                        databook_name,
                        table_name
                    )
                    if equation_symbol is None:
                        logging.error(
                            f"Equation symbol for '{table_name}' not found.")
                        continue

                    # add to property mapping
                    property_mapping[table_name] = equation_symbol
                else:
                    logging.warning(
                        f"Table '{table_name}' has unsupported type '{table_type}'. Skipping.")
                    continue

            #  return property mapping
            return property_mapping
        except Exception as e:
            logging.error(f"Error generating property mapping: {e}")
            return {}

    def get_property_mappings(
        self,
        databook_name: str,
        table_name: Optional[str] = None
    ) -> List[str]:
        '''
        Get the property mappings for a given databook.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        table_name : Optional[str], optional
            The name of the table to filter by, by default None.

        Returns
        -------
        List[str]
            A list of property names with relevant symbols.
        '''
        try:
            # generate property mapping
            property_mapping = self.generate_property_mapping(
                databook_name,
                table_name
            )

            # return the property names
            mappings = list(property_mapping.keys()) + \
                list(property_mapping.values())
            mappings = list(set(mappings))  # remove duplicates

            # check if mappings is empty
            if not mappings:
                logging.warning(
                    f"No property mappings found for databook '{databook_name}'"
                    + (f" and table '{table_name}'." if table_name else ".")
                )
                return []

            # check
            return mappings
        except Exception as e:
            logging.error(f"Error getting property mappings: {e}")
            return []

    def prop_available_in_databook(
        self,
        prop_ids: List[str],
        databook_name: str,
        table_name: Optional[str] = None
    ) -> Dict[str, bool]:
        '''
        Check if the given property IDs are available in the specified databook (and table if provided).

        Parameters
        ----------
        prop_ids : List[str]
            A list of property IDs to check.
        databook_name : str
            The name of the databook.
        table_name : Optional[str], optional
            The name of the table to filter by, by default None.

        Returns
        -------
        Dict[str, bool]
            A dictionary with property IDs as keys and availability (True/False) as values.
        '''
        try:
            # SECTION: get property mappings
            property_mappings = self.get_property_mappings(
                databook_name,
                table_name
            )

            if not property_mappings:
                logging.warning(
                    f"No property mappings found for databook '{databook_name}'"
                    + (f" and table '{table_name}'." if table_name else ".")
                )
                return {prop_id: False for prop_id in prop_ids}

            # SECTION: check availability
            availability = {}
            for prop_id in prop_ids:
                availability[prop_id] = prop_id in property_mappings

            return availability
        except Exception as e:
            logging.error(f"Error checking property availability: {e}")
            return {prop_id: False for prop_id in prop_ids}

    def generate_reference_link(
        self,
        databook_name: str,
        table_names: Optional[str | List[str]] = None,
        component_name: Optional[str] = None,
        component_formula: Optional[str] = None,
        component_state: Optional[str] = None,
        component_key: Literal['Name-State', 'Formula-State'] = 'Name-State',
        ignore_component_state: Optional[bool] = False,
        **kwargs
    ) -> Dict[str, Dict[str, str]]:
        """
        Generate a reference link for a component.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        table_names : Optional[str | List[str]], optional
            The name(s) of the table(s) to include in the reference link, by default None.
        component_name : Optional[str], optional
            The name of the component to include in the reference link, by default None.
        component_formula : Optional[str], optional
            The formula of the component to include in the reference link, by default None.
        component_state : Optional[str], optional
            The state of the component to include in the reference link, by default None.
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for the component, by default 'Name-State'.
        ignore_component_state : Optional[bool], optional
            Whether to ignore the component state when checking availability, by default False.
        kwargs : dict, optional
            Additional keyword arguments, including:
            - ignore_state_props : Optional[List[str]], optional
                A list of state properties to ignore when checking availability, by default None.

        Returns
        -------
        Dict[str, Dict[str, str]]
            A dictionary containing the reference link for the component.
        """
        try:
            # SECTION: additional kwargs
            ignore_state_props: Optional[List[str]] = kwargs.get(
                'ignore_state_props', None
            )

            # >>> check
            if ignore_state_props is None:
                ignore_state_props = []
            elif not isinstance(ignore_state_props, list):
                logger.warning(
                    "ignore_state_props must be a list. Setting to empty list.")
                ignore_state_props = []

            # SECTION: get tables
            tables = self.get_databook_tables(databook_name)

            # check if tables are valid
            if tables is None:
                logging.error(f"No tables found for databook: {databook_name}")
                return {}

            # SECTION: construct the reference config
            reference_config = {
                'DATA': {},
                'EQUATIONS': {},
            }

            # NOTE: check if table_name is provided
            if table_names is not None:
                # convert table_name to list if it is a string
                if isinstance(table_names, str):
                    table_names = [table_names]

                # strip table names
                table_names = [name.strip() for name in table_names]

                # init tables
                tables_ = {}
                # iterate through each table name
                for name in table_names:
                    # check if name exists in tables
                    if name in tables.keys():
                        # add to tables
                        tables_[name] = tables[name]

                # update tables
                tables = tables_

            # SECTION: check component availability
            # NOTE: check if component details are provided
            if component_name and component_formula and component_state:
                # check if component is available in the table
                component_availability = self.check_component_availability(
                    component_name=component_name,
                    component_formula=component_formula,
                    component_state=component_state,
                    databook_name=databook_name,
                    component_key=component_key,
                    ignore_component_state=ignore_component_state,
                    ignore_state_props=ignore_state_props
                )
            else:
                component_availability = None

            # NOTE: update tables if component is not available in any table
            if component_availability:
                # remove tables where component is not available
                tables = {
                    k: v for k, v in tables.items()
                    if component_availability.get(k, {}).get('available', False)
                }

            # SECTION: go through each table content
            # iterate through each table
            for table_name, table in tables.items():

                # NOTE: check if component is available in the table
                if component_name and component_formula and component_state:
                    if component_availability:
                        # ! check component availability in the current table
                        check_ = component_availability[table_name]
                        if not check_['available']:
                            # skip this table
                            continue

                # NOTE: table type
                table_type = self.get_table_type(databook_name, table_name)
                if table_type is None:
                    logging.error(f"Table type for '{table_name}' not found.")
                    continue

                # NOTE: matrix symbols
                matrix_symbols = table.get('MATRIX-SYMBOL', False)

                # get table structure
                structure = table.get('STRUCTURE', None)
                if not isinstance(structure, dict):
                    logging.error(
                        f"Structure for table '{table_name}' is not a dictionary.")
                    continue

                if structure is None:
                    logging.error(
                        f"Structure for table '{table_name}' not found.")
                    continue

                # get columns
                columns = structure.get('COLUMNS', [])
                if not isinstance(columns, list):
                    logging.error(
                        f"Columns for table '{table_name}' are not a list.")
                    continue

                # get symbols
                symbols = structure.get('SYMBOL', [])
                if not isinstance(symbols, list):
                    logging.error(
                        f"Symbols for table '{table_name}' are not a list.")
                    continue

                # check table type
                if table_type == 'DATA':
                    # check
                    if not matrix_symbols:
                        # ! DATA
                        # iterate through each column and symbols
                        for col, symbol in zip(columns, symbols):
                            # check if symbol is None
                            if symbol is not None and symbol not in ['None', '']:
                                # NOTE: strip and convert to string if not already
                                # ? column and symbol must be strings
                                col = col.strip() if isinstance(col, str) else str(col).strip()
                                symbol = symbol.strip() if isinstance(symbol, str) else str(symbol).strip()

                                # add to reference config
                                reference_config['DATA'].update(
                                    {
                                        col: symbol
                                    }
                                )
                    else:
                        # ! MATRIX-SYMBOL
                        # NOTE: build from matrix symbols
                        matrix_symbols_ = self._set_matrix_table_symbols(
                            matrix_symbols
                        )

                        # >> iterate through each matrix symbol
                        for symbol_des, symbol in matrix_symbols_.items():
                            # check if symbol is None
                            if symbol is not None and symbol not in ['None', '']:
                                # NOTE: strip and convert to string if not already
                                # ? symbol must be a string
                                symbol = symbol.strip() if isinstance(symbol, str) else str(symbol).strip()

                                # add to reference config
                                reference_config['DATA'].update(
                                    {
                                        symbol_des: symbol
                                    }
                                )

                elif table_type == 'EQUATIONS':
                    # ! EQUATIONS
                    # get table equations
                    equations = table.get('EQUATIONS', None)
                    if not isinstance(equations, dict):
                        logging.error(
                            f"Equations for table '{table_name}' are not a dictionary.")
                        continue

                    if equations is None:
                        logging.error(
                            f"Equations for table '{table_name}' not found.")
                        continue

                    # select the first equation
                    eq_1 = equations.get('EQ-1', None)
                    if not isinstance(eq_1, dict):
                        logging.error(
                            f"Equation 'EQ-1' for table '{table_name}' is not a dictionary.")
                        continue

                    # NOTE: equation body
                    equation_body = eq_1.get('BODY', None)

                    # check if equation body is empty
                    if (
                        not equation_body or
                        not isinstance(equation_body, list)
                    ):
                        logging.warning(
                            f"Equation body for '{table_name}' is empty, or not a list.")
                        continue

                    # ! analyze the equation body
                    equation_analyzer_res = TableBuilder.analyze_equation(
                        equation_body,
                    )

                    if not equation_analyzer_res:
                        logging.warning(
                            f"No valid components found in equation body for '{table_name}'.")
                        continue

                    # get equation return
                    equation_return = equation_analyzer_res.get(
                        'returns', None)

                    if equation_return is None:
                        logging.warning(
                            f"No return value found in equation body for '{table_name}'.")
                        continue

                    # check if equation_return is a list
                    if not isinstance(equation_return, list):
                        logging.error(
                            f"Equation return for '{table_name}' is not a list.")
                        continue

                    # NOTE: set
                    return_name = equation_return[0].get('name', None)
                    return_symbol = equation_return[0].get('symbol', None)

                    # check if return_name and return_symbol are valid
                    if return_name is None or return_symbol is None:
                        logging.error(
                            f"Return name or symbol not found in equation body for '{table_name}'.")
                        continue

                    # add to reference config
                    reference_config['EQUATIONS'].update(
                        {
                            return_name: return_symbol
                        }
                    )

            # SECTION: check if reference config is empty
            if reference_config['DATA'] == {}:
                # add dummy data
                pass

            if reference_config['EQUATIONS'] == {}:
                # add dummy equations
                pass

            # return the reference config
            return reference_config
        except Exception as e:
            logging.error(f"Error generating reference config: {e}")
            return {
                'DATA': {},
                'EQUATIONS': {},
            }

    def generate_binary_mixture_reference_link(
        self,
        databook_name: str,
        table_names: Optional[str | List[str]] = None,
        components: Optional[List[Component]] = None,
        component_key: Literal['Name-State', 'Formula-State'] = 'Name-State',
        mixture_key: Literal['Name', 'Formula'] = 'Name',
        delimiter: str = '|',
        column_name: str = 'Mixture',
        ignore_component_state: Optional[bool] = False,
        **kwargs
    ):
        '''
        Generate a reference link for a binary mixture of components.

        Parameters
        ----------
        databook_name : str
            The name of the databook.
        table_names : Optional[str | List[str]], optional
            The name(s) of the table(s) to include in the reference link, by default None.
        components : Optional[List[Component]], optional
            A list of two Component objects representing the binary mixture, by default None.
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for the components, by default 'Name-State'.
        mixture_key : Literal['Name', 'Formula'], optional
            The key to use for the mixture, by default 'Name'.
        delimiter : str, optional
            The delimiter to use for the mixture, by default '-'.
        column_name : str, optional
            The name of the column containing the mixture, by default 'Mixture'.
        ignore_component_state : Optional[bool], optional
            Whether to ignore the component state when checking availability, by default False.
        kwargs : dict, optional
            Additional keyword arguments, including:
            - ignore_state_props : Optional[List[str]], optional
                A list of state properties to ignore when checking availability, by default None.

        Returns
        -------
        Dict[str, Dict[str, Union[bool, str, Dict[str, List[str]]]]]
            A dictionary containing the reference link for the binary mixture.

        Notes
        -----
        1- The function checks the availability of the binary mixture in the specified databook and tables.
        2- If the components are not available in any table, the reference link will be empty.
        3- The function handles matrix tables and extracts relevant symbols for the reference link.
        4- The resulting dictionary contains 'DATA' and 'EQUATIONS' sections with relevant symbols.

        Example
        -------
        >>> checker = DataChecker('path/to/databooks')
        >>> component_1 = Component(name='Methanol', formula='CH3OH', state='liquid')
        >>> component_2 = Component(name='Water', formula='H2O', state='liquid')
        >>> reference_link = checker.generate_binary_mixture_reference_link(
        ...     databook_name='ExampleDatabook',
        ...     components=[component_1, component_2]
        ... )
        >>> print(reference_link)

        {
            'DATA': {
                'ideal-gas-heat-capacity': 'Cp_IG',
                'Molecular-Weight': 'MW
                'binary-parameters': 'alpha_i_j'
                '
                ...
            },
            'EQUATIONS': {
                'vapor-pressure': 'VaPr',
                ...
            }
        }
        '''
        try:
            # SECTION: additional kwargs
            ignore_state_props: Optional[List[str]] = kwargs.get(
                'ignore_state_props', None
            )

            # >>> check
            if ignore_state_props is None:
                ignore_state_props = []
            elif not isinstance(ignore_state_props, list):
                logger.warning(
                    "ignore_state_props must be a list. Setting to empty list.")
                ignore_state_props = []

            # SECTION: get tables
            tables = self.get_databook_tables(databook_name)

            # check if tables are valid
            if tables is None:
                logging.error(f"No tables found for databook: {databook_name}")
                return {}

            # SECTION: construct the reference config
            reference_config = {
                'DATA': {},
                'EQUATIONS': {},
            }

            # NOTE: check if table_name is provided
            if table_names is not None:
                # convert table_name to list if it is a string
                if isinstance(table_names, str):
                    table_names = [table_names]

                # strip table names
                table_names = [name.strip() for name in table_names]

                # init tables
                tables_ = {}
                # iterate through each table name
                for name in table_names:
                    # check if name exists in tables
                    if name in tables.keys():
                        # add to tables
                        tables_[name] = tables[name]

                # update tables
                tables = tables_

            # SECTION: check mixture availability
            # NOTE: check if components are provided
            if components:
                if not isinstance(components, list) or len(components) != 2:
                    logging.error(
                        "Components must be a list of two Component objects.")
                    return {}

                component_1 = components[0]
                component_2 = components[1]

                # NOTE: create binary mixture id
                binary_mixture_id = create_binary_mixture_id(
                    component_1,
                    component_2,
                    mixture_key=mixture_key,
                    delimiter=delimiter
                )

                if not all(isinstance(c, Component) for c in components):
                    logging.error(
                        "All items in components must be Component objects.")
                    return {}

                # NOTE: mixture availability checked in all tables
                mixture_availability = self.check_binary_mixture_availability(
                    components=components,
                    databook_name=databook_name,
                    table_name=None,
                    column_name=column_name,
                    component_key=component_key,
                    mixture_key=mixture_key,
                    delimiter=delimiter,
                    ignore_component_state=ignore_component_state,
                    ignore_state_props=ignore_state_props
                )
            else:
                # NOTE: components not provided
                mixture_availability = None
                binary_mixture_id = None

            # NOTE: update tables if component is not available in any table
            if mixture_availability:
                # remove tables where component is not available
                tables = {
                    k: v for k, v in tables.items()
                    if mixture_availability.get(k, {}).get('available', False)
                }

            # SECTION: go through each table content
            # iterate through each table
            for table_name, table in tables.items():

                # NOTE: check if component is available in the table
                if components:
                    if mixture_availability:
                        # ! check mixture availability in the current table
                        check_ = mixture_availability[table_name]
                        if not check_['available']:
                            # skip this table
                            continue

                # NOTE: table type
                table_type = self.get_table_type(databook_name, table_name)
                if table_type is None:
                    logging.error(f"Table type for '{table_name}' not found.")
                    continue

                # NOTE: matrix symbols
                matrix_symbols = table.get('MATRIX-SYMBOL', False)

                # check table type
                if table_type == 'DATA' and matrix_symbols:  # ! matrix (ONLY)

                    # ! MATRIX-SYMBOL
                    # NOTE: build from matrix symbols
                    matrix_symbols_ = self._set_matrix_table_symbols(
                        matrix_symbols
                    )

                    # >> iterate through each matrix symbol
                    for symbol_des, symbol in matrix_symbols_.items():
                        # check if symbol is None
                        if symbol is not None and symbol not in ['None', '']:
                            # NOTE: strip and convert to string if not already
                            # ? symbol must be a string
                            symbol = symbol.strip() if isinstance(symbol, str) else str(symbol).strip()

                            # add to reference config
                            reference_config['DATA'].update(
                                {
                                    symbol_des: symbol
                                }
                            )
                else:
                    # skip
                    logging.warning(
                        f"Table '{table_name}' is not a matrix DATA table. Skipping.")
                    continue

            # SECTION: check if reference config is empty
            if reference_config['DATA'] == {}:
                # add dummy data
                pass

            if reference_config['EQUATIONS'] == {}:
                # add dummy equations
                pass

            # return the reference config
            return reference_config
        except Exception as e:
            logging.error(
                f"Error generating binary mixture reference link: {e}")
            return {
                'DATA': {},
                'EQUATIONS': {},
            }

    def check_component_availability(
        self,
        component_name: str,
        component_formula: str,
        component_state: str,
        databook_name: str,
        table_name: Optional[str] = None,
        component_key: Literal[
            'Name-State', 'Formula-State'
        ] = 'Formula-State',
        ignore_component_state: Optional[bool] = False,
        **kwargs
    ) -> Dict[str, Dict[str, Union[bool, str]]]:
        """
        Check if a component is available in the specified databook.

        Parameters
        ----------
        component_name : str
            The name of the component.
        component_formula : str
            The formula of the component.
        component_state : str
            The state of the component.
        databook_name : str
            The name of the databook.
        table_name : Optional[str], optional
            The name of the table to check, by default None (checks all tables).
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for the components, by default 'Formula-State'.
        ignore_component_state : Optional[bool], optional
            Whether to ignore the component state in the check, by default False.
        **kwargs
            Additional keyword arguments.
            - ignore_state_props: List[str], optional
                A list of state properties to ignore in the check.

        Returns
        -------
        Dict[str, Dict[str, Union[bool, str]]]
            A dictionary indicating whether the component is available in the databook.

        Notes
        -----
        - The search is `case-insensitive` and ignores leading/trailing whitespace.
        - If `ignore_component_state` is True, the state of the component will be ignored in the check for all properties.
        - If `table_name` is provided, only that table will be checked; otherwise, all tables in the databook will be checked.
        - `ignore_state_props` can be used to specify state properties to ignore during the check. As a result, if the component state matches any of the properties in this list, the state will be ignored in the comparison. Then, ignore_component_state will be set to True.
        """
        try:
            # SECTION: kwargs
            # get ignore_state_props from kwargs
            ignore_state_props = kwargs.get('ignore_state_props', [])
            if not isinstance(ignore_state_props, list):
                ignore_state_props = []

            # NOTE: init
            res = {}

            # NOTE: standardize component inputs
            component_name_ = component_name.strip()
            component_formula = component_formula.strip()
            component_state = component_state.strip()

            # SECTION: get tables
            tables = self.get_databook_tables(databook_name)

            # check if tables are valid
            if tables is None:
                logging.error(f"No tables found for databook: {databook_name}")
                return {"results": {'available': False, 'message': 'No tables found.'}}

            # NOTE: check if table_name is provided
            if table_name is not None:
                # strip table name
                table_name = table_name.strip()

                # check if table_name exists in tables
                if table_name in tables.keys():
                    # update tables to only include the specified table
                    tables = {table_name: tables[table_name]}
                else:
                    logging.error(
                        f"Table '{table_name}' not found in databook '{databook_name}'.")
                    return {"results": {'available': False, 'message': f"Table '{table_name}' not found."}}

            # SECTION: iterate through each table
            for table_name, table in tables.items():
                # NOTE: iterate through each property mapping
                if ignore_state_props and len(ignore_state_props) > 0:

                    # NOTE: get property mapping
                    property_mappings = self.get_property_mappings(
                        databook_name,
                        table_name
                    )

                    # >> normalized property mappings
                    property_mappings_lower = [
                        prop.strip().lower() for prop in property_mappings
                    ]

                    for prop in ignore_state_props:
                        # set ignore state
                        ignore_component_state = ignore_state_in_prop(
                            prop_name=prop,
                            ignore_state_props=property_mappings_lower
                        )

                        # >> check
                        if ignore_component_state is True:
                            break

                # NOTE: get table components
                # ! all components in the table
                components = self.get_table_components(
                    databook_name,
                    table_name
                )

                if components is None:
                    logging.error(
                        f"Components not found for table '{table_name}' in databook '{databook_name}'.")
                    continue

                # ! component records
                component_records = components.get(
                    component_name_,
                    None
                )

                if component_records is None:
                    logging.warning(
                        f"Component '{component_name_}' not found in table '{table_name}'.")
                    continue

                # check if component_records is a dictionary
                if not isinstance(component_records, dict):
                    logging.error(
                        f"Component records for '{component_name_}' in table '{table_name}' are not a dictionary.")
                    continue

                # NOTE: set name, formula and state from component records - case-insensitive
                name = component_records.get('Name', None)
                formula = component_records.get('Formula', None)
                state = component_records.get('State', None)

                # NOTE: check if component records are valid
                if component_key == 'Name-State' and (name is None or state is None):
                    logging.warning(
                        f"Component records for '{component_name_}' in table '{table_name}' are missing 'Name' or 'State.")
                    continue

                if component_key == 'Formula-State' and (formula is None or state is None):
                    logging.warning(
                        f"Component records for '{component_name_}' in table '{table_name}' are missing 'Formula' or 'State'.")
                    continue

                # SECTION: standardize component records
                component_name = component_name.lower()
                component_formula = component_formula.lower()
                component_state = component_state.lower()

                # SECTION: ignore component state if specified
                if ignore_component_state:
                    # NOTE: if ignoring state, only check name or formula
                    if component_key == 'Name-State' and name is not None:
                        if name.lower().strip() == component_name:
                            # add
                            res[table_name] = {
                                'available': True,
                                'ignore_component_state': ignore_component_state,
                                'component_key': 'Name'

                            }
                        else:
                            # add
                            res[table_name] = {
                                'available': False,
                                'ignore_component_state': ignore_component_state,
                                'component_key': 'Name'
                            }

                        # go to next table
                        continue
                    elif component_key == 'Formula-State' and formula is not None:
                        if formula.lower().strip() == component_formula:
                            # add
                            res[table_name] = {
                                'available': True,
                                'ignore_component_state': ignore_component_state,
                                'component_key': 'Formula'
                            }
                        else:
                            # add
                            res[table_name] = {
                                'available': False,
                                'ignore_component_state': ignore_component_state,
                                'component_key': 'Formula'
                            }

                        # go to next table
                        continue
                    else:
                        logging.error(
                            f"Invalid component_key: {component_key}. Must be 'Name-State' or 'Formula-State'.")
                        continue

                # SECTION: check if component matches the formula and state
                if component_key == 'Name-State' and (name is not None and state is not None):
                    # NOTE: check
                    # ! normal comparison
                    if (
                        name.lower().strip() == component_name and
                        state.lower().strip() == component_state
                    ):
                        # add
                        res[table_name] = {
                            'available': True,
                            'ignore_component_state': ignore_component_state,
                            'component_key': component_key
                        }
                    else:
                        # add
                        res[table_name] = {
                            'available': False,
                            'ignore_component_state': ignore_component_state,
                            'component_key': component_key
                        }
                elif component_key == 'Formula-State' and (formula is not None and state is not None):
                    # NOTE: check
                    # ! normal comparison
                    if (
                        formula.lower().strip() == component_formula and
                        state.lower().strip() == component_state
                    ):
                        # add
                        res[table_name] = {
                            'available': True,
                            'ignore_component_state': ignore_component_state,
                            'component_key': component_key
                        }
                    else:
                        # add
                        res[table_name] = {
                            'available': False,
                            'ignore_component_state': ignore_component_state,
                            'component_key': component_key
                        }
                else:
                    logging.error(
                        f"Invalid component_key: {component_key}. Must be 'Name-State' or 'Formula-State'.")
                    continue

                # NOTE: reset loop vars
                # ! ignore_component_state for next table
                if len(ignore_state_props) > 0:
                    ignore_component_state = False

            # res
            return res

        except Exception as e:
            logging.error(f"Error checking component availability: {e}")
            return {"results": {'available': False, 'message': str(e)}}

    def check_binary_mixture_availability(
        self,
        components: List[Component],
        databook_name: str,
        table_name: Optional[str] = None,
        column_name: str = 'Mixture',
        component_key: Literal[
            'Name-State', 'Formula-State'
        ] = 'Formula-State',
        mixture_key: Literal[
            'Name', 'Formula'
        ] = 'Name',
        delimiter: str = '|',
        ignore_component_state: Optional[bool] = False,
        **kwargs
    ) -> Dict[str, Dict[str, Union[bool, str, int]]]:
        """
        Check if a binary mixture of components is available in the specified databook. The mixture is only found in a matrix table.

        Parameters
        ----------
        components : List[Component]
            A list of components in the mixture.
        databook_name : str
            The name of the databook.
        table_name : Optional[str], optional
            The name of the table to check, by default None (checks all tables).
        column_name : str, optional
            The name of the column containing the mixture information, by default 'Mixture'.
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for the components, by default 'Formula-State'.
        mixture_key : Literal['Name', 'Formula'], optional
            The key to use for the mixture, by default 'Formula'.
        delimiter : str, optional
            The delimiter used to separate components in the mixture string, by default '|'.
        ignore_component_state : Optional[bool], optional
            Whether to ignore the component state in the check, by default False.
        **kwargs
            Additional keyword arguments.
            - ignore_state_props: List[str], optional
                A list of state properties to ignore in the check.

        Returns
        -------
        Dict[str, Dict[str, Union[bool, str, int]]]
            A dictionary indicating whether the mixture is available in the databook as:
            - 'available': bool
            - 'ignore_component_state': bool
            - 'component_key': str
            - 'mixture_key': str
            - 'available_count': int
            - If the mixture is not found in any table, returns:

                {'results': {'available': False, 'message': 'Mixture not found in any table.'}}

        Notes
        -----
        - The search is `case-insensitive` and ignores leading/trailing whitespace.
        - If `ignore_component_state` is True, the state of the components will be ignored in the check.
        - If `table_name` is provided, only that table will be checked; otherwise, all tables in the databook will be checked.
        - The matrix table has a column named "Mixture" which contains the mixture information.
        - The mixture is defined as `Component1|Component2` for Name key and `Formula1|Formula2` for Formula key.

        The matrix table should look like this:

        COLUMNS:
        - [No.,Mixture,Name,Formula,State,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]

        VALUES:
        - [1,methanol|ethanol,methanol,CH3OH,l,0,0.300492719,0,1.564200272,0,35.05450323,0,4.481683583]
        - [2,methanol|ethanol,ethanol,C2H5OH,l,0.380229054,0,-20.63243601,0,0.059982839,0,4.481683583,0]

        Every mixture has two rows, one for each component in the mixture.
        """
        try:
            # SECTION: kwargs
            # get ignore_state_props from kwargs
            ignore_state_props = kwargs.get('ignore_state_props', [])
            if not isinstance(ignore_state_props, list):
                ignore_state_props = []

            # SECTION: check inputs
            if not isinstance(components, list) or len(components) != 2:
                logging.error(
                    "component_list must be a list of two Component objects.")
                return {"results": {'available': False, 'message': 'Invalid component_list.'}}

            # NOTE: component identifiers for mixture id creation
            component_1 = components[0]
            component_2 = components[1]

            # SECTION: construct mixture string
            binary_mixture_id = create_binary_mixture_id(
                component_1=component_1,
                component_2=component_2,
                mixture_key=mixture_key
            )

            if not binary_mixture_id:
                logging.error("Failed to create binary mixture ID.")
                return {"results": {'available': False, 'message': 'Failed to create binary mixture ID.'}}

            # >> standardize binary mixture id
            binary_mixture_id = binary_mixture_id.lower().strip()

            # SECTION: get tables
            tables = self.get_databook_tables(databook_name)

            # check if tables are valid
            if tables is None:
                logging.error(f"No tables found for databook: {databook_name}")
                return {"results": {'available': False, 'message': 'No tables found.'}}

            # NOTE: check if table_name is provided
            if table_name is not None:
                # strip table name
                table_name = table_name.strip()

                # check if table_name exists in tables
                if table_name in tables.keys():
                    # update tables to only include the specified table
                    tables = {table_name: tables[table_name]}
                else:
                    logging.error(
                        f"Table '{table_name}' not found in databook '{databook_name}'.")
                    return {"results": {'available': False, 'message': f"Table '{table_name}' not found."}}

            # NOTE: init
            res = {}

            # SECTION: iterate through each table
            for table_name, table in tables.items():
                # NOTE: iterate through each property mapping
                if ignore_state_props and len(ignore_state_props) > 0:

                    # NOTE: get property mapping
                    property_mappings = self.get_property_mappings(
                        databook_name=databook_name,
                        table_name=table_name
                    )

                    # >> normalized property mappings
                    property_mappings_lower = [
                        prop.strip().lower() for prop in property_mappings
                    ]

                    for prop in ignore_state_props:
                        # set ignore state
                        ignore_component_state = ignore_state_in_prop(
                            prop_name=prop,
                            ignore_state_props=property_mappings_lower
                        )

                        # ! >> check
                        if ignore_component_state is True:
                            break

                # NOTE: table type
                table_type = self.get_table_type(
                    databook_name=databook_name,
                    table_name=table_name
                )
                # check
                if table_type is None:
                    logging.error(f"Table type for '{table_name}' not found.")
                    continue

                # >> only proceed if table is a matrix data table
                if table_type != 'DATA' or not self.is_matrix_table(databook_name, table_name):
                    logging.info(
                        f"Skipping table '{table_name}' as it is not a matrix data table.")
                    continue

                # NOTE: get table structure
                structure = table.get('STRUCTURE', None)
                if not isinstance(structure, dict):
                    logging.error(
                        f"Structure for table '{table_name}' is not a dictionary.")
                    continue

                if structure is None:
                    logging.error(
                        f"Structure for table '{table_name}' not found.")
                    continue

                # get columns
                columns = structure.get('COLUMNS', [])
                if not isinstance(columns, list):
                    logging.error(
                        f"Columns for table '{table_name}' are not a list.")
                    continue

                # check if "Mixture" column exists
                if column_name not in columns:
                    logging.warning(
                        f"'{column_name}' column not found in table '{table_name}'.")
                    continue

                # NOTE: get table data
                table_data = self.get_table_data(
                    databook_name=databook_name,
                    table_name=table_name
                )

                if table_data is None or not isinstance(table_data, list):
                    logging.error(
                        f"Table data for '{table_name}' in databook '{databook_name}' is invalid.")
                    continue

                # NOTE: normalize mixture id function
                def normalize_mixture_id(
                    mixture: str,
                    delimiter: str
                ) -> str:
                    parts = mixture.lower().strip().split(delimiter)
                    return delimiter.join(sorted(parts))

                # SECTION: search for the mixture in the table data
                # NOTE: build dataframe for easier searching
                df = pd.DataFrame(
                    data=table_data,
                    columns=columns
                )

                # NOTE: normalized dataframe
                # normalized column
                normalized_column_name = f'Normalized_{column_name}'

                # ! create normalized column
                df[normalized_column_name] = df[column_name].apply(
                    lambda x: normalize_mixture_id(str(x).strip(), delimiter)
                )

                # SECTION: filter dataframe for the mixture
                # ! normalized binary mixture id
                normalized_binary_mixture_id = normalize_mixture_id(
                    mixture=binary_mixture_id,
                    delimiter=delimiter
                )

                # ! mask
                mask_ = df[normalized_column_name].str.strip(
                ) == normalized_binary_mixture_id
                # found rows
                mixture_df = df[mask_]

                # count row
                available_count = 0
                # check availability
                if mixture_df.empty:
                    all_available = False
                else:
                    # SECTION: check component name/formula and state in each row
                    mask_component_1 = None
                    mask_component_2 = None

                    # NOTE: create masks for each component based on component_key and ignore_component_state
                    if component_key == 'Name-State' and ignore_component_state is False:
                        mask_component_1 = (
                            (
                                mixture_df['Name'].str.lower().str.strip(
                                ) == component_1.name.lower().strip()
                            ) &
                            (
                                mixture_df['State'].str.lower().str.strip(
                                ) == component_1.state.lower().strip()
                            )
                        )
                        mask_component_2 = (
                            (
                                mixture_df['Name'].str.lower().str.strip(
                                ) == component_2.name.lower().strip()
                            ) &
                            (
                                mixture_df['State'].str.lower().str.strip()
                                == component_2.state.lower().strip()
                            )
                        )
                    elif component_key == 'Formula-State' and ignore_component_state is False:
                        mask_component_1 = (
                            (
                                mixture_df['Formula'].str.lower().str.strip(
                                ) == component_1.formula.lower().strip()
                            ) &
                            (
                                mixture_df['State'].str.lower().str.strip()
                                == component_1.state.lower().strip()
                            )
                        )
                        mask_component_2 = (
                            (
                                mixture_df['Formula'].str.lower().str.strip(
                                ) == component_2.formula.lower().strip()
                            ) &
                            (
                                mixture_df['State'].str.lower().str.strip()
                                == component_2.state.lower().strip()
                            )
                        )
                    elif ignore_component_state:
                        # NOTE: set Name for chosen Name-State
                        component_key_ = 'Name' if component_key == 'Name-State' else 'Formula'

                        # NOTE: compare
                        # >> component set id
                        component_1_id = component_1.name if component_key_ == 'Name' else component_1.formula
                        component_2_id = component_2.name if component_key_ == 'Name' else component_2.formula

                        # masks
                        mask_component_1 = (
                            mixture_df[component_key_].str.lower().str.strip()
                            == component_1_id.lower().strip()
                        )
                        mask_component_2 = (
                            mixture_df[component_key_].str.lower().str.strip()
                            == component_2_id.lower().strip()
                        )
                    else:
                        raise ValueError(
                            "Invalid component_key or ignore_component_state configuration.")

                    # NOTE: check
                    if mask_component_1 is None or mask_component_2 is None:
                        raise ValueError(
                            "Component masks could not be determined.")
                    # check if both components are found
                    if not mixture_df[mask_component_1].empty and not mixture_df[mask_component_2].empty:
                        all_available = True
                        # count available rows containing the mixture
                        available_count = len(mixture_df)
                    else:
                        all_available = False

                # add result for the current table
                res[table_name] = {
                    'available': all_available,
                    'ignore_component_state': ignore_component_state,
                    'component_key': component_key,
                    'mixture_key': mixture_key,
                    'available_count': available_count,
                }

                # NOTE: reset loop vars
                # dataframe
                df = pd.DataFrame()

            # res
            return res

        except Exception as e:
            logging.error(f"Error checking mixture availability: {e}")
            return {"results": {'available': False, 'message': str(e)}}

    def get_component_reference_config(
        self,
        component_name: str,
        component_formula: str,
        component_state: str,
        databook_name: str,
        table_name: Optional[str] = None,
        add_label: Optional[bool] = False,
        check_labels: Optional[bool] = False,
        component_key: Literal[
            'Name-State', 'Formula-State'
        ] = 'Formula-State',
        ignore_component_state: Optional[bool] = False,
        ignore_state_props: Optional[List[str]] = None
    ) -> Optional[Dict[str, ComponentConfig]]:
        """
        Get the reference including the databook name and table name for a component.

        Parameters
        ----------
        component_name : str
            The name of the component.
        component_formula : str
            The formula of the component.
        component_state : str
            The state of the component.
        databook_name : str
            The name of the databook.
        table_name : Optional[str], optional
            The name of the table to check, by default None (checks all tables).
        add_label : Optional[bool], optional
            Whether to include the label in the reference, by default False.
        check_labels : Optional[bool], optional
            Whether to check if the labels are valid, by default False.
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for the components, by default 'Formula-State'.
        ignore_component_state : Optional[bool], optional
            Whether to ignore the component state in the check, by default False.
        ignore_state_props : Optional[List[str]], optional
            A list of properties for which the component state should be ignored during the check, by default None.

        Returns
        -------
        Optional[Dict[str, ComponentConfig]]
            A dictionary containing the reference config if the component exists, otherwise None.
        """
        try:
            # SECTION: check inputs
            # NOTE: component name, formula, and state must be provided
            if not component_name or not component_formula or not component_state:
                logging.error(
                    "Component name, formula, and state must be provided.")
                return None

            # NOTE: ignore state props
            if ignore_state_props and isinstance(ignore_state_props, list):
                # check list
                if len(ignore_state_props) == 0:
                    logger.warning("ignore_state_props is an empty list.")
                    ignore_state_props = None

            # SECTION: check component availability
            availability = self.check_component_availability(
                component_name=component_name,
                component_formula=component_formula,
                component_state=component_state,
                databook_name=databook_name,
                table_name=table_name,
                component_key=component_key,
                ignore_component_state=ignore_component_state,
                ignore_state_props=ignore_state_props
            )

            # SECTION: symbol settings
            # init symbols
            symbols = None
            if check_labels:
                # init symbol controller
                symbol_controller = SymbolController()
                # set
                symbols = symbol_controller.symbols
                # check if symbols is valid
                if symbols is None:
                    logging.error("Symbols not found.")
                    return None

            # NOTE: init result
            res: Dict[str, ComponentConfig] = {}

            # SECTION: iterate through each table in availability
            for table_name, availability_val in availability.items():
                # NOTE: extract availability
                is_available = availability_val.get('available', False)

                # only proceed if available
                if is_available:
                    # reset res_availability
                    res_availability = {}

                    # ! table type
                    table_type = self.get_table_type(
                        databook_name=databook_name,
                        table_name=table_name
                    )

                    if table_type is None:
                        logging.error(
                            f"Table type for '{table_name}' not found.")
                        continue

                    # >> check if table is matrix
                    is_matrix = self.is_matrix_table(
                        databook_name,
                        table_name
                    )

                    # ! get symbols
                    if table_type == 'DATA' and is_matrix is False:

                        # get symbols
                        symbols = self.get_table_data_details(
                            databook_name,
                            table_name
                        )
                        # ! check symbols
                        if check_labels and symbols is not None:
                            # convert to list if not already
                            symbols_: List[str] = list(symbols.values())
                            symbol_controller_ = symbol_controller.check_symbols(
                                symbols_)

                            # >> check if any symbol is invalid
                            if symbol_controller_ is False:
                                logging.error(
                                    f"Invalid symbols found in table '{table_name}'.")
                                continue

                        # set
                        res_availability = {
                            'databook': databook_name,
                            'table': table_name,
                            'mode': table_type,
                            'labels': symbols if add_label else []
                        }

                    elif table_type == 'DATA' and is_matrix is True:
                        # get symbols
                        symbols = self.get_matrix_table_symbols(
                            databook_name,
                            table_name
                        )

                        # ! check symbols
                        if check_labels and symbols is not None:
                            # convert to list if not already
                            symbols_: List[str] = list(symbols.values())
                            symbol_controller_ = symbol_controller.check_symbols(
                                symbols_
                            )

                            # >> check if any symbol is invalid
                            if symbol_controller_ is False:
                                logging.error(
                                    f"Invalid symbols found in table '{table_name}'.")
                                continue

                        # set
                        res_availability = {
                            'databook': databook_name,
                            'table': table_name,
                            'mode': table_type,
                            'labels': symbols if add_label else []
                        }

                    elif table_type == 'EQUATIONS':
                        symbol = self.get_table_equation_details(
                            databook_name,
                            table_name
                        )

                        # ! check symbol
                        if check_labels and symbol is not None:
                            symbol_controller_ = symbol_controller.check_symbols(
                                [symbol]
                            )

                            # >> check if any symbol is invalid
                            if symbol_controller_ is False:
                                logging.error(
                                    f"Invalid symbol '{symbol}' found in table '{table_name}'.")
                                continue

                        # set
                        res_availability = {
                            'databook': databook_name,
                            'table': table_name,
                            'mode': table_type,
                            'label': symbol if add_label else None
                        }
                    else:
                        logging.error(
                            f"Invalid table type '{table_type}' for table '{table_name}'.")
                        continue

                    # convert to ComponentConfig
                    res_availability = ComponentConfig(**res_availability)
                    # >> add to result
                    res[table_name] = res_availability

            # check if res is empty
            if not res:
                logging.warning(
                    f"Component '{component_name}' with formula '{component_formula}' and state '{component_state}' not found in databook '{databook_name}'.")
                return None

            # return the result
            return res
        except Exception as e:
            logging.error(f"Error getting component reference: {e}")
            return None

    def get_component_reference_configs(
        self,
        component_name: str,
        component_formula: str,
        component_state: str,
        add_label: Optional[bool] = False,
        check_labels: Optional[bool] = False,
        component_key: Literal[
            'Name-State', 'Formula-State'
        ] = 'Formula-State',
        ignore_component_state: Optional[bool] = False,
        ignore_state_props: Optional[List[str]] = None
    ) -> Optional[Dict[str, ComponentConfig]]:
        """
        Get the reference including the databook name and table name for a component
        across all databooks.

        Parameters
        ----------
        component_name : str
            The name of the component.
        component_formula : str
            The formula of the component.
        component_state : str
            The state of the component.
        add_label : Optional[bool], optional
            Whether to include the label in the reference, by default False.
        check_labels : Optional[bool], optional
            Whether to check if the labels are valid, by default False.
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for the components, by default 'Formula-State'.
        ignore_component_state : Optional[bool], optional
            Whether to ignore the component state in the check, by default False.
        ignore_state_props : Optional[List[str]], optional
            A list of properties for which the component state should be ignored during the check, by default None.

        Returns
        -------
        Optional[Dict[str, ComponentConfig]]
            A dictionary containing the reference config if the component exists, otherwise None.

        Notes
        -----
        - The search is `case-insensitive` and ignores leading/trailing whitespace.
        - If `ignore_component_state` is True, the state of the component will be ignored in the check.
        - ignore_state_props can be used to specify state properties to ignore during the check. As a result, if the component state matches any of the properties in this list, the state will be ignored in the comparison. Then, ignore_component_state will be set to True.
        - The result dictionary keys are in the format "DatabookName::TableName".
        """
        try:
            # SECTION: check inputs
            # component name, formula, and state must be provided
            if not component_name or not component_formula or not component_state:
                logging.error(
                    "Component name, formula, and state must be provided.")
                return None

            # ignore_state_props must be a list if provided
            if ignore_state_props is not None and not isinstance(ignore_state_props, list):
                logging.error("ignore_state_props must be a list.")
                ignore_state_props = None

            # SECTION: init result
            res: Dict[str, ComponentConfig] = {}

            # NOTE: databook names
            databook_names = self.get_databook_names()
            # check
            if not databook_names:
                logging.error("No databooks found.")
                return None

            # SECTION: iterate through each databook
            for databook_name in databook_names:
                # get component reference config for each databook
                res_databook: Optional[Dict[str, ComponentConfig]] = self.get_component_reference_config(
                    component_name=component_name,
                    component_formula=component_formula,
                    component_state=component_state,
                    databook_name=databook_name,
                    add_label=add_label,
                    check_labels=check_labels,
                    component_key=component_key,
                    ignore_component_state=ignore_component_state,
                    ignore_state_props=ignore_state_props
                )

                if res_databook is not None:
                    # iterate through each table in res_databook
                    for table_name, table_info in res_databook.items():
                        # create a unique key for each table in the result
                        databook_table_key = f"{databook_name}::{table_name}"
                        # add to result with unique key
                        res[databook_table_key] = table_info

            # check if res is empty
            if not res:
                logging.warning(
                    f"Component '{component_name}' with formula '{component_formula}' and state '{component_state}' not found in any databook.")
                return None

            # return the result
            return res
        except Exception as e:
            logging.error(f"Error getting component references: {e}")
            return None

    def get_binary_mixture_reference_config(
        self,
        components: List[Component],
        databook_name: str,
        table_name: Optional[str] = None,
        add_label: Optional[bool] = False,
        check_labels: Optional[bool] = False,
        component_key: Literal[
            'Name-State', 'Formula-State'
        ] = 'Formula-State',
        mixture_key: Literal[
            'Name', 'Formula'
        ] = 'Name',
        delimiter: str = '|',
        column_name: str = 'Mixture',
        ignore_component_state: Optional[bool] = False,
        ignore_state_props: Optional[List[str]] = None,
    ):
        '''
        Get the reference including the databook name and table name for a binary mixture of components.

        Parameters
        ----------
        components : List[Component]
            A list of two components in the mixture.
        databook_name : str
            The name of the databook.
        table_name : Optional[str], optional
            The name of the table to check, by default None (checks all tables).
        add_label : Optional[bool], optional
            Whether to include the label in the reference, by default False.
        check_labels : Optional[bool], optional
            Whether to check if the labels are valid, by default False.
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for the components, by default 'Formula-State'.
        mixture_key : Literal['Name', 'Formula'], optional
            The key to use for the mixture, by default 'Name'.
        delimiter : str, optional
            The delimiter used to separate components in the mixture string, by default '|'.
        column_name : str, optional
            The name of the column containing the mixture information, by default 'Mixture'.
        ignore_component_state : Optional[bool], optional
            Whether to ignore the component state in the check, by default False.
        ignore_state_props : Optional[List[str]], optional
            A list of properties for which the component state should be ignored during the check, by default
            None.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the reference config if the mixture exists, otherwise None.
            The dictionary has the following structure:
            {
                'databook': str,
                'table': str,
                'mode': 'DATA' or 'EQUATIONS',
                'labels': Dict[str, str] (if mode is 'DATA'),
                'label': str (if mode is 'EQUATIONS')
            }

        Notes
        -----
        - The search is `case-insensitive` and ignores leading/trailing whitespace.
        - If `ignore_component_state` is True, the state of the components will be ignored in the check (`mixture availability`).
        - If `table_name` is provided, only that table will be checked; otherwise, all tables in the databook will be checked.
        - The matrix table has a column named "Mixture" which contains the mixture information.
        - The mixture is defined as `Component1|Component2` for Name key and `Formula1|Formula2` for Formula key.
        - The result dictionary keys are in the format "DatabookName::TableName".
        - The mixture is only found in a matrix table.
        - The matrix table should look like this:

        COLUMNS:
        - [No.,Mixture,Name,Formula,State,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
        VALUES:
        - [1,methanol|ethanol,methanol,CH3OH,l,0,0.300492719,0,1.564200272,0,35.05450323,0,4.481683583]
        - [2,methanol|ethanol,ethanol,C2H5OH,l,0.380229054,0,-20.63243601,0,0.059982839,0,4.481683583,0]

        Every mixture has two rows, one for each component in the mixture.

        '''
        try:
            # SECTION: check inputs
            if not isinstance(components, list) or len(components) != 2:
                logging.error(
                    "components must be a list of two Component objects.")
                return None

            # ignore_state_props must be a list if provided
            if ignore_state_props is not None and not isinstance(ignore_state_props, list):
                logging.error("ignore_state_props must be a list.")
                ignore_state_props = None

            # SECTION: check mixture availability
            availability = self.check_binary_mixture_availability(
                components=components,
                databook_name=databook_name,
                table_name=table_name,
                column_name=column_name,
                component_key=component_key,
                mixture_key=mixture_key,
                delimiter=delimiter,
                ignore_component_state=ignore_component_state,
                ignore_state_props=ignore_state_props
            )

            # SECTION: symbol settings
            # init symbols
            symbols = None
            if check_labels:
                # init symbol controller
                symbol_controller = SymbolController()
                # set
                symbols = symbol_controller.symbols
                # check if symbols is valid
                if symbols is None:
                    logging.error("Symbols not found.")
                    return None

            # NOTE: init result
            res: Dict[str, ComponentConfig] = {}

            # SECTION: iterate through each table in availability
            for table_name, availability_val in availability.items():
                # NOTE: extract availability
                is_available = availability_val.get('available', False)

                # only proceed if available
                if is_available:
                    # reset res_availability
                    res_availability = {}

                    # ! table type
                    table_type = self.get_table_type(
                        databook_name=databook_name,
                        table_name=table_name
                    )

                    if table_type is None:
                        logging.error(
                            f"Table type for '{table_name}' not found.")
                        continue

                    # >> check if table is matrix
                    is_matrix = self.is_matrix_table(
                        databook_name=databook_name,
                        table_name=table_name
                    )

                    if table_type == 'DATA' and is_matrix is True:
                        # get symbols
                        symbols = self.get_matrix_table_symbols(
                            databook_name=databook_name,
                            table_name=table_name
                        )

                        # ! check symbols
                        if check_labels and symbols is not None:
                            # convert to list if not already
                            symbols_: List[str] = list(symbols.values())
                            check_symbol_ = symbol_controller.check_symbols(
                                symbols_
                            )

                            # >> if any symbol is invalid, skip this table
                            if not check_symbol_:
                                logging.error(
                                    f"One or more symbols in table '{table_name}' are invalid.")
                                continue

                        # set
                        res_availability = {
                            'databook': databook_name,
                            'table': table_name,
                            'mode': table_type,
                            'labels': symbols if add_label else []
                        }

                    else:
                        logging.error(
                            f"Table '{table_name}' is not a matrix DATA table.")
                        continue

                    # convert to ComponentConfig
                    res_availability = ComponentConfig(**res_availability)
                    # >> add to result
                    res[table_name] = res_availability

            # check if res is empty
            if not res:
                logging.warning(
                    f"Mixture of components not found in databook '{databook_name}'.")
                return None

            # return the result
            return res
        except Exception as e:
            logging.error(f"Error getting binary mixture reference: {e}")
            return None

    def get_binary_mixture_reference_configs(
        self,
        components: List[Component],
        add_label: Optional[bool] = False,
        check_labels: Optional[bool] = False,
        component_key: Literal[
            'Name-State', 'Formula-State'
        ] = 'Formula-State',
        mixture_key: Literal[
            'Name', 'Formula'
        ] = 'Name',
        delimiter: str = '|',
        column_name: str = 'Mixture',
        ignore_component_state: Optional[bool] = False,
        ignore_state_props: Optional[List[str]] = None,
    ) -> Optional[Dict[str, ComponentConfig]]:
        '''
        Get the reference including the databook name and table name for a binary mixture of components
        across all databooks.

        Parameters
        ----------
        components : List[Component]
            A list of two components in the mixture.
        add_label : Optional[bool], optional
            Whether to include the label in the reference, by default False.
        check_labels : Optional[bool], optional
            Whether to check if the labels are valid, by default False.
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for the components, by default 'Formula-State'.
        mixture_key : Literal['Name', 'Formula'], optional
            The key to use for the mixture, by default 'Name'.
        delimiter : str, optional
            The delimiter used to separate components in the mixture string, by default '|'.
        column_name : str, optional
            The name of the column containing the mixture information, by default 'Mixture'.
        ignore_component_state : Optional[bool], optional
            Whether to ignore the component state in the check, by default False.
        ignore_state_props : Optional[List[str]], optional
            A list of properties for which the component state should be ignored during the check, by default
            None.

        Returns
        -------
        Optional[Dict[str, ComponentConfig]]
            A dictionary containing the reference config if the mixture exists, otherwise None.
            The dictionary has the following structure:
            {
                'databook': str,
                'table': str,
                'mode': 'DATA' or 'EQUATIONS',
                'labels': Dict[str, str] (if mode is 'DATA'),
                'label': str (if mode is 'EQUATIONS')
            }

        Notes
        -----
        - The search is `case-insensitive` and ignores leading/trailing whitespace.
        - If `ignore_component_state` is True, the state of the components will be ignored in the check (`mixture availability`).
        - The result dictionary keys are in the format "DatabookName::TableName".
        - The mixture is only found in a matrix table.
        - The matrix table should look like this:

        COLUMNS:
        - [No.,Mixture,Name,Formula,State,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]

        VALUES:
        - [1,methanol|ethanol,methanol,CH3OH,l,0,0.300492719,0,1.564200272,0,35.05450323,0,4.481683583]
        - [2,methanol|ethanol,ethanol,C2H5OH,l,0.380229054,0,-20.63243601,0,0.059982839,0,4.481683583,0]

        Every mixture has two rows, one for each component in the mixture.

        '''
        try:
            # SECTION: check inputs
            if not isinstance(components, list) or len(components) != 2:
                logging.error(
                    "components must be a list of two Component objects.")
                return None

            # ignore_state_props must be a list if provided
            if ignore_state_props is not None and not isinstance(ignore_state_props, list):
                logging.error("ignore_state_props must be a list.")
                ignore_state_props = None

            # SECTION: init result
            res: Dict[str, ComponentConfig] = {}

            # NOTE: databook names
            databook_names = self.get_databook_names()
            # check
            if not databook_names:
                logging.error("No databooks found.")
                return None

            # SECTION: iterate through each databook
            for databook_name in databook_names:
                # get binary mixture reference config for each databook
                res_databook: Optional[Dict[str, ComponentConfig]] = self.get_binary_mixture_reference_config(
                    components=components,
                    databook_name=databook_name,
                    table_name=None,
                    add_label=add_label,
                    check_labels=check_labels,
                    component_key=component_key,
                    mixture_key=mixture_key,
                    delimiter=delimiter,
                    column_name=column_name,
                    ignore_component_state=ignore_component_state,
                    ignore_state_props=ignore_state_props
                )

                if res_databook is not None:
                    # iterate through each table in res_databook
                    for table_name, table_info in res_databook.items():
                        # create a unique key for each table in the result
                        databook_table_key = f"{databook_name}::{table_name}"
                        # add to result with unique key
                        res[databook_table_key] = table_info

            # check if res is empty
            if not res:
                logging.warning(
                    f"Mixture of components not found in any databook.")
                return None

            # return the result
            return res
        except Exception as e:
            logging.error(f"Error getting binary mixture references: {e}")
            return None

    def generate_reference_rules(
        self,
        reference_configs: Dict[str, Any]
    ) -> Dict[str, Dict[str, str]]:
        """
        generate the reference rules for a component based on the provided reference configurations. It consists of two main parts: DATA and EQUATIONS. Each part contains thermodynamic properties and their corresponding symbols (labels).

        Parameters
        ----------
        reference_configs : Dict[str, Any]
            A dictionary containing the reference configurations for the component.

        Returns
        -------
        Dict[str, Dict[str, str]]
            A dictionary containing the reference rules for the component.

        Notes
        -----
        The reference_configs dictionary should have the following structure:

        ```python
        {
            'reference_key_1': {
                'databook': 'Databook Name',
                'table': 'Table Name',
                'mode': 'DATA' or 'EQUATIONS',
                'labels': {
                    'Property1': 'Symbol1',
                    'Property2': 'Symbol2',
                    ...
                } (for DATA mode)
                'label': 'Symbol' (for EQUATIONS mode)
            },
            ...
        }
        ```

        The `reference_key` can be any unique identifier for the reference configuration. It could be the name of the property such as `General Data`, `Vapor Pressure`, `Enthalpy of Vaporization`, etc.

        Then reference rule is formed as:

        ```python
        {
            'DATA': {
                'Property1': 'Symbol1',
                'Property2': 'Symbol2',
                ...
            },
            'EQUATIONS': {
                'Property3': 'Symbol3',
                ...
            }
        }
        """
        try:
            # SECTION: init result
            reference_rules = {
                'DATA': {},
                'EQUATIONS': {}
            }

            # SECTION: iterate through each reference config
            for ref_key, ref_config in reference_configs.items():
                # check if ref_config is a dictionary
                if not isinstance(ref_config, dict):
                    logging.error(
                        f"Reference config for '{ref_key}' is not a dictionary.")
                    continue

                # get mode
                mode = ref_config.get('mode', None)
                if mode is None:
                    logging.error(
                        f"Mode not found in reference config for '{ref_key}'.")
                    continue

                # check mode
                if mode == 'DATA':
                    # iterate through each label
                    labels = ref_config.get('labels', None)
                    if not isinstance(labels, dict):
                        logging.error(
                            f"Labels not found or invalid in reference config for '{ref_key}'.")
                        continue

                    for prop, label in labels.items():
                        # check if prop and label are valid
                        if prop is None or label is None or label in ['None', '']:
                            logging.error(
                                f"Property or label not found or invalid in reference config for '{ref_key}'.")
                            continue

                        # add to reference rules
                        if prop not in reference_rules['DATA']:
                            reference_rules['DATA'][prop] = label

                elif mode == 'EQUATIONS':
                    # get label
                    label = ref_config.get('label', None)
                    if label is None or label in ['None', '']:
                        logging.error(
                            f"Label not found or invalid in reference config for '{ref_key}'.")
                        continue

                    # table
                    table = ref_config.get('table', None)
                    if table is None:
                        logging.error(
                            f"Table not found in reference config for '{ref_key}'.")
                        continue
                    # get property name from label (assuming the property name is the same as the label)
                    prop = ref_key  # This can be modified based on actual requirements

                    # add to reference rules
                    if prop not in reference_rules['EQUATIONS']:
                        reference_rules['EQUATIONS'][prop] = label
                else:
                    logging.error(
                        f"Invalid mode '{mode}' in reference config for '{ref_key}'.")
                    continue

            # return the reference rules
            return reference_rules
        except Exception as e:
            logging.error(f"Error building reference rules: {e}")
            return {
                'DATA': {},
                'EQUATIONS': {}
            }

    def generate_component_reference_rules(
        self,
        reference_configs: Dict[str, ComponentConfig]
    ) -> Dict[str, ComponentRule]:
        """
        generate the reference rules for a component based on the provided reference configurations. It consists of two main parts: DATA and EQUATIONS. Each part contains thermodynamic properties and their corresponding symbols (labels).

        Parameters
        ----------
        reference_configs : Dict[str, ComponentConfig]
            A dictionary containing the reference configurations for the component.

        Returns
        -------
        Dict[str, ComponentRule]
            A dictionary containing the reference rules for the component.

        Notes
        -----
        The reference_configs dictionary should have the following structure:
        {
            'reference_key_1': {
                'databook': 'Databook Name',
                'table': 'Table Name',
                'mode': 'DATA' or 'EQUATIONS',
                'labels': {
                    'Property1': 'Symbol1',
                    'Property2': 'Symbol2',
                    ...
                } (for DATA mode)
                'label': 'Symbol' (for EQUATIONS mode)
            },
            ...
        }
        """
        try:
            # SECTION: init result
            reference_rules: Dict[str, ComponentRule] = {
                'DATA': {},
                'EQUATIONS': {}
            }

            # SECTION: iterate through each reference config
            for ref_key, ref_config in reference_configs.items():
                # check if ref_config is a dictionary
                if not isinstance(ref_config, dict):
                    logging.error(
                        f"Reference config for '{ref_key}' is not a dictionary.")
                    continue

                # NOTE: get mode
                mode = ref_config.get('mode', None)
                if mode is None:
                    logging.error(
                        f"Mode not found in reference config for '{ref_key}'.")
                    continue

                # check mode
                if mode == 'DATA':
                    # NOTE: iterate through each label
                    labels = ref_config.get('labels', None)
                    if not isinstance(labels, dict):
                        logging.error(
                            f"Labels not found or invalid in reference config for '{ref_key}'.")
                        continue

                    for prop, label in labels.items():
                        # check if prop and label are valid
                        if prop is None or label is None or label in ['None', '']:
                            logging.error(
                                f"Property or label not found or invalid in reference config for '{ref_key}'.")
                            continue

                        # add to reference rules
                        if prop not in reference_rules['DATA']:

                            reference_rules['DATA'][prop] = label

                elif mode == 'EQUATIONS':
                    # NOTE: get label
                    label = ref_config.get('label', None)
                    if label is None or label in ['None', '']:
                        logging.error(
                            f"Label not found or invalid in reference config for '{ref_key}'.")
                        continue

                    # NOTE: table
                    table = ref_config.get('table', None)
                    if table is None:
                        logging.error(
                            f"Table not found in reference config for '{ref_key}'.")
                        continue
                    # get property name from label (assuming the property name is the same as the label)
                    prop = ref_key  # This can be modified based on actual requirements

                    # add to reference rules
                    if prop not in reference_rules['EQUATIONS']:
                        reference_rules['EQUATIONS'][prop] = label
                else:
                    logging.error(
                        f"Invalid mode '{mode}' in reference config for '{ref_key}'.")
                    continue

            # return the reference rules
            return reference_rules
        except Exception as e:
            logging.error(f"Error building reference rules: {e}")
            return {
                'DATA': {},
                'EQUATIONS': {}
            }

    def generate_binary_mixture_reference_rules(
        self,
        reference_configs: Dict[str, ComponentConfig]
    ) -> Dict[str, ComponentRule]:
        """
        generate the reference rules for a binary mixture based on the provided reference configurations. It consists of two main parts: DATA and EQUATIONS. Each part contains thermodynamic properties and their corresponding symbols (labels).

        Parameters
        ----------
        reference_configs : Dict[str, ComponentConfig]
            A dictionary containing the reference configurations for the binary mixture.

        Returns
        -------
        Dict[str, ComponentRule]
            A dictionary containing the reference rules for the binary mixture.

        Notes
        -----
        The reference_configs dictionary should have the following structure:
        {
            'reference_key_1': {
                'databook': 'Databook Name',
                'table': 'Table Name',
                'mode': 'DATA' or 'EQUATIONS',
                'labels': {
                    'Property1': 'Symbol1',
                    'Property2': 'Symbol2',
                    ...
                } (for DATA mode)
                'label': 'Symbol' (for EQUATIONS mode)
            },
            ...
        }
        """
        try:
            # SECTION: init result
            reference_rules: Dict[str, ComponentRule] = {
                'DATA': {},
                'EQUATIONS': {}
            }

            # SECTION: iterate through each reference config
            for ref_key, ref_config in reference_configs.items():
                # check if ref_config is a dictionary
                if not isinstance(ref_config, dict):
                    logging.error(
                        f"Reference config for '{ref_key}' is not a dictionary.")
                    continue

                # NOTE: get mode
                mode = ref_config.get('mode', None)
                if mode is None:
                    logging.error(
                        f"Mode not found in reference config for '{ref_key}'.")
                    continue

                # NOTE: check matrix table
                # ! databook
                databook = ref_config.get('databook', None)
                # >> check
                if databook is None:
                    logging.error(
                        f"Databook not found in reference config for '{ref_key}'.")
                    continue

                # ! table
                table = ref_config.get('table', None)
                # >> check
                if table is None:
                    logging.error(
                        f"Table not found in reference config for '{ref_key}'.")
                    continue

                # ! check if table is matrix
                is_matrix = self.is_matrix_table(
                    databook_name=databook,
                    table_name=table
                )

                if is_matrix is not True:
                    logging.error(
                        f"Table '{table}' in databook '{databook}' is not a matrix table.")
                    continue

                # check mode
                if mode == 'DATA' and is_matrix is True:
                    # NOTE: iterate through each label
                    labels = ref_config.get('labels', None)
                    if not isinstance(labels, dict):
                        logging.error(
                            f"Labels not found or invalid in reference config for '{ref_key}'.")
                        continue

                    for prop, label in labels.items():
                        # check if prop and label are valid
                        if prop is None or label is None or label in ['None', '']:
                            logging.error(
                                f"Property or label not found or invalid in reference config for '{ref_key}'.")
                            continue

                        # add to reference rules
                        if prop not in reference_rules['DATA']:
                            reference_rules['DATA'][prop] = label

                else:
                    logging.error(
                        f"Invalid mode '{mode}' in reference config for '{ref_key}'. Only 'DATA' mode is supported for binary mixtures.")
                    continue

            # return the reference rules
            return reference_rules
        except Exception as e:
            logging.error(f"Error building reference rules: {e}")
            return {
                'DATA': {},
                'EQUATIONS': {}
            }
