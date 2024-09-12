# import packages/modules
import pandas as pd
import yaml


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

    def get_property(self, property_name, dataframe=False):
        '''
        Get a component property from data table structure

        Parameters
        ----------
        property_name : str | int
            string/int of property name
        dataframe : bool, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        df : dataframe
            component property

        '''
        # dataframe
        df = pd.DataFrame(self.prop_data)

        # choose a column
        if isinstance(property_name, str):
            df = df[property_name]
        elif isinstance(property_name, int):
            df = df.iloc[:, property_name-1]
        else:
            raise ValueError("loading error!")
        # check
        if dataframe:
            return df
        else:
            # convert to dict
            df = df.to_dict()
            return df

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
