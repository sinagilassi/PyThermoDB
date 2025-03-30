# import packages/modules
import pandas as pd
from typing import Optional
# local imports
from ..models import DataResult


class TableData:
    # vars
    __trans_data = {}
    __prop_data = {}

    def __init__(self, databook_name, table_name, table_data):
        self.databook_name = databook_name
        self.table_name = table_name
        self.table_data = table_data  # reference template (yml)

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

    def data_structure(self):
        '''
        Display data table structure

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