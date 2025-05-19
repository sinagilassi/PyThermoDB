# import packages/modules
import pandas as pd
import numpy as np
from typing import Union, Optional, Any, Literal, TypedDict, Dict, List, Tuple
from warnings import warn
# local
from ..models import DataResultType, DataResult


class TableMatrixData:
    # vars
    __trans_data = {}
    __prop_data = {}
    __matrix_symbol = None
    __table_structure = None
    # pack
    __trans_data_pack = {}
    __prop_data_pack = {}
    # matrix elements
    __matrix_elements = None
    # matrix items
    __matrix_items: Optional[List[Dict[str, List[str | int | float]]]] = None
    # matrix item keys
    __matrix_item_keys: Optional[List[str]] = None
    # matrix mode
    matrix_mode: Literal['VALUES', 'ITEMS'] = 'VALUES'

    def __init__(self,
                 databook_name: str | int,
                 table_name: str | int,
                 table_data,
                 matrix_table=None,
                 matrix_symbol: Optional[List[str]] = None):
        self.databook_name = databook_name
        self.table_name = table_name
        self.table_data = table_data  # NOTE: reference template (yml)
        self.matrix_table = matrix_table  # all elements saved in the matrix-table

        # NOTE: check
        if matrix_symbol is None:
            # matrix symbol such as Alpha_i_j
            symbol_ = self.table_data['MATRIX-SYMBOL']
            self.__matrix_symbol = symbol_

            # matrix items
            items_ = self.table_data.get('ITEMS', None)
            # check
            if items_ is not None and items_ != "None":
                # setting matrix items
                self.__set_matrix_items(items_)

        # NOTE: table structure
        self.__generate_table_structure(self.table_data)

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

    @property
    def matrix_symbol(self):
        return self.__matrix_symbol

    @property
    def matrix_elements(self):
        return self.__matrix_elements

    @matrix_elements.setter
    def matrix_elements(self, value):
        self.__matrix_elements = {}
        self.__matrix_elements = value

    @property
    def matrix_items(self):
        """Return matrix items if valid, otherwise None."""
        if isinstance(self.__matrix_items, list) and self.__matrix_items:
            return self.__matrix_items
        return None

    @property
    def matrix_item_keys(self):
        """Get matrix item keys"""
        return self.__matrix_item_keys

    def __set_matrix_items(self, matrix_items):
        """Set matrix items"""
        # init
        self.__matrix_item_keys = []
        self.__matrix_items = []

        # check
        if matrix_items is not None:
            # check
            if isinstance(matrix_items, list) and len(matrix_items) > 0:

                # looping through matrix items
                for item in matrix_items:
                    # looping through item
                    for key, value in item.items():
                        # check
                        if "|" in key:
                            # split key
                            key_split = key.split('|')
                            # check
                            if len(key_split) != 2:
                                raise Exception(
                                    "Matrix item key is not in the correct format!")

                            # strip
                            key_split = [name.strip() for name in key_split]
                            # std key
                            key_std = " | ".join(key_split)

                            # NOTE: build component-n | component-n
                            keys_identical = []
                            # looping through component names
                            for name in key_split:
                                # create key
                                key_identical = f"{name.strip()} | {name.strip()}"
                                # set
                                keys_identical.append(key_identical)

                            # set
                            self.__matrix_item_keys.append(key_std)
                            self.__matrix_item_keys.extend(keys_identical)
                            # set
                            self.__matrix_items.append({
                                key_std: value
                            })

                # NOTE: update matrix mode
                if len(matrix_items) > 0:
                    self.matrix_mode = 'ITEMS'
            else:
                # set
                self.__matrix_item_keys = []
        else:
            # set
            self.__matrix_item_keys = []

    def __generate_table_items(self, component_names: list[str]):
        '''
        Generate dataframe for each matrix item

        Parameters
        ----------
        component_names : list[str]
            component names

        Notes
        -----
        The Dataframe structure is based on columns, symbols, units as:
        - header: No.,Name,Formula, matrix_symbol, matrix_symbol, ...
        - row 1: No.,Name,Formula, matrix_symbol, matrix_symbol, ...
        - row 2: None,None,None,1,1,1, ...
        - row 3: None,None,None, 1,2,1,2, ...

        Build two rows for each matrix item:
        - row 4: None, None, None, component1_name, component2_name, ...
        - row 5: None, None, None, component1_symbol, component2_symbol, ...

        Embedded the item data (List[List[str | int | float]]) in the matrix table as:
        - row 6: 1, component1_name, component1_formula, 1, 1, 1, ...
        - row 7: 2, component2_name, component2_formula, 1, 1, 1, ...
        '''
        try:
            # NOTE: matrix structure
            table_structure = self.__table_structure
            # check
            if table_structure is None:
                raise Exception("Table structure is None!")

            # extract
            columns = table_structure.get('COLUMNS', None)
            symbol = table_structure.get('SYMBOL', None)
            unit = table_structure.get('UNIT', None)

            # NOTE: matrix symbols
            matrix_symbol = self.__matrix_symbol
            # number of matrix symbols
            matrix_symbol_num = len(matrix_symbol) if matrix_symbol else 0
            # check
            if matrix_symbol_num == 0:
                raise Exception("Matrix symbol is None!")

            # NOTE: item tables
            # item_tables = {}

            # SECTION: component names
            # set strip
            component_names = [name.strip() for name in component_names]
            # temp key
            key = " | ".join(component_names)

            # check
            if self.__matrix_item_keys:
                if key not in self.__matrix_item_keys:
                    return None

            # SECTION: matrix items
            # check
            if self.matrix_items and isinstance(self.matrix_items, dict):
                # selected matrix items
                value = self.matrix_items.get(key, None)

                # if value is None:
                if value is None or not isinstance(value, list) and len(value) == 0:
                    return None

                # ? key: components names [str | str]
                # ? value: components data [str | int | float]
                # key contains separator [|]
                if "|" in key:
                    # split key
                    key_split = key.split('|')
                    # check
                    if len(key_split) != 2:
                        raise Exception(
                            "Matrix item key is not in the correct format!")

                    # temp component names
                    temp_component_names_ = [
                        name.strip() for name in key_split]

                    # component idx
                    temp_comp_idx_ = [str(i+1) for i, name in enumerate(
                        temp_component_names_) if name in component_names]

                    # formula
                    temp_component_formula_ = []

                    # looping through component names
                    for name in temp_component_names_:
                        # check component values
                        for v in value:
                            # check
                            if isinstance(v, list):
                                if name in v[0:3]:
                                    # set
                                    temp_component_formula_.append(v[2])

                    # repeated based on matrix symbol
                    temp_component_names = temp_component_names_*matrix_symbol_num
                    # repeated based on matrix symbol
                    temp_component_formula = temp_component_formula_*matrix_symbol_num
                    # repeated based on matrix symbol
                    temp_component_idx = temp_comp_idx_*matrix_symbol_num

                    # NOTE: build row 3
                    row_3 = ['-', '-', '-']
                    # update row 3
                    row_3.extend(temp_component_idx)

                    # NOTE: build row 4
                    row_4 = ['None', 'None', 'None']
                    # update row 4
                    row_4.extend(temp_component_names)

                    # NOTE: build row 5
                    row_5 = ['None', 'None', 'None']
                    # update row 5
                    row_5.extend(temp_component_formula)

                    # NOTE: dataframe data
                    df_data = [
                        symbol, unit, row_3, row_4, row_5, *value
                    ]

                    # create dataframe
                    df = pd.DataFrame(
                        columns=columns,
                        data=df_data,
                    )

                    # NOTE: set
                    # item_key = " | ".join(temp_component_names_)
                    # item_tables[item_key] = df

                # res
                return df
            else:
                # res
                return None
        except Exception as e:
            raise Exception("Generating matrix items failed!, ", e)

    def __generate_table_structure(self, table_data: dict[str, Any]):
        '''
        Generate table structure from data table

        Parameters
        ----------
        table_data : dict[str, Any]
            data table
        '''
        try:
            # init
            self.__table_structure = {}
            # looping through table data
            for key, value in self.table_data.items():
                if key != 'MATRIX-SYMBOL' and key != 'ITEMS':
                    # set
                    self.__table_structure[key] = value

            # check
            if self.__table_structure is None:
                raise Exception("Table structure is None!")
        except Exception as e:
            raise Exception("Generating table structure failed!, ", e)

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
        try:
            # NOTE: choose from table data structure all except matrix-symbol
            # dataframe
            df = pd.DataFrame(self.__table_structure)
            # add ID column
            df.insert(0, 'ID', range(1, len(df) + 1))
            # arrange columns
            # change the position of ID column to the last
            cols = df.columns.tolist()
            cols.insert(len(cols), cols.pop(cols.index('ID')))
            df = df[cols]

            return df
        except Exception as e:
            raise Exception("Matrix data structure failed!, ", e)

    def get_matrix_table(self, mode: Literal['all', 'selected'] = 'all') -> pd.DataFrame:
        '''
        Get matrix table data

        Parameters
        ----------
        mode : str
            mode of data table (all or selected)

        Returns
        -------
        pd.DataFrame
            matrix table data
        '''
        try:
            # matrix table
            matrix_table = self.matrix_table

            if matrix_table is None:
                raise Exception("Matrix table is None!")

            # NOTE: check mode
            if mode == 'all':
                # SECTION: matrix table (all data)
                return matrix_table
            elif mode == 'selected':
                # SECTION: get all records in Name column
                # matrix table
                Names = matrix_table['Name'].unique()
                Names = [str(i) for i in Names if str(i) != "-"]

                # selected records
                Names_selected = self.matrix_elements

                # check
                if Names_selected is None:
                    raise Exception("Selected records are None!")

                # reduced records
                Names_ignored = [i for i in Names if i not in Names_selected]

                # NOTE: remove row where Name is XXX
                # matrix table
                matrix_table_filtered = matrix_table[~matrix_table['Name'].isin(
                    Names_ignored)]
                # drop columns for all Names ignored
                for column in matrix_table_filtered.columns:
                    # looping through ignored names
                    for name in Names_ignored:
                        # check column name
                        if name in matrix_table_filtered[column].values:
                            # drop column
                            matrix_table_filtered = matrix_table_filtered.drop(
                                column, axis=1)
                # return filtered matrix table
                return matrix_table_filtered
            else:
                raise ValueError("Mode not recognized!")
        except Exception as e:
            raise Exception("Getting matrix table failed!, ", e)

    def get_property(self, property: str | int, component_name: str) -> DataResultType | dict:
        '''
        Get a component property from data table structure

        Parameters
        ----------
        property : str | int
            property name or id
        component_name : str
            component name

        Returns
        -------
        dict
            component property
        '''
        # find component property
        prop_data = self._find_component_prop_data(component_name)

        if not isinstance(prop_data, dict):
            raise Exception("Component property data is not a dictionary!")

        # dataframe (selected component data)
        df = pd.DataFrame(prop_data)

        # choose a column
        if isinstance(property, str):
            # df = df[property_name]
            # look up prop_data dict
            # check key exists
            if property in prop_data.keys():
                get_data = prop_data[property]  # return dict
            else:
                # check symbol value in each item
                for key, value in prop_data.items():
                    if property == value['symbol']:
                        get_data = prop_data[key]
                        break

            # print(type(get_data))
            return get_data

        elif isinstance(property, int):
            # get column index
            column_index = df.columns[property-1]
            sr: pd.Series = df.loc[:, column_index]

            # set
            get_data = sr.to_dict()

            return get_data

        else:
            raise ValueError("loading error!")

    def get_matrix_property_by_name(self, property: str) -> DataResult:
        '''
        Get a component property from data table structure

        Parameters
        ----------
        property : str
            property name or id must be string as: Alpha_ij (i,j are component names) such as `Alpha_ethanol_methanol`

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

    def ij(self,
           property: str,
           symbol_format: Literal[
               'alphabetic', 'numeric'
           ] = 'alphabetic',
           message: Optional[str] = None) -> DataResult:
        '''
        Get a component property from data table structure (matrix data)

        Parameters
        ----------
        property : str
            property name or id must be string as: Alpha_ij (i,j are component names) such as `Alpha_ethanol_methanol` or `Alpha | ethanol | methanol`
        symbol_format : str
            symbol format alphabetic or numeric (default: alphabetic)
        message : str
            message (default: None)

        Returns
        -------
        matrix_property: DataResult
            component property taken from matrix data
        '''
        try:
            # check property name
            # check not empty
            if property is None or property.strip() == "":
                raise Exception("Property name is empty!")

            # extract data
            # NOTE: format 1: Alpha_ij (i,j are component names) such as `Alpha_ethanol_methanol`
            # check contains underscore
            extracted = property.strip().split('_')

            # check len
            if len(extracted) == 3:
                prop_name, comp1, comp2 = extracted
                # remove _ij
                prop_name = prop_name.replace('_ij', '')
            else:
                # NOTE: format 2: Alpha | ethanol | methanol
                extracted = property.strip().split('|')

                # check len
                if len(extracted) == 3:
                    prop_name, comp1, comp2 = extracted
                    # remove _ij
                    prop_name = prop_name.replace('_ij', '')
                else:
                    raise Exception(
                        "Invalid property name. It should have three parts, Please use the following format: Alpha_ij (i,j are component names) such as Alpha_ethanol_methanol"
                    )

            # NOTE: check all extracted
            if prop_name is None or comp1 is None or comp2 is None:
                raise Exception("Property name is not in the correct format!")

            # trim
            prop_name = prop_name.strip()
            comp1 = comp1.strip()
            comp2 = comp2.strip()

            # set property name
            prop_name = prop_name+'_i_j'

            # set message
            if message is None:
                message = f"Get {prop_name} property from matrix data table structure"

            # get matrix property
            matrix_property = self.get_matrix_property(
                prop_name, [comp1, comp2], symbol_format, message)

            return matrix_property
        except Exception as e:
            raise Exception("Getting matrix property failed!, ", e)

    def get_matrix_property(self,
                            property: str,
                            component_names: list[str],
                            symbol_format: Literal[
                                'alphabetic', 'numeric'
                            ] = 'alphabetic',
                            message: str = 'Get a component property from data table structure') -> DataResult:
        '''
        Get a component property from data table structure

        Parameters
        ----------
        property : str
            property must be a string as: Alpha_ij
        component_names : list[str]
            component names such as ['ethanol', 'methanol']
        symbol_format : str
            symbol format alphabetic or numeric (default: alphabetic)

        Returns
        -------
        DataResult
            component property
        '''
        # NOTE: warning deprecated method
        # warn("get_matrix_property is deprecated, use ij method instead",
        #      DeprecationWarning, stacklevel=2)

        # NOTE: check matrix mode
        if self.matrix_mode == 'ITEMS':
            # SECTION: check matrix items
            matrix_table = self.__generate_table_items(component_names)

        elif self.matrix_mode == 'VALUES':
            # SECTION: matrix structure (all data)
            matrix_table = self.matrix_table

        else:
            raise Exception("Matrix mode is not recognized!")

        # ! check dataframe
        if not isinstance(matrix_table, pd.DataFrame):
            raise Exception("Matrix data is not a dataframe!")

        # column name
        matrix_table_column_name = list(matrix_table.columns)

        # NOTE: component names
        comp_i = 1
        matrix_table_component = {}
        # looping through Name column
        for i, item in enumerate(list(matrix_table['Name'])):
            # check item is a component name
            if item != "-" and len(item) > 1 and item != 'None' and item != 'None':
                matrix_table_component[item] = comp_i
                comp_i += 1

        # component names
        matrix_table_component_no = len(matrix_table_component)

        # matrix table component keys
        matrix_table_component_names = list(matrix_table_component.keys())

        # get component data (row)
        matrix_table_comp_data = {}
        # looping through component
        for i in range(matrix_table_component_no):
            # define filter for component
            component_name_filter = matrix_table_component_names[i]

            # get component data
            _data_get = matrix_table[matrix_table['Name'].str.match(
                component_name_filter, case=False, na=False)]

            # set
            _row_index = int(_data_get.index[0])
            _data = _data_get.to_dict(orient='records')[0]

            # update
            _data['row_index'] = _row_index

            # check
            if len(_data) == 0:
                raise Exception("No data for component: " +
                                component_name_filter)

            # get component data
            _component_name = _data['Name']
            matrix_table_comp_data[_component_name] = _data

        # ! manage property
        if isinstance(property, str) and property.endswith('_i_j'):
            # find the columns
            _property = property.split('_')
            property_name = _property[0]

            # matrix columns
            matrix_columns = []
            # matrix column index
            matrix_column_index = []

            # look for the property name in the column names
            for column in matrix_table_column_name:
                # column name set
                column_set = column.split('_')[0]
                # check
                if property_name.upper() == column_set.upper():
                    # get the column index
                    column_index = matrix_table_column_name.index(column)
                    # get the column
                    matrix_columns.append(column)
                    # get the column index
                    matrix_column_index.append(column_index)

            # check matrix columns
            if len(matrix_columns) != matrix_table_component_no:
                raise Exception(
                    "Matrix columns do not match the number of components!")
            # check matrix column index
            if len(matrix_column_index) != matrix_table_component_no:
                raise Exception(
                    "Matrix column index does not match the number of components!")

            # property value
            comp1_index = matrix_table_component[component_names[0]] - 1
            comp2_index = matrix_table_component[component_names[1]] - 1

            # row index component 1
            row_index_comp1 = matrix_table_comp_data[component_names[0]].get(
                'row_index')
            # row index component 2
            row_index_comp2 = matrix_table_comp_data[component_names[1]].get(
                'row_index')

            # property column
            property_column = matrix_columns[comp2_index]
            # get index
            property_column_index = matrix_column_index[comp2_index]

            # get property value
            property_value = matrix_table.iat[row_index_comp1,
                                              property_column_index]

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
            res: DataResult = {
                "property_name": str(property_name),
                "symbol": str(property_symbol),
                "unit": str(property_unit),
                "value": float(property_value),
                "message": message if message else "No message",
                "databook_name": self.databook_name,
                "table_name": self.table_name
            }

            # return
            return res
        else:
            raise ValueError(f"Property format {property} not recognized.")

    def ijs(self,
            property: str,
            res_format: Literal[
                'alphabetic', 'numeric'
            ] = 'alphabetic',
            symbol_delimiter: Literal[
                "|", "_"
            ] = "|"
            ) -> Dict[str, float | int] | np.ndarray:
        '''
        Generate a dictionary for ij property

        Parameters
        ----------
        property : str
            property name must be string as: Alpha_ij (i,j are component names) such as `Alpha_ethanol_methanol` or `Alpha | ethanol | methanol`
        res_format : str
            result format (default: dict)
        symbol_delimiter : str
            symbol delimiter (default: |), array element symbol delimiter
            such as `Alpha | ethanol | methanol` or `Alpha_ethanol_methanol`

        Returns
        -------
        dict
            dictionary for ij property
        '''
        try:
            # check property name
            # check not empty
            if property is None or property.strip() == "":
                raise Exception("Property name is empty!")

            # extract data
            # NOTE: format 1: Alpha_ij (i,j are component names) such as `Alpha_ethanol_methanol`
            # check contains underscore
            extracted = property.strip().split('_')

            # check len
            if len(extracted) == 3:
                prop_name, comp1, comp2 = extracted
                # remove _ij
                prop_name = prop_name.replace('_ij', '')
            else:
                # NOTE: format 2: Alpha | ethanol | methanol
                extracted = property.strip().split('|')

                # check len
                if len(extracted) == 3:
                    prop_name, comp1, comp2 = extracted
                    # remove _ij
                    prop_name = prop_name.replace('_ij', '')
                else:
                    raise Exception(
                        "Invalid property name. It should have three parts, Please use the following format: Alpha_ij (i,j are component names) such as Alpha_ethanol_methanol"
                    )

            # NOTE: check all extracted
            if prop_name is None or comp1 is None or comp2 is None:
                raise Exception("Property name is not in the correct format!")

            # check
            if comp1 == comp2:
                raise Exception("Component names are the same!")

            # set property name
            prop_name = prop_name.strip()

            # components
            components = [comp1.strip(), comp2.strip()]

            # res
            res_array = np.zeros((len(components), len(components)))
            res_dict = {}

            # NOTE: set
            if symbol_delimiter == "_":
                symbol_delimiter_set = "_"
            elif symbol_delimiter == "|":
                symbol_delimiter_set = " | "
            else:
                raise Exception("Symbol delimiter not recognized!")

            # NOTE: extract data
            for i in range(len(components)):
                for j in range(len(components)):
                    # key
                    key = f"{components[i]}_{components[j]}"
                    prop_ = f"{prop_name}_{key}"

                    # get property
                    val = self.ij(prop_).get('value')

                    # set
                    key_comp = f"{components[i]}{symbol_delimiter_set}{components[j]}"
                    res_dict[key_comp] = val
                    res_array[i][j] = val

            # check
            if res_format == 'alphabetic':
                # NOTE: convert to alphabetic format
                return res_dict
            elif res_format == 'numeric':
                # NOTE: convert to numeric format
                return res_array
            else:
                raise Exception("Result format not recognized!")

        except Exception as e:
            raise Exception("Generating dictionary failed!, ", e)

    def mat(self,
            property_name: str,
            component_names: list[str],
            symbol_format: Literal['alphabetic', 'numeric'] = 'numeric'):
        '''
        Get matrix data

        Parameters
        ----------
        property_name : str
            property name such as `Alpha` represented `Alpha_ij`
        component_names : list[str]
            component names such as ['ethanol', 'methanol']
        symbol_format : str
            symbol format alphabetic or numeric (default: numeric)

        Returns
        -------
        dict | np.ndarray
            matrix data (dict or np.ndarray)
        '''
        try:
            # NOTE: check property name
            # check not empty
            if property_name is None or property_name.strip() == "":
                raise Exception("Property name is empty!")
            # set
            property_name = property_name.strip()
            # remove _i_j
            property_name = property_name.replace('_i_j', '')

            # NOTE: check component names
            if component_names is None or len(component_names) == 0:
                raise Exception("Component names are empty!")
            # component num
            component_num = len(component_names)

            # component strip
            components = [name.strip() for name in component_names]

            # NOTE: matrix data
            mat_ij = np.zeros((component_num, component_num))

            # matrix data dict
            mat_ij_dict: Dict[str, str | float | int | None] = {}

            # looping through component names
            for i in range(component_num):
                for j in range(component_num):
                    # key
                    key = f"{components[i]}_{components[j]}"
                    prop_ = f"{property_name}_{key}"
                    # get matrix property
                    matrix_property = self.ij(prop_)

                    # set value
                    mat_ij[i][j] = matrix_property['value']

                    # set dict
                    key_dict = f"{components[i]} | {components[j]}"
                    mat_ij_dict[key_dict] = matrix_property['value']

            # check
            if mat_ij is None:
                raise Exception("Matrix data is None!")

            # return
            if symbol_format == 'alphabetic':
                return mat_ij_dict
            elif symbol_format == 'numeric':
                return mat_ij
            else:
                raise Exception("Symbol format not recognized!")
        except Exception as e:
            raise Exception("Getting matrix data failed!, ", e)

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
