# import packages/modules
import pandas as pd
from typing import Optional, List, Dict, Any, Union
# local imports
from ..models import DataResult


class TableData:
    # vars
    __trans_data = {}
    __prop_data = {}

    def __init__(self, databook_name, table_name, table_data,
                 table_values: Optional[List | Dict] = None,
                 table_structure: Optional[Dict[str, Any]] = None):
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
        self.__prop_data = {key: value for key,
                            value in value.items() if key != exclude_key}

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
    def table_units(self, unit_name: str = 'UNIT') -> List[str]:
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

    def get_property(self, property: str | int, message: Optional[str] = None) -> DataResult:
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

    def insert(self, property: str | int, message: Optional[str] = None) -> DataResult:
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
