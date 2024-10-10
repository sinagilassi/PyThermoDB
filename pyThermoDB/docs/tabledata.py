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

    def get_property(self, property):
        '''
        Get a component property from data table structure

        Parameters
        ----------
        property : str | int
            property name or id

        Returns
        -------
        dict
            component property
        '''
        # dataframe
        df = pd.DataFrame(self.prop_data)

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
                        get_data = self.prop_data[key]
                        break
            # series
            sr = pd.Series(get_data)

        elif isinstance(property, int):
            # get column index
            column_index = df.columns[property-1]
            sr = df.loc[:, column_index]

        else:
            raise ValueError("loading error!")

        return sr.to_dict()

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
