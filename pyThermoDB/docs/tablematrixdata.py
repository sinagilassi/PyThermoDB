# import packages/modules
import pandas as pd
import numpy as np


class TableMatrixData:
    # vars
    __trans_data = {}
    __prop_data = {}
    # pack
    __trans_data_pack = {}
    __prop_data_pack = {}

    def __init__(self, table_name, table_data, matrix_table=None):
        self.table_name = table_name
        self.table_data = table_data
        self.matrix_table = matrix_table

    @property
    def trans_data_pack(self):
        return self.__trans_data_pack

    @trans_data_pack.setter
    def trans_data_pack(self, value):

        self.__trans_data_pack = {}
        self.__trans_data_pack = value

    @property
    def prop_data_pack(self):
        return self.__prop_data_pack

    @prop_data_pack.setter
    def prop_data_pack(self, value):
        self.__prop_data_pack = {}
        self.__prop_data_pack = value

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
        exclude_key = 'matrix-data'
        self.__prop_data = {key: value for key,
                            value in value.items() if key != exclude_key}

    def _find_component_prop_data(self, component_name_set: str):
        '''
        Get a component property from data table structure

        Parameters
        ----------
        component_name : str
            component name

        Returns
        -------
        value : dict
            component property
        '''
        try:
            # exclude key
            exclude_key = 'matrix-data'

            # set res
            prop_data = {}
            # looping through self.prop_data_pack
            for component_name, component_value in self.prop_data_pack.items():
                if component_name == component_name_set:
                    # check value
                    prop_data = {key: value for key,
                                 value in component_value.items() if key != exclude_key}
                    return prop_data
            # check
            if len(prop_data) == 0:
                raise Exception("Component not found!")
        except Exception as e:
            raise Exception("Finding component property failed!, ", e)

    def matrix_data_structure(self):
        '''
        Display matrix-data table structure
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

    def get_property(self, property: str, component_name: str):
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
        # find component property
        prop_data = self._find_component_prop_data(component_name)

        if not isinstance(prop_data, dict):
            raise Exception("Component property data is not a dictionary!")

        # dataframe
        df = pd.DataFrame(prop_data)

        # choose a column
        if isinstance(property, str):
            # df = df[property_name]
            # look up prop_data dict
            # check key exists
            if property in prop_data.keys():
                get_data = prop_data[property]
            else:
                # check symbol value in each item
                for key, value in prop_data.items():
                    if property == value['symbol']:
                        get_data = prop_data[key]
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

    def get_matrix_property_by_name(self, property: str):
        '''
        Get a component property from data table structure

        Parameters
        ----------
        property : str
            property name or id must be string as: Alpha_ij (i,j are component names) such as Alpha_ethanol_methanol

        Returns
        -------
        dict
            component property
        '''
        try:

            # check property name
            if "_" not in property.strip():
                raise Exception(
                    "Invalid property name. Please use the following format: Alpha_ij (i,j are component names) such as Alpha_ethanol_methanol"
                )

            # extract data
            prop_name, comp1, comp2 = property.split('_')

            # set property name
            prop_name = prop_name.strip()+'_i_j'

            # get matrix property
            matrix_property = self.get_matrix_property(
                prop_name, [comp1, comp2])

            return matrix_property
        except Exception as e:
            raise Exception("Getting matrix property failed!, ", e)

    def get_matrix_property(self, property: str, component_names: list[str],
                            symbol_format: str = 'alphabetic'):
        '''
        Get a component property from data table structure

        Parameters
        ----------
        property : str | int
            property name or id must be string as: Alpha_ij
        component_names : list[str]
            component names
        symbol_format : str
            symbol format alphabetic or numeric (default: alphabetic)

        Returns
        -------
        dict
            component property
        '''
        # matrix structure
        matrix_table = self.matrix_table

        # check dataframe
        if not isinstance(matrix_table, pd.DataFrame):
            raise Exception("Matrix data is not a dataframe!")

        # column name
        column_name = list(matrix_table.columns)

        # component names
        comp_i = 1
        matrix_table_component = {}
        for i, item in enumerate(matrix_table.iloc[:, 1].to_list()):
            # check item is a component name
            if item != "-" and len(item) > 1:
                matrix_table_component[item] = comp_i
                comp_i += 1

        # component names
        comp_no = len(matrix_table_component)

        # get component data (row)
        matrix_table_comp_data = {}
        for i in range(comp_no):
            _data = matrix_table.iloc[5+i, :].to_dict()
            _component_name = _data['Name']
            matrix_table_comp_data[_component_name] = _data

        res = 0
        # choose a column
        if isinstance(property, str) and property.endswith('_i_j'):
            # find the columns
            _property = property.split('_')
            property_name = _property[0]

            # matrix columns
            matrix_columns = []
            # matrix column index
            matrix_column_index = []

            # look for the property name in the column names
            for column in column_name:
                # column set
                column_set = column.split('_')[0]
                # check
                if property_name.upper() in column_set.upper():
                    # get the column index
                    column_index = column_name.index(column)
                    # get the column
                    matrix_columns.append(column)
                    # get the column index
                    matrix_column_index.append(column_index)

            # check matrix columns
            if len(matrix_columns) != comp_no:
                raise Exception(
                    "Matrix columns do not match the number of components!")
            # check matrix column index
            if len(matrix_column_index) != comp_no:
                raise Exception(
                    "Matrix column index does not match the number of components!")

            # property value
            comp1_index = matrix_table_component[component_names[0]] - 1
            comp2_index = matrix_table_component[component_names[1]] - 1

            # property column
            property_column = matrix_columns[comp2_index]
            # get index
            property_column_index = matrix_column_index[comp2_index]
            # get property value
            property_value = matrix_table.iloc[comp1_index +
                                               5, property_column_index]
            # get property symbol
            symbol_idx = str(matrix_table.iloc[0, property_column_index]).split('_')[
                0]+'_'+str(comp1_index+1)+'_'+str(comp2_index+1)
            # symbol name
            symbol_name = str(matrix_table.iloc[0, property_column_index]).split('_')[
                0]+'_'+str(component_names[0])+'_'+str(component_names[1])

            # set symbol
            if symbol_format.lower() == 'alphabetic':
                property_symbol = symbol_name
            elif symbol_format.lower() == 'numeric':
                property_symbol = symbol_idx
            else:
                raise ValueError(
                    f"Symbol format {symbol_format} not recognized.")

            # get property unit
            property_unit = matrix_table.iloc[1, property_column_index]

            # res
            res = {
                "symbol": property_symbol,
                "unit": property_unit,
                "value": property_value
            }

            # return
            return res
        else:
            raise ValueError(f"Property format {property} not recognized.")

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
