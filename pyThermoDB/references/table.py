# import libs
import logging
from typing import (
    Optional,
    List,
    Dict,
    Any
)
# local
from .builder import TableBuilder


class ThermoTable(TableBuilder):
    """
    Table class serves as a container for table data.
    """
    # NOTE: attributes
    # table name
    _name: str = ""
    # data
    _data: str = ""
    # equation
    _equations: List[str] = []
    # matrix symbol
    _matrix_symbol: List[str] = []
    # table id
    _id: int = 0
    # table type
    _types: str = ""
    # description
    _description: str = ""

    # SECTION: table sections
    # structure
    structure: Dict[str, Any] = {}
    # columns
    columns: Optional[List[str]] = None
    # symbols
    symbols: Optional[List[str]] = None
    # units
    units: Optional[List[str]] = None
    # conversion factors
    conversion_factors: Optional[List[float | int]] = None
    # values
    values: Optional[List[Any]] = None
    # items
    items: Optional[List[Any]] = None

    # SECTION: data table
    # data table
    table: Dict[str, Any] = {}

    def __init__(
        self,
        name: str,
        data: str,
        id: int,
        types: str,
        equations: Optional[List[str]] = None,
        description: Optional[str] = None
    ):
        """
        Initializes the ThermoTable instance.

        Parameters
        ----------
        name : str
            The name of the table.
        data : str
            The data of the table in csv format.
        id : int
            The id of the table.
        types : str
            The type of the table.
        equations : Optional[List[str]], optional
            The equations associated with the table, by default None.
        description : Optional[str], optional
            The description of the table, by default None.
        """
        # NOTE: set attributes
        self._name = name
        self._data = data
        self._id = id
        self._types = types
        self._description = description if description else ""
        self._equations = equations if equations else []

        # reset the table
        self.table = {}

        # SECTION: initialize the parent class
        super().__init__()

    def __str__(self):
        """
        Returns a string representation of the ThermoTable instance.
        """
        return f"ThermoTable(name={self._name}, id={self._id}, type={self._types})"

    def __repr__(self):
        """
        Returns a detailed string representation of the ThermoTable instance.
        """
        return (f"ThermoTable(name={self._name}, id={self._id}, type={self._types}, "
                f"description={self._description}, equations={self._equations})")

    @property
    def name(self) -> str:
        """
        Returns the name of the table.
        """
        return self._name

    @property
    def id(self) -> int:
        """
        Returns the id of the table.
        """
        return self._id

    @property
    def types(self) -> str:
        """
        Returns the type of the table.
        """
        return self._types

    @property
    def description(self) -> str:
        """
        Returns the description of the table.
        """
        return self._description

    @property
    def equations(self) -> List[str]:
        """
        Returns the equations associated with the table.
        """
        return self._equations

    @property
    def matrix_symbol(self) -> List[str]:
        """
        Returns the matrix symbols associated with the table.
        """
        return self._matrix_symbol

    @property
    def get_table_name(self) -> str:
        """
        Returns the name of the table.
        """
        return self._name

    @property
    def get_table_id(self) -> int:
        """
        Returns the id of the table.
        """
        return self._id

    @property
    def get_data(self) -> str:
        """
        Returns the data of the table.
        """
        return self._data

    def update_data(self, new_data: str):
        """
        Updates the data of the table.

        Parameters
        ----------
        new_data : str
            The new data (csv format) to be set for the table.
        """
        self._data = new_data

    def extract(self):
        """
        Extracts the table data (csv format) and set attributes.


        """
        try:
            # SECTION: extract the data
            # NOTE: load the csv data
            data_ = self.load_csv(self._data)
            # NOTE: split the data into lines
            lines = self.extract_csv_data(data_)

            # SECTION: set the structure
            # NOTE: header (columns)
            header = lines[0]
            self.columns = header

            # NOTE: symbols
            symbol = lines[1]
            self.symbols = symbol

            # NOTE: units
            units = lines[2]

            # conversion factors
            # Default to 1.0 for each unit
            conversion_factors = [1.0] * len(units)
            self.units = units

            # LINK: update structure
            self.structure = {
                "COLUMNS": self.columns,
                "SYMBOL": self.symbols,
                "UNIT": self.units,
                "CONVERSION": conversion_factors
            }

            # NOTE: values
            # Skip the first three lines (header, symbols, units)
            self.values = lines[3:]

        except Exception as e:
            raise RuntimeError(f"Failed to extract table data: {e}")

    def build_table(self):
        """
        Builds the table from the extracted data.
        """
        try:
            # NOTE: build based on types
            if self._types == "data":
                self._build_data_table()
            elif self._types == "equation":
                self._build_equation_table()
            else:
                raise ValueError(f"Unsupported table type: {self.types}")
        except ValueError as ve:
            logging.error(f"Error building table '{self.name}': {ve}")
            raise

    def _build_data_table(self):
        """
        Builds the data table from the extracted data.
        """
        try:
            # SECTION: build the data table
            # NOTE: set the table
            self._table = {}

            # SECTION: extract the data
            self.extract()

            # SECTION: create the table structure
            TABLE = {}

            # NOTE: table name
            TABLE_NAME = self.get_table_name
            # set
            TABLE[TABLE_NAME] = {
                'TABLE-ID': self.get_table_id,
                'DESCRIPTION': self.description,
                'DATA': [],
                'MATRIX-SYMBOL': [],
                'STRUCTURE': self.structure,
                'VALUES': self.values,
                'ITEMS': []
            }

            # NOTE: copy the table
            self.table = TABLE

            # log success
            logging.info(f"Data table '{self.name}' built successfully.")
        except Exception as e:
            logging.error(f"Error building data table '{self.name}': {e}")
            raise

    def _build_equation_table(self):
        """
        Builds the equation table from the extracted data.
        """
        try:
            # SECTION: build the data table
            # NOTE: set the table
            self._table = {}

            # SECTION: extract the data
            self.extract()

            # check columns, symbols, and units
            if not self.columns or not self.symbols or not self.units:
                raise ValueError(
                    "Columns, symbols, and units must be provided for the equation table.")

            # section: extract equations
            if not self.equations:
                raise ValueError(
                    "No equations provided for the equation table.")

            # body
            equation_body = self.convert_function_equation_v2(
                self.equations[0],
                self.columns,
                self.symbols,
                self.units,
            )

            # equation structure
            equation_structure = {
                "EQ-1": {
                    'BODY': equation_body,
                    'BODY-INTEGRAL': 'None',
                    "BODY-FIRST-DERIVATIVE": 'None',
                    "BODY-SECOND-DERIVATIVE": 'None',
                }
            }

            # SECTION: create the table structure
            TABLE = {}

            # NOTE: table name
            TABLE_NAME = self.get_table_name
            # set
            TABLE[TABLE_NAME] = {
                'TABLE-ID': self.get_table_id,
                'DESCRIPTION': self.description,
                'DATA': [],
                'MATRIX-SYMBOL': [],
                'EQUATIONS': equation_structure,
                'STRUCTURE': self.structure,
                'VALUES': self.values,
                'ITEMS': []
            }

            # NOTE: copy the table
            self.table = TABLE
            # log success
            logging.info(f"Equation table '{self.name}' built successfully.")
        except Exception as e:
            logging.error(f"Error building equation table '{self.name}': {e}")
            raise
