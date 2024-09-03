# import packages/modules
import pandas as pd


class TableData:
    # vars
    __trans_data = {}
    __prop_data = {}

    def __init__(self, table_name, table_data):
        self.table_name = table_name
        self.table_data = table_data

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
        df = pd.DataFrame(self.table_data)
        return df

    def get_property(self, property_name, dataframe=False):
        '''
        Get a component property from data table structure

        '''
        df = pd.DataFrame(self.prop_data)

        # choose a column
        if isinstance(property_name, str):
            df = df[property_name]
        elif isinstance(property_name, int):
            df = df.iloc[:, property_name]
        else:
            raise ValueError("loading error!")
        # check
        if dataframe:
            return df
        else:
            # convert to dict
            df = df.to_dict()
            return df
