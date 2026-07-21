# import libs
import logging
import pandas as pd
import numpy as np
from typing import Optional, Any, Literal, Dict, List
from warnings import warn
from pythermodb_settings.models import ComponentKey, Component
# local
from ..handlers import (
    TableMatrixDataConversionError,
    TableMatrixDataDefinitionError,
    TableMatrixDataError,
    TableMatrixDataFormatError,
    TableMatrixDataFrameError,
    TableMatrixDataGenerationError,
    TableMatrixDataLookupError,
    TableMatrixDataStructureError,
)
from ..models import DataResultType, DataResult


# NOTE: logger
logger = logging.getLogger(__name__)


class TableMatrixData:
    # vars
    __trans_data = {}
    __prop_data = {}
    __matrix_symbol = None
    _table_structure = {}
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
    # mixture id
    mixture_id: Optional[str] = None
    # mixture idx
    mixture_ids: Optional[List[str]] = None

    def __init__(
        self,
        databook_name: str | int,
        table_name: str | int,
        table_data,
        matrix_table=None,
        matrix_symbol: Optional[List[str]] = None
    ):
        # set values
        self.databook_name = databook_name
        self.table_name = table_name
        self.table_data = table_data  # NOTE: reference template (yml)
        self.matrix_table = matrix_table  # ! all elements saved in the matrix-table

        # NOTE: check
        if matrix_symbol is None:
            # matrix symbol such as Alpha_i_j
            symbol_ = self.table_data['MATRIX-SYMBOL']

            # init
            self.__matrix_symbol = []

            # iterate through symbol_
            for item in symbol_:
                if isinstance(item, str):
                    self.__matrix_symbol.append(item)
                elif isinstance(item, dict):
                    # add values
                    for key, value in item.items():
                        self.__matrix_symbol.append(value)

            # matrix items
            items_ = self.table_data.get('ITEMS', None)
            # check
            if items_ is not None and items_ != "None":
                # setting matrix items
                self.__set_matrix_items(items_)

        # NOTE: table structure
        self._table_structure = self._generate_table_structure(self.table_data)

    def _context(self, **context):
        base_context = {
            "databook_name": self.databook_name,
            "table_name": self.table_name,
        }
        base_context.update(context)
        return base_context

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

    @property
    def table_structure(self):
        """Get table structure"""
        return self._table_structure

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
                                raise TableMatrixDataFormatError(
                                    "Matrix item key is not in the correct format",
                                    context=self._context(matrix_item_key=key),
                                )

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
            table_structure = self._table_structure
            # check
            if table_structure is None:
                raise TableMatrixDataStructureError(
                    "Table structure is None",
                    context=self._context(),
                )

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
                raise TableMatrixDataStructureError(
                    "Matrix symbol is None",
                    context=self._context(),
                )

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
                        raise TableMatrixDataFormatError(
                            "Matrix item key is not in the correct format",
                            context=self._context(matrix_item_key=key),
                        )

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
        except (TableMatrixDataFormatError, TableMatrixDataStructureError):
            raise
        except Exception as e:
            raise TableMatrixDataGenerationError(
                "Generating matrix items failed",
                context=self._context(component_names=component_names),
            ) from e

    def _generate_table_structure(self, table_data: dict[str, Any]):
        '''
        Generate table structure from data table

        Parameters
        ----------
        table_data : dict[str, Any]
            data table
        '''
        try:
            # init
            table_structure = {}
            # looping through table data
            for key, value in self.table_data.items():
                if key != 'MATRIX-SYMBOL' and key != 'ITEMS':
                    # set
                    table_structure[key] = value

            # check
            if table_structure is None:
                raise TableMatrixDataStructureError(
                    "Table structure is None",
                    context=self._context(),
                )

            # res
            return table_structure
        except TableMatrixDataStructureError:
            raise
        except Exception as e:
            raise TableMatrixDataStructureError(
                "Generating table structure failed",
                context=self._context(),
            ) from e

    def _find_component_prop_data(
            self,
            component_id: str,
    ):
        '''
        Get a component property from data table structure

        Parameters
        ----------
        component_id : str
            component id

        Returns
        -------
        value : dict
            component property
        '''
        try:
            # SECTION: check component id availability
            if component_id is None or component_id.strip() == "":
                logger.error("Component id is empty!")
                return {}

            # NOTE: prop_data_pack keys
            prop_data_pack_keys = list(self.prop_data_pack.keys())
            # >> check exact match
            if component_id not in prop_data_pack_keys:
                # >> check case insensitive match
                matched_keys = [
                    key for key in prop_data_pack_keys if key.lower() == component_id.lower()
                ]
                if len(matched_keys) == 0:
                    logger.error(
                        f"Component id '{component_id}' not found in property data pack!")
                    return {}
                else:
                    # set component id to matched key
                    component_id = matched_keys[0]

            # SECTION: find component property
            # exclude key
            exclude_key = 'matrix-data'

            # init
            prop_data = {}

            # NOTE: looping through self.prop_data_pack
            for component_id_, component_value in self.prop_data_pack.items():
                if component_id_ == component_id:
                    # check value
                    prop_data = {
                        key: value for key, value in component_value.items() if key != exclude_key
                    }
                    return prop_data
            # check
            if len(prop_data) == 0:
                return {}

        except Exception as e:
            raise TableMatrixDataLookupError(
                "Finding component property failed",
                context=self._context(component_id=component_id),
            ) from e

    def _fid_component_prop_data_from_mixture(
            self,
            component_id: str,
            mixture_id: str,
            column_name: str
    ):
        '''
        Get a component property from data table structure based on mixture from data table

        Parameters
        ----------
        component_id : str
            component id
        mixture_id : str
            mixture id
        column_name : str
            column name
        '''
        pass

    def _get_matrix_data_info(self):
        '''
        Get matrix data info
        '''
        try:
            # NOTE: matrix structure
            table_structure = self._table_structure

            # check
            if table_structure is None:
                logger.error("Table structure is None!")
                return {
                    'COLUMNS': None,
                    'SYMBOL': None,
                    'UNIT': None
                }

            # extract
            columns = table_structure.get('COLUMNS', None)
            symbol = table_structure.get('SYMBOL', None)
            unit = table_structure.get('UNIT', None)

            # res
            return {
                'COLUMNS': columns,
                'SYMBOL': symbol,
                'UNIT': unit
            }
        except Exception as e:
            raise TableMatrixDataStructureError(
                "Getting matrix data header failed",
                context=self._context(),
            ) from e

    def matrix_data_structure(self):
        '''
        Display matrix-data table structure
        '''
        try:
            # NOTE: choose from table data structure all except matrix-symbol
            # dataframe
            df = pd.DataFrame(self._table_structure)
            # add ID column
            df.insert(0, 'ID', range(1, len(df) + 1))
            # arrange columns
            # change the position of ID column to the last
            cols = df.columns.tolist()
            cols.insert(len(cols), cols.pop(cols.index('ID')))
            df = df[cols]

            return df
        except Exception as e:
            raise TableMatrixDataStructureError(
                "Matrix data structure failed",
                context=self._context(),
            ) from e

    def get_matrix_table(
        self,
        mode: Literal[
            'all', 'selected'
        ] = 'all'
    ) -> pd.DataFrame:
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
                raise TableMatrixDataLookupError(
                    "Matrix table is None",
                    context=self._context(mode=mode),
                )

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
                    raise TableMatrixDataLookupError(
                        "Selected records are None",
                        context=self._context(mode=mode),
                    )

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
                raise TableMatrixDataDefinitionError(
                    "Mode not recognized",
                    context=self._context(mode=mode),
                )
        except (
            TableMatrixDataDefinitionError,
            TableMatrixDataLookupError,
        ):
            raise
        except Exception as e:
            raise TableMatrixDataLookupError(
                "Getting matrix table failed",
                context=self._context(mode=mode),
            ) from e

    def _get_component_data_from_mixture_table(
        self,
        component_id: str,
        mixture_name: str,
        component_column_id: str,
        mixture_column_id: str,
    ):
        '''
        Retrieve component data from mixture table based on component id and mixture id

        Parameters
        ----------
        component_id : str
            component id
        mixture_name : str
            mixture name
        component_column_id : str
            component column name
        mixture_column_id : str
            mixture column name

        Returns
        -------
        dict
            component data
        '''
        try:
            # NOTE: check matrix mode
            if self.matrix_mode == 'ITEMS':
                # SECTION: check matrix items
                # matrix_table = self.__generate_table_items(component_names)
                raise TableMatrixDataDefinitionError(
                    "Matrix items are not available! Please use the matrix table instead!",
                    context=self._context(matrix_mode=self.matrix_mode),
                )

            elif self.matrix_mode == 'VALUES':
                # SECTION: matrix structure (all data)
                # ! load matrix table
                matrix_table = self.matrix_table
            else:
                raise TableMatrixDataDefinitionError(
                    "Matrix mode is not recognized",
                    context=self._context(matrix_mode=self.matrix_mode),
                )

            # ! check dataframe
            if not isinstance(matrix_table, pd.DataFrame):
                raise TableMatrixDataFrameError(
                    "Matrix data is not a dataframe",
                    context=self._context(matrix_mode=self.matrix_mode),
                )

            # >> column name
            matrix_table_column_name = list(matrix_table.columns)
            # to str
            matrix_table_column_name_str = ", ".join(matrix_table_column_name)

            # >> check column name exists
            if component_column_id not in matrix_table_column_name:
                raise TableMatrixDataStructureError(
                    f"Column name '{component_column_id}' not found in matrix table as {matrix_table_column_name_str}!",
                    context=self._context(column_name=component_column_id),
                )

            if mixture_column_id not in matrix_table_column_name:
                raise TableMatrixDataStructureError(
                    f"Column name '{mixture_column_id}' not found in matrix table as {matrix_table_column_name_str}!",
                    context=self._context(column_name=mixture_column_id),
                )

            # SECTION: check columns names
            # Function to normalize mixtures
            def normalize_mixture(mix):
                parts = [x.strip() for x in mix.split('|')]
                parts.sort()
                return ' | '.join(parts)

            # SECTION: mixture
            # >> if 'Mixture' column exists, filter rows based on mixture_name
            if any(
                col.lower() == 'mixture' for col in matrix_table_column_name
            ):
                # sorted
                mixture_name = normalize_mixture(mixture_name)

                # build dataframe for the mixture
                # NOTE: Extract header + row1 + row2
                header_rows = matrix_table.iloc[:2]  # row 0 and 1

                # NOTE: Normalize the 'Mixture' column for comparison
                matrix_table['normalized_mixture'] = matrix_table[mixture_column_id].apply(
                    normalize_mixture
                )

                # NOTE: Filter rows where 'mixture' == specific_name
                filtered_rows = matrix_table[
                    matrix_table['normalized_mixture'] == mixture_name
                ]

                # Combine into new DataFrame
                # (remove duplicates if overlap with header_rows)
                matrix_table = pd.concat(
                    [header_rows, filtered_rows]
                ).drop_duplicates().reset_index(drop=True)

                # drop the normalized_mixture column
                matrix_table = matrix_table.drop(
                    columns=['normalized_mixture'])
            else:
                # log
                logger.info("No 'Mixture' column found in the matrix table.")

            # SECTION: find component data
            # >> check component id availability
            if component_id is None or component_id.strip() == "":
                logger.error("Component id is empty!")
                return {}

            # SECTION: component names
            # load all component names in Name column
            comp_i = 1
            matrix_table_component = {}
            # looping through Name column
            for i, item in enumerate(list(matrix_table[component_column_id])):
                # check item is a component name
                if (
                    item != "-" and
                    len(item) > 1 and
                    item != 'None' and
                    item != 'None'
                ):
                    matrix_table_component[item] = comp_i
                    comp_i += 1

            # component names
            matrix_table_component_no = len(matrix_table_component)

            # matrix table component keys
            matrix_table_component_names = list(matrix_table_component.keys())

            # SECTION: get component data (row)
            matrix_table_comp_data = {}

            # looping through component
            for i in range(matrix_table_component_no):
                # define filter for component
                component_name_filter = matrix_table_component_names[i]

                # check component name matches component id
                if component_name_filter.lower() != component_id.lower():
                    continue

                # NOTE: get component data
                _data_get = matrix_table[
                    matrix_table[component_column_id].str.match(
                        component_name_filter,
                        case=False,
                        na=False
                    )
                ]

                # set
                _row_index = int(_data_get.index[0])
                _data = _data_get.to_dict(orient='records')[0]

                # update
                _data['row_index'] = _row_index

                # check
                if len(_data) == 0:
                    raise TableMatrixDataLookupError(
                        "No data for component: " + component_name_filter,
                        context=self._context(
                            component_id=component_name_filter),
                    )

                # get component data
                _component_name = _data[component_column_id]
                matrix_table_comp_data[_component_name] = _data

            # NOTE: check
            if len(matrix_table_comp_data) == 0:
                logger.error(
                    f"Component id '{component_id}' not found in matrix table!")
                return {}

            # SECTION: config: add symbol and unit to each property
            # NOTE: matrix data info
            matrix_data_info = self._get_matrix_data_info()
            # >> check
            if matrix_data_info is None:
                raise TableMatrixDataStructureError(
                    "Matrix data info is None",
                    context=self._context(),
                )

            # >> extract
            matrix_data_columns = matrix_data_info.get('COLUMNS', [])
            matrix_data_symbol = matrix_data_info.get('SYMBOL', [])
            matrix_data_unit = matrix_data_info.get('UNIT', [])

            # >> check
            if matrix_data_columns is None or len(matrix_data_columns) == 0:
                raise TableMatrixDataStructureError(
                    "Matrix data columns is None or empty",
                    context=self._context(field="COLUMNS"),
                )
            if matrix_data_symbol is None or len(matrix_data_symbol) == 0:
                raise TableMatrixDataStructureError(
                    "Matrix data symbol is None or empty",
                    context=self._context(field="SYMBOL"),
                )
            if matrix_data_unit is None or len(matrix_data_unit) == 0:
                raise TableMatrixDataStructureError(
                    "Matrix data unit is None or empty",
                    context=self._context(field="UNIT"),
                )

            # looping through matrix_table_comp_data
            for comp_name, comp_data in matrix_table_comp_data.items():
                # looping through columns
                for col in matrix_data_columns:
                    # check column exists in comp_data
                    if col in comp_data.keys():
                        # get index
                        col_index = matrix_data_columns.index(col)
                        # set symbol and unit
                        symbol = matrix_data_symbol[col_index] if col_index < len(
                            matrix_data_symbol) else ''
                        unit = matrix_data_unit[col_index] if col_index < len(
                            matrix_data_unit) else ''

                        # update comp_data
                        comp_data[col] = {
                            'value': comp_data[col],
                            'unit': unit,
                            'symbol': symbol,
                        }

                # update
                matrix_table_comp_data[comp_name] = comp_data

            # res
            return matrix_table_comp_data.get(component_id, {})
        except (
            TableMatrixDataDefinitionError,
            TableMatrixDataFrameError,
            TableMatrixDataLookupError,
            TableMatrixDataStructureError,
        ):
            raise
        except Exception as e:
            raise TableMatrixDataLookupError(
                "Getting component data from mixture table failed",
                context=self._context(
                    component_id=component_id,
                    mixture_name=mixture_name,
                ),
            ) from e

    def get_property(
        self,
        property: str | int,
        component_name: str,
        mixture_name: Optional[str] = None,
        component_key: Literal['Name', 'Formula'] = 'Name',
        mixture_column: str = 'Mixture',
    ) -> DataResultType | dict:
        '''
        Get a component property from data table structure

        Parameters
        ----------
        property : str | int
            property name or id
        component_name : str
            component name
        mixture_name : str, optional
            mixture name (default is None)
        component_key : Literal['Name', 'Formula']
            component key Name or Formula (default: Name)
        mixture_column : str
            mixture column name (default: Mixture)

        Returns
        -------
        dict
            component property

        Notes
        -----
        - property can be a string or an integer
        - if property is a string, it can be a property name or symbol
        - if property is an integer, it is the column index (1-based)
        - component_name is the name of the component to look for in the data table
        - the function returns a dictionary with the property data
        - if the property is not found, an empty dictionary is returned

        Table structure example:

        Non-randomness parameters of the NRTL equation:

        | No. | Name     | Formula | Alpha_i_1 | Alpha_i_2 | Alpha_i_3 | Beta_i_1 | Beta_i_2 | Beta_i_3 | Delta_i_1 | Delta_i_2 | Delta_i_3 |
        |-----|----------|---------|-----------|-----------|-----------|----------|----------|----------|-----------|-----------|-----------|
        | 1   | methanol | CH3OH   | 0         | 0.3       | -1.709    | 0        | 1        | 2        | 0         | 10        | 20        |
        | 2   | ethanol  | C2H5OH  | 0.3       | 0         | 0.569     | 3        | 0        | 4        | 30        | 0         | 40        |
        | 3   | benzene  | C6H6    | 11.58     | -0.916    | 0         | 5        | 6        | 0        | 50        | 60        | 0         |

        Example
        -------
        >>> get_property('Alpha_i_1', 'ethanol')
        {'value': 0.3, 'unit': '', 'symbol': 'Alpha_i_1', 'description': 'Non-randomness parameter Alpha_i_1'}
        >>> get_property(4, 'ethanol')
        {'value': 0.3, 'unit': '', 'symbol': 'Alpha_i_1', 'description': 'Non-randomness parameter Alpha_i_1'}
        >>> get_property('Alpha_i_1', 'ethanol', mixture_name='methanol | ethanol', component_key='Name-State', mixture_key='Name')
        {'value': 0.3, 'unit': '', 'symbol': 'Alpha_i_1', 'description': 'Non-randomness parameter Alpha_i_1'}

        '''
        # REVIEW
        # SECTION: find component property
        if mixture_name is not None:
            # set column name
            if mixture_column is None:
                # set column name
                mixture_column = 'Mixture'

            # ! build prop data from matrix data
            prop_data = self._get_component_data_from_mixture_table(
                component_id=component_name,
                mixture_name=mixture_name,
                component_column_id=component_key,
                mixture_column_id=mixture_column
            )
        else:
            # ! build prop data from prop_data_pack
            prop_data = self._find_component_prop_data(
                component_id=component_name
            )

        # >> check
        if prop_data is None or len(prop_data) == 0:
            logger.error(
                f"Component '{component_name}' property data not found!")
            return {}
        # >> check
        if not isinstance(prop_data, dict):
            raise TableMatrixDataDefinitionError(
                "Component property data is not a dictionary",
                context=self._context(component_name=component_name),
            )

        # NOTE: dataframe (selected component data)
        df = pd.DataFrame(prop_data)

        # NOTE: prop keys
        prop_keys = list(prop_data.keys())

        # >> init
        get_data = {}

        # SECTION: choose a column
        if isinstance(property, str):
            # df = df[property_name]
            # look up prop_data dict
            # check key exists
            if property in prop_data.keys():
                get_data = prop_data[property]  # return dict
            else:
                # check symbol value in each item
                for key, value in prop_data.items():
                    # check symbol key
                    if 'symbol' in prop_keys:
                        if property == value['symbol']:
                            get_data = prop_data[key]
                            break
                    elif 'Symbol' in prop_keys:
                        if property == value['Symbol']:
                            get_data = prop_data[key]
                            break
                    else:
                        continue

            # << log empty data
            if len(get_data) == 0:
                logger.warning(
                    f"Property '{property}' not found for component '{component_name}' while searching in `symbol` or `Symbol` keys!")

            # >> res
            return get_data
        elif isinstance(property, int):
            # get column index
            column_index = df.columns[property-1]
            sr: pd.Series = df.loc[:, column_index]

            # set
            get_data = sr.to_dict()

            # empty data
            if len(get_data) == 0:
                logger.warning(
                    f"Property index '{property}' not found for component '{component_name}'!")

            return get_data

        else:
            # logger
            logger.error("Property must be a string or an integer!")
            return {}

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
                raise TableMatrixDataFormatError(
                    "Invalid property name. Please use the following format: Alpha_ij (i,j are component names) such as Alpha_ethanol_methanol",
                    context=self._context(property=property),
                )

            # extract data
            prop_name, comp1, comp2 = property.split('_')

            # set property name
            prop_name = prop_name.strip()+'_i_j'

            # get matrix property
            matrix_property = self.get_matrix_property(
                prop_name, [comp1, comp2])

            return matrix_property
        except TableMatrixDataError:
            raise
        except Exception as e:
            raise TableMatrixDataLookupError(
                "Getting matrix property failed",
                context=self._context(property=property),
            ) from e

    def ij(
        self,
        property: str,
        symbol_format: Literal[
            'alphabetic', 'numeric'
        ] = 'alphabetic',
        message: Optional[str] = None,
        **kwargs
    ) -> DataResult:
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
        **kwargs : dict
            additional arguments
            - mixture_name: str

        Returns
        -------
        matrix_property: DataResult
            component property taken from matrix data
        '''
        try:
            # check property name
            # check not empty
            if property is None or property.strip() == "":
                raise TableMatrixDataFormatError(
                    "Property name is empty",
                    context=self._context(property=property),
                )

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
                    raise TableMatrixDataFormatError(
                        "Invalid property name. It should have three parts, Please use the following format: Alpha_ij (i,j are component names) such as Alpha_ethanol_methanol",
                        context=self._context(property=property),
                    )

            # NOTE: check all extracted
            if prop_name is None or comp1 is None or comp2 is None:
                raise TableMatrixDataFormatError(
                    "Property name is not in the correct format",
                    context=self._context(property=property),
                )

            # trim
            prop_name = prop_name.strip()
            comp1 = comp1.strip()
            comp2 = comp2.strip()

            # set property name
            prop_name = prop_name+'_i_j'

            # set message
            if message is None:
                message = f"Get {prop_name} property from matrix data table structure"

            # NOTE: set mixture name
            # mixture name
            mixture_name = kwargs.get('mixture_name', None)
            # check
            if mixture_name is None:
                mixture_name = f"{comp1} | {comp2}"

            # get matrix property
            matrix_property = self.get_matrix_property(
                property=prop_name,
                component_names=[comp1, comp2],
                symbol_format=symbol_format,
                message=message,
                mixture_name=mixture_name
            )

            return matrix_property
        except TableMatrixDataError:
            raise
        except Exception as e:
            raise TableMatrixDataLookupError(
                "Getting matrix property failed",
                context=self._context(property=property),
            ) from e

    def get_matrix_property(
        self,
        property: str,
        component_names: list[str],
        symbol_format: Literal[
            'alphabetic', 'numeric'
        ] = 'alphabetic',
        component_key: Literal['Name'] = 'Name',
        message: str = 'Get a component property from data table structure',
        **kwargs
    ) -> DataResult:
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
        component_key : Literal['Name']
            component key Name or Formula (default: Name)
        message : str
            message (default: None)
        **kwargs : dict
            additional arguments
            - mixture_name: str, mixture name

        Returns
        -------
        DataResult
            component property

        Notes
        -----
        - property must be a string as: Alpha_ij (i,j are component names) such as `Alpha_ethanol_methanol`
        - component_names is a list of component names such as ['ethanol', 'methanol']
        - symbol_format is either 'alphabetic' or 'numeric' (default: 'alphabetic')
        - component_key is either 'Name' or 'Formula' (default: 'Name')
        - the function returns a DataResult object with the property data
        - if the property is not found, an empty DataResult object is returned with a warning message
        - the function supports two formats for the property name:
          1. `Alpha_ij` where `i` and `j` are component names separated by an underscore
          2. `Alpha | component1 | component2` where `component1` and `component2` are component names separated by a pipe (`|`)

        The matrix data table structure is as follows:

        - Format 1 (matrix format):

        | No. | Name     | Formula | Alpha_i_1 | Alpha_i_2 | Alpha_i_3 | Beta_i_1 | Beta_i_2 | Beta_i_3 | Delta_i_1 | Delta_i_2 | Delta_i_3 |
        |-----|----------|---------|-----------|-----------|-----------|----------|----------|----------|-----------|-----------|-----------|
        | 1   | methanol | CH3OH   | 0         | 0.3       | -1.709    | 0        | 1        | 2        | 0         | 10        | 20        |
        | 2   | ethanol  | C2H5OH  | 0.3       | 0         | 0.569     | 3        | 0        | 4        | 30        | 0         | 40        |
        | 3   | benzene  | C6H6    | 11.58     | -0.916    | 0         | 5        | 6        | 0        | 50        | 60        | 0         |

        - Format 2 (matrix items format):

        | No. | Mixture          | Name     | Formula | State | a_i_1 | a_i_2 | b_i_1      | b_i_2 | c_i_1     | c_i_2 | alpha_i_1  | alpha_i_2 |
        |-----|------------------|----------|---------|-------|-------|-------|------------|-------|-----------|-------|------------|-----------|
        | 1   | methanol\\|ethanol | methanol | CH3OH   | l     | 0     | 1     | 1.564200272 | 0     | 35.05450323 | 0     | 4.481683583 |
        | 2   | methanol\\|ethanol | ethanol  | C2H5OH  | l     | 2     | 3     | -20.63243601| 0     | 0.059982839 | 0     | 4.481683583 |
        | 1   | methanol\\|methane | methanol | CH3OH   | l     | 1     | 0.300492719 | 0     | 1.564200272 | 0     | 35.05450323 | 0     | 4.481683583 |
        | 2   | methanol\\|methane | methane  | CH4     | g     | 0.380229054 | 0     | -20.63243601| 0     | 0.059982839 | 0     | 4.481683583 | 0     |

        '''
        # NOTE: mixture_components
        mixture_name = kwargs.get('mixture_name', None)

        # NOTE: get mixture id
        # mixture_id = self.mixture_id

        # NOTE: selected columns based on component_key
        if component_key not in ['Name']:
            raise TableMatrixDataDefinitionError(
                "component_key must be 'Name'!",
                context=self._context(component_key=component_key),
            )

        # >> selected column
        selected_column = component_key

        # NOTE: check matrix mode
        if self.matrix_mode == 'ITEMS':
            # SECTION: check matrix items
            # matrix_table = self.__generate_table_items(component_names)
            raise TableMatrixDataDefinitionError(
                "Matrix items are not available! Please use the matrix table instead!",
                context=self._context(matrix_mode=self.matrix_mode),
            )

        elif self.matrix_mode == 'VALUES':
            # SECTION: matrix structure (all data)
            # ! load matrix table
            matrix_table_source = self.matrix_table
            if not isinstance(matrix_table_source, pd.DataFrame):
                raise TableMatrixDataFrameError(
                    "Matrix data is not a dataframe",
                    context=self._context(matrix_mode=self.matrix_mode),
                )
            matrix_table = matrix_table_source.copy()
        else:
            raise TableMatrixDataDefinitionError(
                "Matrix mode is not recognized",
                context=self._context(matrix_mode=self.matrix_mode),
            )

        # ! check dataframe
        if not isinstance(matrix_table, pd.DataFrame):
            raise TableMatrixDataFrameError(
                "Matrix data is not a dataframe",
                context=self._context(matrix_mode=self.matrix_mode),
            )

        # >> column name
        matrix_table_column_name = list(matrix_table.columns)

        # SECTION: check columns names
        # Function to normalize mixtures
        def normalize_mixture(mix):
            parts = [x.strip() for x in mix.split('|')]
            parts.sort()
            return ' | '.join(parts)

        # SECTION: mixture
        # >> if 'Mixture' column exists, filter rows based on mixture_name
        if any(
            col.lower() == 'mixture' for col in matrix_table_column_name
        ):
            # NOTE: check
            if mixture_name is None:
                # set
                mixture_name = " | ".join(component_names)

            # sorted
            mixture_name = normalize_mixture(mixture_name)

            # build dataframe for the mixture
            # NOTE: Extract header + row1 + row2
            header_rows = matrix_table.iloc[:2]  # row 0 and 1

            # NOTE: Normalize the 'Mixture' column for comparison
            matrix_table['normalized_mixture'] = matrix_table['Mixture'].apply(
                normalize_mixture
            )

            # NOTE: Filter rows where 'mixture' == specific_name
            filtered_rows = matrix_table[
                matrix_table['normalized_mixture'] == mixture_name
            ]

            # Combine into new DataFrame
            # (remove duplicates if overlap with header_rows)
            matrix_table = pd.concat(
                [header_rows, filtered_rows]
            ).drop_duplicates().reset_index(drop=True)

            # drop the normalized_mixture column
            matrix_table = matrix_table.drop(columns=['normalized_mixture'])
        else:
            # log
            logger.info("No 'Mixture' column found in the matrix table.")

        # log
        # print(f"Matrix table shape: {matrix_table.shape}")
        # print(matrix_table)

        # SECTION: component names
        # load all component names in Name column
        comp_i = 1
        matrix_table_component = {}
        # looping through Name column
        for i, item in enumerate(list(matrix_table[selected_column])):
            # check item is a component name
            if (
                item != "-" and
                len(item) > 1 and
                item != 'None' and
                item != 'None'
            ):
                matrix_table_component[item] = comp_i
                comp_i += 1

        # component names
        matrix_table_component_no = len(matrix_table_component)

        # matrix table component keys
        matrix_table_component_names = list(matrix_table_component.keys())

        # SECTION: get component data (row)
        matrix_table_comp_data = {}
        # looping through component
        for i in range(matrix_table_component_no):
            # define filter for component
            component_name_filter = matrix_table_component_names[i]

            # NOTE: get component data
            _data_get = matrix_table[
                matrix_table[selected_column].str.match(
                    component_name_filter,
                    case=False,
                    na=False
                )
            ]

            # set
            _row_index = int(_data_get.index[0])
            _data = _data_get.to_dict(orient='records')[0]

            # update
            _data['row_index'] = _row_index

            # check
            if len(_data) == 0:
                raise TableMatrixDataLookupError(
                    "No data for component: " + component_name_filter,
                    context=self._context(
                        component_name=component_name_filter),
                )

            # get component data
            _component_name = _data[selected_column]
            matrix_table_comp_data[_component_name] = _data

        # SECTION: manage property
        if (
            isinstance(property, str) and
            property.endswith('_i_j')
        ):
            # ! find the columns
            _property = property.split('_')
            property_name = _property[0]

            # matrix columns
            matrix_columns = []
            # matrix column index
            matrix_column_index = []

            # SECTION: matrix data info
            # matrix_data_info = self._get_matrix_data_info()
            # ! check property name availability
            property_names_available = False
            # std column names (without _i_j)
            matrix_table_column_name_std = [
                col.split('_')[0] for col in matrix_table_column_name
            ]

            # iterate through std column names
            for col in matrix_table_column_name_std:
                if property_name.upper() == col.upper():  # ! exact match
                    property_names_available = True
                    break

            if not property_names_available:
                logger.warning(
                    f"Property name '{property_name}' not found in matrix table columns!"
                )
                return {
                    "property_name": str(property_name),
                    "symbol": str("N/A"),
                    "unit": str("N/A"),
                    "value": float(-1),
                    "message": f"Property name '{property_name}' not found in matrix table columns!",
                    "databook_name": self.databook_name,
                    "table_name": self.table_name
                }

            # SECTION: look for the property name in the column names
            for column in matrix_table_column_name:
                # column name set
                column_set = column.split('_')[0]
                # >> check
                # ! case insensitive
                if property_name.upper() == column_set.upper():  # ! exact match
                    # get the column index
                    column_index = matrix_table_column_name.index(column)
                    # get the column
                    matrix_columns.append(column)
                    # get the column index
                    matrix_column_index.append(column_index)

            # >> check matrix columns
            if len(matrix_columns) != matrix_table_component_no:
                raise TableMatrixDataStructureError(
                    "Matrix columns do not match the number of components",
                    context=self._context(property=property),
                )
            # >> check matrix column index
            if len(matrix_column_index) != matrix_table_component_no:
                raise TableMatrixDataStructureError(
                    "Matrix column index does not match the number of components",
                    context=self._context(property=property),
                )

            # NOTE: property value
            comp1_index = matrix_table_component[component_names[0]] - 1
            comp2_index = matrix_table_component[component_names[1]] - 1

            # row index component 1
            row_index_comp1 = matrix_table_comp_data[component_names[0]].get(
                'row_index'
            )
            # row index component 2
            row_index_comp2 = matrix_table_comp_data[component_names[1]].get(
                'row_index'
            )

            # property column
            property_column = matrix_columns[comp2_index]
            # get index
            property_column_index = matrix_column_index[comp2_index]

            # NOTE: get property value
            property_value = matrix_table.iat[
                row_index_comp1,
                property_column_index
            ]
            # >> check empty
            if pd.isna(property_value) or str(property_value).lower() == "none":
                # log
                logger.warning(
                    f"Property value for '{property}' is empty, setting to -1.")
                property_value = -1
            # >> check type
            if not isinstance(property_value, (int, float, str)):
                # log
                logger.warning(
                    f"Property value '{property_value}' is not a number, setting to -1.")
                property_value = -1

            # NOTE: get property symbol
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
                raise TableMatrixDataFormatError(
                    f"Symbol format {symbol_format} not recognized.",
                    context=self._context(symbol_format=symbol_format),
                )

            # NOTE: get property unit
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
            raise TableMatrixDataFormatError(
                f"Property format {property} not recognized.",
                context=self._context(property=property),
            )

    def ijs(
        self,
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

        Notes
        -----
        - property must be a string as: Alpha_ij (i,j are component names) such as `Alpha_ethanol_methanol` or `Alpha | ethanol | methanol`
        - res_format is the result format (default: dict)
        - symbol_delimiter is the symbol delimiter (default: |), array element symbol delimiter
        - the function returns a dictionary with the ij property
        - if the property is not found, an empty dictionary is returned
        '''
        try:
            # NOTE: property name
            if (
                property is None or
                property.strip() == ""
            ):
                raise TableMatrixDataFormatError(
                    "Property name is empty",
                    context=self._context(property=property),
                )

            # extract data
            # NOTE: format 1: Alpha_ij (i,j are component names) such as `Alpha_ethanol_methanol`
            # check contains underscore
            extracted = property.strip().split('_')

            # NOTE: check len
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
                    raise TableMatrixDataFormatError(
                        "Invalid property name. It should have three parts, Please use the following format: Alpha_ij (i,j are component names) such as Alpha_ethanol_methanol",
                        context=self._context(property=property),
                    )

            # NOTE: check all extracted
            if prop_name is None or comp1 is None or comp2 is None:
                raise TableMatrixDataFormatError(
                    "Property name is not in the correct format",
                    context=self._context(property=property),
                )

            # check
            if comp1 == comp2:
                raise TableMatrixDataFormatError(
                    "Component names are the same",
                    context=self._context(property=property),
                )

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
                logger.error("Symbol delimiter not recognized!")
                raise TableMatrixDataFormatError(
                    "Symbol delimiter not recognized",
                    context=self._context(symbol_delimiter=symbol_delimiter),
                )

            # NOTE: define mixture
            # mixture name
            mixture_name = f"{components[0]} | {components[1]}"

            # SECTION: extract data
            for i in range(len(components)):
                for j in range(len(components)):
                    # key
                    key = f"{components[i]}_{components[j]}"
                    prop_ = f"{prop_name}_{key}"

                    # get property
                    val = self.ij(
                        prop_,
                        mixture_name=mixture_name
                    ).get('value')

                    # set
                    key_comp = f"{components[i]}{symbol_delimiter_set}{components[j]}"
                    res_dict[key_comp] = val
                    res_array[i][j] = val

            # NOTE: check
            if res_format == 'alphabetic':
                # >> convert to alphabetic format
                return res_dict
            elif res_format == 'numeric':
                # >> convert to numeric format
                return res_array
            else:
                raise TableMatrixDataFormatError(
                    "Result format not recognized",
                    context=self._context(res_format=res_format),
                )

        except TableMatrixDataError:
            raise
        except Exception as e:
            raise TableMatrixDataGenerationError(
                "Generating dictionary failed",
                context=self._context(property=property),
            ) from e

    @staticmethod
    def _normalize_mixture_name(mixture_name: str) -> str:
        '''
        Normalize a mixture name by trimming and alphabetically sorting parts.
        '''
        parts = [str(item).strip() for item in str(mixture_name).split('|')]
        parts = [item for item in parts if item]
        parts.sort(key=str.lower)
        return ' | '.join(parts)

    @staticmethod
    def _is_component_row(value: Any) -> bool:
        '''
        Check if a matrix-table row value represents a component identifier.
        '''
        value_set = str(value).strip()
        return (
            value_set != "" and
            value_set != "-" and
            value_set.lower() != "none" and
            value_set.lower() != "nan"
        )

    def get_component_ids(
        self,
        component_names: list[str],
    ) -> Dict[str, int]:
        '''
        Assign zero-based ids to a component-name list.

        Parameters
        ----------
        component_names : list[str]
            Component names in the requested matrix order.

        Returns
        -------
        Dict[str, int]
            Component name to zero-based id mapping.
        '''
        try:
            if component_names is None or len(component_names) == 0:
                raise TableMatrixDataFormatError(
                    "Component names are empty",
                    context=self._context(component_names=component_names),
                )

            components = [str(name).strip() for name in component_names]
            if any(name == "" for name in components):
                raise TableMatrixDataFormatError(
                    "Component names contain an empty value",
                    context=self._context(component_names=component_names),
                )

            if len(set(name.lower() for name in components)) != len(components):
                raise TableMatrixDataFormatError(
                    "Component names contain duplicates",
                    context=self._context(component_names=component_names),
                )

            return {
                component_name: component_id
                for component_id, component_name in enumerate(components)
            }
        except TableMatrixDataError:
            raise
        except Exception as e:
            raise TableMatrixDataLookupError(
                "Getting component ids failed",
                context=self._context(component_names=component_names),
            ) from e

    def get_matrix_rows(
        self,
        component_names: list[str],
        component_key: Literal['Name'] = 'Name',
        mixture_column: str = 'Mixture',
    ) -> pd.DataFrame:
        '''
        Get matrix-table data rows matching a component-name list.

        For binary-pair encoded mixture tables, this returns all rows whose
        mixture is one of the component pairs. For regular square matrix tables,
        this returns rows whose component key is in `component_names`.

        Parameters
        ----------
        component_names : list[str]
            Component names to include in the matrix.
        component_key : Literal['Name']
            Component column name (default: Name).
        mixture_column : str
            Mixture column name for binary-pair encoded tables (default:
            Mixture).

        Returns
        -------
        pd.DataFrame
            Matrix-table data rows for the selected components.
        '''
        try:
            if component_key not in ['Name']:
                raise TableMatrixDataDefinitionError(
                    "component_key must be 'Name'!",
                    context=self._context(component_key=component_key),
                )

            matrix_table_source = self.matrix_table
            if not isinstance(matrix_table_source, pd.DataFrame):
                raise TableMatrixDataFrameError(
                    "Matrix data is not a dataframe",
                    context=self._context(),
                )

            component_ids = self.get_component_ids(component_names)
            components = list(component_ids.keys())
            components_lower = {component.lower() for component in components}

            matrix_table = matrix_table_source.copy()
            matrix_table = matrix_table.drop(
                columns=[
                    column
                    for column in ['normalized_mixture', '_normalized_mixture']
                    if column in matrix_table.columns
                ]
            )
            matrix_table_columns = list(matrix_table.columns)

            if component_key not in matrix_table_columns:
                raise TableMatrixDataStructureError(
                    f"Component column '{component_key}' not found",
                    context=self._context(component_key=component_key),
                )

            data_rows = matrix_table[
                matrix_table[component_key].apply(self._is_component_row)
            ].copy()

            data_rows = data_rows[
                data_rows[component_key].astype(str).str.strip().str.lower().isin(
                    components_lower
                )
            ].copy()

            if mixture_column in matrix_table_columns:
                pair_names = set()
                for i, component_i in enumerate(components):
                    for j, component_j in enumerate(components):
                        if i == j:
                            continue
                        pair_names.add(
                            self._normalize_mixture_name(
                                f"{component_i} | {component_j}"
                            )
                        )

                data_rows['_normalized_mixture'] = data_rows[
                    mixture_column
                ].apply(self._normalize_mixture_name)
                data_rows = data_rows[
                    data_rows['_normalized_mixture'].isin(pair_names)
                ].drop(columns=['_normalized_mixture'])

            return data_rows.reset_index(drop=True)
        except TableMatrixDataError:
            raise
        except Exception as e:
            raise TableMatrixDataLookupError(
                "Getting matrix rows failed",
                context=self._context(component_names=component_names),
            ) from e

    @staticmethod
    def _matrix_value(value: Any) -> float:
        '''
        Convert a matrix-table value to a float.
        '''
        if (
            pd.isna(value) or
            str(value).lower() == "none"
        ):
            return float(-1)
        return float(value)

    @staticmethod
    def _matrix_dict(
        components: list[str],
    ) -> Dict[str, str | float | int]:
        '''
        Initialize a component-wise matrix dictionary.
        '''
        return {
            f"{component_i} | {component_j}": 0
            for component_i in components
            for component_j in components
        }

    @staticmethod
    def _component_key_columns(
        component_key: ComponentKey,
    ) -> list[str]:
        '''
        Get matrix-table columns required to build a component label.
        '''
        if component_key == 'Name':
            return ['Name']
        if component_key == 'Formula':
            return ['Formula']
        if component_key == 'Name-State':
            return ['Name', 'State']
        if component_key == 'Formula-State':
            return ['Formula', 'State']
        if component_key == 'Name-Formula':
            return ['Name', 'Formula']
        if component_key == 'Name-Formula-State':
            return ['Name', 'Formula', 'State']
        if component_key == 'Formula-Name-State':
            return ['Formula', 'Name', 'State']

        raise TableMatrixDataFormatError(
            f"Component key {component_key} not recognized."
        )

    @classmethod
    def _component_label(
        cls,
        row: dict[str, Any],
        component_key: ComponentKey,
    ) -> str:
        '''
        Build a component label from a matrix-table row.
        '''
        columns = cls._component_key_columns(component_key)
        values = [str(row[column]).strip() for column in columns]
        return '-'.join(values)

    def _matrix_component_labels(
        self,
        components: list[str],
        matrix_rows: pd.DataFrame,
        component_key: ComponentKey,
    ) -> dict[str, str]:
        '''
        Build display labels for component-wise matrix dictionary keys.
        '''
        required_columns = self._component_key_columns(component_key)
        missing_columns = [
            column
            for column in required_columns
            if column not in matrix_rows.columns
        ]
        if len(missing_columns) > 0:
            raise TableMatrixDataStructureError(
                f"Matrix table is missing columns for component_key "
                f"{component_key}: {missing_columns}",
                context=self._context(component_key=component_key),
            )

        component_rows = {}
        for _, row in matrix_rows.iterrows():
            component_name = str(row['Name']).strip()
            if component_name not in component_rows:
                component_rows[component_name] = row.to_dict()

        labels = {}
        for component_name in components:
            if component_name not in component_rows:
                raise TableMatrixDataLookupError(
                    f"Component '{component_name}' row not found",
                    context=self._context(component_name=component_name),
                )
            labels[component_name] = self._component_label(
                component_rows[component_name],
                component_key,
            )

        return labels

    @staticmethod
    def _matrix_result_dict(
        components: list[str],
        component_labels: dict[str, str],
        mat_ij: np.ndarray,
    ) -> Dict[str, str | float | int]:
        '''
        Build a matrix dictionary from display labels and matrix values.
        '''
        return {
            f"{component_labels[component_i]} | {component_labels[component_j]}": (
                float(mat_ij[i][j])
            )
            for i, component_i in enumerate(components)
            for j, component_j in enumerate(components)
        }

    @staticmethod
    def _matrix_property_columns(
        property_name: str,
        matrix_columns: list[str],
    ) -> list[str]:
        '''
        Get matrix columns that belong to a property name.
        '''
        return [
            column
            for column in matrix_columns
            if str(column).split('_')[0].lower() == property_name.lower()
        ]

    def _matrix_table_source(self) -> pd.DataFrame:
        '''
        Get the stored matrix table as a DataFrame.
        '''
        matrix_table_source = self.matrix_table
        if not isinstance(matrix_table_source, pd.DataFrame):
            raise TableMatrixDataFrameError(
                "Matrix data is not a dataframe",
                context=self._context(),
            )
        return matrix_table_source.copy()

    def _matrix_table_component_order(self) -> list[str]:
        '''
        Get component order from a full square matrix table.
        '''
        matrix_table = self._matrix_table_source()
        matrix_table = matrix_table.drop(
            columns=[
                column
                for column in ['normalized_mixture', '_normalized_mixture']
                if column in matrix_table.columns
            ]
        )

        return [
            str(item).strip()
            for item in list(matrix_table['Name'])
            if self._is_component_row(item)
        ]

    def _fill_pair_matrix(
        self,
        mat_ij: np.ndarray,
        mat_ij_dict: Dict[str, str | float | int],
        matrix_rows: pd.DataFrame,
        property_columns: list[str],
        component_ids: Dict[str, int],
    ) -> None:
        '''
        Fill matrix values from a binary-pair encoded matrix table.
        '''
        for _, row in matrix_rows.iterrows():
            source_component = str(row['Name']).strip()
            if source_component not in component_ids:
                continue

            source_id = component_ids[source_component]
            mixture_components = [
                item.strip()
                for item in str(row['Mixture']).split('|')
            ]

            for property_column in property_columns:
                try:
                    target_local_id = int(
                        str(property_column).split('_')[-1]
                    ) - 1
                except ValueError:
                    continue

                if target_local_id >= len(mixture_components):
                    continue

                target_component = mixture_components[target_local_id]
                if target_component not in component_ids:
                    continue

                target_id = component_ids[target_component]
                property_value = self._matrix_value(row[property_column])

                mat_ij[source_id][target_id] = property_value
                mat_ij_dict[
                    f"{source_component} | {target_component}"
                ] = property_value

    def _fill_square_matrix(
        self,
        mat_ij: np.ndarray,
        mat_ij_dict: Dict[str, str | float | int],
        matrix_rows: pd.DataFrame,
        property_columns: list[str],
        component_ids: Dict[str, int],
    ) -> None:
        '''
        Fill matrix values from a full square matrix table.
        '''
        table_component_order = self._matrix_table_component_order()

        for _, row in matrix_rows.iterrows():
            source_component = str(row['Name']).strip()
            if source_component not in component_ids:
                continue

            source_id = component_ids[source_component]

            for property_column in property_columns:
                try:
                    target_id = int(
                        str(property_column).split('_')[-1]
                    ) - 1
                except ValueError:
                    continue

                if target_id >= len(table_component_order):
                    continue

                target_component = table_component_order[target_id]
                if target_component not in component_ids:
                    continue

                target_output_id = component_ids[target_component]
                property_value = self._matrix_value(row[property_column])

                mat_ij[source_id][target_output_id] = property_value
                mat_ij_dict[
                    f"{source_component} | {target_component}"
                ] = property_value

    def mat(
        self,
        property_name: str,
        component_names: list[str],
        symbol_format: Literal[
            'alphabetic', 'numeric'
        ] = 'numeric',
        component_key: ComponentKey = 'Name',
    ) -> Dict[str, str | float | int] | np.ndarray:
        '''
        Get matrix data from matrix data table structure (2x2, 3x3, ...)

        Parameters
        ----------
        property_name : str
            property name such as `Alpha` represented `Alpha_ij`
        component_names : list[str]
            component names such as ['ethanol', 'methanol']
        symbol_format : str
            symbol format alphabetic or numeric (default: numeric)
        component_key : ComponentKey
            Component label format used for alphabetic dictionary keys
            (default: Name). Supported values include Name, Formula,
            Name-State, Formula-State, Name-Formula, Name-Formula-State,
            and Formula-Name-State.

        Returns
        -------
        dict | np.ndarray
            matrix data (dict or np.ndarray)

        Notes
        -----
        - property_name must be a string as: Alpha (i,j are component names) such as `Alpha`
        - component_names is a list of component names such as ['ethanol', 'methanol']
        - the function returns a dictionary or numpy array with the matrix data
        '''
        try:
            # NOTE: check property name
            # check not empty
            if property_name is None or property_name.strip() == "":
                raise TableMatrixDataFormatError(
                    "Property name is empty",
                    context=self._context(property_name=property_name),
                )
            # set
            property_name = property_name.strip()
            # remove _i_j
            property_name = property_name.replace('_i_j', '')

            # NOTE: check component names
            if component_names is None or len(component_names) == 0:
                raise TableMatrixDataFormatError(
                    "Component names are empty",
                    context=self._context(component_names=component_names),
                )
            # component num
            component_num = len(component_names)

            # component strip
            components = [name.strip() for name in component_names]
            component_ids = self.get_component_ids(components)

            # NOTE: matrix data
            mat_ij = np.zeros((component_num, component_num))

            # matrix data dict
            mat_ij_dict = self._matrix_dict(components)

            matrix_rows = self.get_matrix_rows(components)

            if len(matrix_rows) == 0:
                raise TableMatrixDataLookupError(
                    "No matrix rows found for component names",
                    context=self._context(component_names=component_names),
                )

            matrix_columns = list(matrix_rows.columns)
            property_columns = self._matrix_property_columns(
                property_name,
                matrix_columns,
            )

            if len(property_columns) == 0:
                logger.warning(
                    f"Property name '{property_name}' not found in matrix table columns!"
                )
                mat_ij[:, :] = -1
                for key in mat_ij_dict:
                    mat_ij_dict[key] = -1
            elif 'Mixture' in matrix_columns:
                self._fill_pair_matrix(
                    mat_ij=mat_ij,
                    mat_ij_dict=mat_ij_dict,
                    matrix_rows=matrix_rows,
                    property_columns=property_columns,
                    component_ids=component_ids,
                )
            else:
                self._fill_square_matrix(
                    mat_ij=mat_ij,
                    mat_ij_dict=mat_ij_dict,
                    matrix_rows=matrix_rows,
                    property_columns=property_columns,
                    component_ids=component_ids,
                )

            # NOTE: check
            if (
                mat_ij is None or
                mat_ij_dict is None
            ):
                # log
                logger.error("Matrix data is None!")
                return {}

            # NOTE: return
            if symbol_format == 'alphabetic':
                component_labels = self._matrix_component_labels(
                    components,
                    matrix_rows,
                    component_key,
                )
                mat_ij_dict = self._matrix_result_dict(
                    components,
                    component_labels,
                    mat_ij,
                )
                return mat_ij_dict
            elif symbol_format == 'numeric':
                return mat_ij
            else:
                raise TableMatrixDataFormatError(
                    f"Symbol format {symbol_format} not recognized.",
                    context=self._context(symbol_format=symbol_format),
                )
        except TableMatrixDataError:
            raise
        except Exception as e:
            raise TableMatrixDataLookupError(
                "Getting matrix data failed",
                context=self._context(
                    property_name=property_name,
                    component_names=component_names,
                ),
            ) from e

    def matX(
        self,
        property_name: str,
        components: List[Component],
        symbol_format: Literal[
            'alphabetic', 'numeric'
        ] = 'numeric',
        component_key: ComponentKey = 'Name',
    ) -> Dict[str, str | float | int] | np.ndarray:
        '''
        Get matrix data using Component objects.

        Parameters
        ----------
        property_name : str
            Property name such as `Alpha` represented `Alpha_ij`.
        components : List[Component]
            Components in the requested matrix order.
        symbol_format : str
            Result format, alphabetic dictionary or numeric array
            (default: numeric).
        component_key : ComponentKey
            Component label format used for alphabetic dictionary keys
            (default: Name).

        Returns
        -------
        dict | np.ndarray
            Matrix data.
        '''
        try:
            if components is None or len(components) == 0:
                raise TableMatrixDataFormatError(
                    "Components are empty",
                    context=self._context(components=components),
                )

            if not all(isinstance(component, Component) for component in components):
                raise TableMatrixDataFormatError(
                    "All components must be Component instances",
                    context=self._context(components=components),
                )

            component_names = [
                component.name.strip()
                for component in components
            ]

            return self.mat(
                property_name=property_name,
                component_names=component_names,
                symbol_format=symbol_format,
                component_key=component_key,
            )
        except TableMatrixDataError:
            raise
        except Exception as e:
            raise TableMatrixDataLookupError(
                "Getting matrix data using Component objects failed",
                context=self._context(
                    property_name=property_name,
                    components=components,
                ),
            ) from e

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
            raise TableMatrixDataConversionError(
                "Conversion failed",
                context=self._context(),
            ) from e
