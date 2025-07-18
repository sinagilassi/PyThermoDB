# import libs
import logging
from typing import (
    Union,
    Optional,
    Dict,
    List,
    Any,
    Literal
)
# locals
from ..docs import CustomRef
from .builder import TableBuilder


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

    def check_reference_format(self):
        """
        Check the format of the custom reference. Tree Traversal, DFS and BFS
        """
        pass

    def load_reference(
        self
    ) -> Optional[Dict[str, List[str | Dict[str, Any]]]]:
        """
        Load the custom reference.

        Returns
        -------
        Optional[Dict[str, List[str | Dict[str, Any]]]]
            The custom reference if it exists, otherwise None.
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
        except Exception as e:
            logging.error(f"Error loading custom reference: {e}")
            return None

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

    def generate_reference_link(
        self,
        databook_name: str,
    ) -> Dict[str, Any]:
        """
        Generate a reference link for a component.

        Parameters
        ----------
        databook_name : str
            The name of the databook.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the reference link for the component.
        """
        try:
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

            # iterate through each table
            for table_name, table in tables.items():
                # NOTE: table type
                table_type = self.get_table_type(databook_name, table_name)
                if table_type is None:
                    logging.error(f"Table type for '{table_name}' not found.")
                    continue

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
                                    symbol: symbol
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

            # return the reference config
            return reference_config
        except Exception as e:
            logging.error(f"Error generating reference config: {e}")
            return {}

    def check_component_availability(
        self,
        component_name: str,
        component_formula: str,
        component_state: str,
        databook_name: str
    ) -> Dict[str, Union[bool, str]]:
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

        Returns
        -------
        Dict[str, Union[bool, str]]
            A dictionary indicating whether the component is available in the databook.
        """
        try:
            # NOTE: init
            res = {}

            # SECTION: get tables
            tables = self.get_databook_tables(databook_name)

            # check if tables are valid
            if tables is None:
                logging.error(f"No tables found for databook: {databook_name}")
                return {'available': False, 'message': 'No tables found.'}

            # SECTION: iterate through each table
            for table_name, table in tables.items():
                # NOTE: get table components
                components = self.get_table_components(
                    databook_name,
                    table_name
                )

                if components is None:
                    logging.error(
                        f"Components not found for table '{table_name}' in databook '{databook_name}'.")
                    continue

                # component records
                component_records = components.get(
                    component_name,
                    None
                )

                if component_records is None:
                    logging.warning(
                        f"Component '{component_name}' not found in table '{table_name}'.")
                    continue

                # check if component_records is a dictionary
                if not isinstance(component_records, dict):
                    logging.error(
                        f"Component records for '{component_name}' in table '{table_name}' are not a dictionary.")
                    continue

                # set
                formula = component_records.get('Formula', None)
                state = component_records.get('State', None)

                # NOTE: check if component records are valid
                if not formula or not state:
                    logging.error(
                        f"Component records for '{component_name}' in table '{table_name}' are missing 'Formula' or 'State'.")
                    continue

                # check if component matches the formula and state
                if (
                    formula == component_formula and
                    state == component_state
                ):
                    # add
                    res[table_name] = True
                else:
                    # add
                    res[table_name] = False

            # res
            return res

        except Exception as e:
            logging.error(f"Error checking component availability: {e}")
            return {'available': False, 'message': str(e)}

    def get_component_reference_config(
        self,
        component_name: str,
        component_formula: str,
        component_state: str,
        databook_name: str
    ):
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
        """
        try:
            # SECTION: check component availability
            availability = self.check_component_availability(
                component_name,
                component_formula,
                component_state,
                databook_name
            )

            # NOTE: init result
            res = {}

            # iterate through each table in availability
            for table_name, is_available in availability.items():
                if is_available:
                    # add to result
                    res_availability = {
                        'databook': databook_name,
                        'table': table_name,
                    }

                    # add to result
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
