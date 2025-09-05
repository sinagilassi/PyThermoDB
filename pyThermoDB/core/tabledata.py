# import packages/modules
import logging
import pandas as pd
from typing import Optional, List, Dict, Any, Literal
# local imports
from ..models import DataResult
from .table_util import TableUtil
from ..models import PropertyMatch

# logger
logger = logging.getLogger(__name__)


class TableData:
    # vars
    __trans_data = {}
    __prop_data = {}

    def __init__(
        self,
        databook_name,
        table_name,
        table_data,
        table_values: Optional[List | Dict] = None,
        table_structure: Optional[Dict[str, Any]] = None
    ):
        '''
        Initialize TableData class

        Parameters
        ----------
        databook_name : str
            databook name
        table_name : str
            table name
        table_data : dict
            table data (dict), taken directly from yml file
        table_values : list | dict, optional
            table values (default: None), taken directly from yml file if exists
        table_structure : dict, optional
            table structure (default: None), taken directly from yml file if exists
        '''
        self.databook_name = databook_name
        self.table_name = table_name
        self.table_data = table_data  # reference template (yml)
        # table values (yml)
        self.__table_values = table_values if table_values else None
        self.__table_structure = table_structure if table_structure else None

    @property
    def trans_data(self):
        return self.__trans_data

    @trans_data.setter
    def trans_data(self, value):
        self.__trans_data = {}
        self.__trans_data = value

    @property
    def prop_data(self):
        return self.__prop_data

    @prop_data.setter
    def prop_data(self, value):
        self.__prop_data = {}
        exclude_key = 'data'
        self.__prop_data = {
            key: value for key, value in value.items() if key != exclude_key
        }

    @property
    def table_values(self):
        '''Get table values from yml file (if exists)'''
        if self.__table_values:
            return self.__table_values
        else:
            msg = f"""No table values found in the following reference \n
            ::: {self.databook_name}
            :::  {self.table_name}!
            """
            print(msg)
            return None

    @property
    def table_structure(self):
        '''Get table structure from yml file (if exists)'''
        if self.__table_structure:
            return self.__table_structure
        else:
            msg = f"""No table structure found in the following reference \n
            ::: {self.databook_name}
            :::  {self.table_name}!
            """
            print(msg)
            return None

    @property
    def table_columns(self, column_name: str = 'COLUMNS') -> List[str]:
        '''
        Get table columns from data-table structure

        Parameters
        ----------
        column_name : str
            column name (default: 'COLUMNS')

        Returns
        -------
        columns : list
            list of columns
        '''
        try:
            return self.table_data[column_name]
        except KeyError:
            raise KeyError(
                "Table columns not found in the data table structure!")
        except Exception as e:
            raise Exception(f"Error retrieving table columns: {e}")

    @property
    def table_symbols(self, symbol_name: str = 'SYMBOL') -> List[str]:
        '''
        Get table symbols from data-table structure

        Parameters
        ----------
        symbol_name : str
            symbol name (default: 'SYMBOL')

        Returns
        -------
        symbols : list
            list of symbols
        '''
        try:
            return self.table_data[symbol_name]
        except KeyError:
            raise KeyError(
                "Table symbols not found in the data table structure!")
        except Exception as e:
            raise Exception(f"Error retrieving table symbols: {e}")

    @property
    def table_units(
        self,
        unit_name: str = 'UNIT'
    ) -> List[str]:
        '''
        Get table units from data-table structure

        Parameters
        ----------
        unit_name : str
            unit name (default: 'UNIT')

        Returns
        -------
        units : list
            list of units
        '''
        try:
            return self.table_data[unit_name]
        except KeyError:
            raise KeyError(
                "Table units not found in the data table structure!")
        except Exception as e:
            raise Exception(f"Error retrieving table units: {e}")

    def data_structure(self):
        '''
        Display data-table structure including `column names`, `symbol`, `units` and `values`
        '''
        # dataframe
        df = pd.DataFrame(self.table_data)
        # add ID column
        df.insert(0, 'ID', range(1, len(df) + 1))
        # arrange columns
        # change the position of ID column to the last
        cols = df.columns.tolist()
        cols.insert(len(cols), cols.pop(cols.index('ID')))
        df = df[cols]

        return df

    def get_property(
            self,
            property: str | int,
            message: Optional[str] = None
    ) -> DataResult:
        '''
        Get a component property from data table structure

        Parameters
        ----------
        property : str | int
            property name or id
        message : str
            message to display when property is found or not found

        Returns
        -------
        data_dict : DataResult
            property result dict
        '''
        # ! get data for a selected component
        # dataframe
        df = pd.DataFrame(self.prop_data)

        get_data = None
        # choose a column
        if isinstance(property, str):
            # df = df[property_name]
            # look up prop_data dict
            # ! case insensitive
            prop_data_keys_ = [key.lower() for key in self.prop_data.keys()]

            # NOTE: property lower
            property_ = property.lower().strip()

            # check key exists
            if property_ in prop_data_keys_:
                # loop through prop_data dict
                for key, value in self.prop_data.items():
                    # check key
                    if property_ == key.lower():
                        # value found
                        get_data = self.prop_data[key]
                        # property name
                        property = key
                        break
                # get_data = self.prop_data[property]
            else:
                # NOTE: symbol
                # check symbol value in each item
                for key, value in self.prop_data.items():
                    # check if property is in the symbol
                    # ! case insensitive
                    if property_ == str(value['symbol']).lower().strip():
                        # value found
                        get_data = self.prop_data[key]
                        # property name
                        property = key
                        break

            # ! check if property found
            if get_data is None:
                raise ValueError(f"Property '{property}' not found!")
            # series
            sr = pd.Series(get_data, dtype='str')
            # print(type(sr))

        elif isinstance(property, int):
            # get column index
            column_index = df.columns[property-1]
            sr = df.loc[:, column_index]
            # print(type(sr))

        else:
            raise ValueError(f"loading error! {property} is not a valid type!")

        # convert to dict
        data_dict = DataResult(**sr.to_dict())
        # print(data_dict, type(data_dict))

        # property name
        if isinstance(property, str):
            data_dict['property_name'] = property
        else:
            data_dict['property_name'] = df.columns[property-1]

        # update message
        if message:
            data_dict['message'] = str(message)
        else:
            data_dict['message'] = 'No message'

        # add databook and table name
        data_dict['databook_name'] = self.databook_name if self.databook_name else 'No databook name'
        data_dict['table_name'] = self.table_name if self.table_name else 'No table name'

        # res
        return data_dict

    def insert(
            self,
            property: str | int,
            message: Optional[str] = None
    ) -> DataResult:
        '''
        Get a component property from data table structure

        Parameters
        ----------
        property : str | int
            property name, symbol or id
        message : str
            message to display when property is found or not found

        Returns
        -------
        data_dict : DataResult
            property result dict
        '''
        # ! get data for a selected component
        # dataframe
        df = pd.DataFrame(self.prop_data)

        get_data = None
        # choose a column
        if isinstance(property, str):
            # df = df[property_name]
            # look up prop_data dict
            # check key exists
            if property in self.prop_data.keys():
                get_data = self.prop_data[property]
            else:
                # check symbol value in each item
                for key, value in self.prop_data.items():
                    if property == value['symbol']:
                        # value found
                        get_data = self.prop_data[key]
                        # property name
                        property = key
                        break
            if get_data is None:
                raise ValueError(f"Property '{property}' not found!")
            # series
            sr = pd.Series(get_data, dtype='str')
            # print(type(sr))

        elif isinstance(property, int):
            # get column index
            column_index = df.columns[property-1]
            sr = df.loc[:, column_index]
            # print(type(sr))

        else:
            raise ValueError(f"loading error! {property} is not a valid type!")

        # convert to dict
        data_dict = DataResult(**sr.to_dict())
        # print(data_dict, type(data_dict))

        # property name
        if isinstance(property, str):
            data_dict['property_name'] = property
        else:
            data_dict['property_name'] = df.columns[property-1]

        # update message
        if message:
            data_dict['message'] = str(message)
        else:
            data_dict['message'] = 'No message'

        # add databook and table name
        data_dict['databook_name'] = self.databook_name if self.databook_name else 'No databook name'
        data_dict['table_name'] = self.table_name if self.table_name else 'No table name'

        # res
        return data_dict

    def to_dict(self):
        '''
        Convert prop to dict

        Parameters
        ----------
        component_name : str
            component name

        Returns
        -------
        res : dict
            dict
        '''
        try:
            # comp data
            res = self.prop_data

            return res
        except Exception as e:
            raise Exception("Conversion failed!, ", e)

    def is_symbol_available(self, symbol: str):
        '''
        Check if a symbol is available in the table data. This method is case-insensitive.

        Parameters
        ----------
        symbol : str
            Symbol to check.

        Returns
        -------
        bool
            True if the symbol is available, False otherwise.
        '''
        try:
            # NOTE: get symbols
            symbols = self.table_symbols

            # SECTION: check if symbol exists (case-sensitive)
            return TableUtil.is_symbol_available(symbol, symbols)
        except Exception as e:
            logger.error(f"Error checking symbol availability: {e}")
            return PropertyMatch(
                prop_id=symbol,
                availability=False,
                search_mode='SYMBOL',
            )

    def is_column_name_available(self, column_name: str):
        '''
        Check if a column name is available in the table data.

        Parameters
        ----------
        column_name : str
            Column name to check.

        Returns
        -------
        bool
            True if the column name is available, False otherwise.
        '''
        try:
            # NOTE: get column names
            column_names = self.table_columns

            # SECTION: check if column exists (case-sensitive)
            return TableUtil.is_column_name_available(column_name, column_names)
        except Exception as e:
            logger.error(f"Error checking column name availability: {e}")
            return PropertyMatch(
                prop_id=column_name,
                availability=False,
                search_mode='COLUMN',
            )

    def is_property_available(
            self,
            prop_id: str,
            search_mode: Literal[
                'SYMBOL', 'COLUMN', 'BOTH'
            ] = 'BOTH'
    ) -> PropertyMatch:
        '''
        Check if a property is available in the table data.

        Parameters
        ----------
        prop_id : str
            Property ID to check.
        search_mode : Literal['SYMBOL', 'COLUMN', 'BOTH'], optional
            Search mode (default: 'BOTH'). Can be 'SYMBOL', 'COLUMN', or 'BOTH'.

        Returns
        -------
        bool
            True if the property is available, False otherwise.
        '''
        try:
            # NOTE: check inputs
            if not isinstance(prop_id, str):
                logger.error(
                    "Invalid property ID input! Property ID must be a string.")
                return False

            # SECTION: get property names
            if search_mode == 'SYMBOL':
                # ! symbol only
                return self.is_symbol_available(prop_id)
            elif search_mode == 'COLUMN':
                # ! column name only
                return self.is_column_name_available(prop_id)
            elif search_mode != 'BOTH':
                logger.error(
                    "Invalid search mode! Must be 'SYMBOL', 'COLUMN', or 'BOTH'."
                )
                return False

            # SECTION: check both symbol and column name
            # NOTE: check symbols (true/false)
            check_symbol_res = self.is_symbol_available(prop_id)

            # NOTE: check column names (true/false)
            check_column_res = self.is_column_name_available(prop_id)

            # check
            if check_symbol_res.availability or check_column_res.availability:
                return PropertyMatch(
                    prop_id=prop_id,
                    availability=True,
                    search_mode='BOTH'
                )
            else:
                return PropertyMatch(
                    prop_id=prop_id,
                    availability=False,
                    search_mode='BOTH'
                )

        except Exception as e:
            logger.error(f"Error checking property availability: {e}")
            return PropertyMatch(
                prop_id=prop_id,
                availability=False,
                search_mode=search_mode,
            )
