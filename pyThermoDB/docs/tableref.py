# import packages/modules
import os
import pandas as pd
from typing import (
    Optional,
    Literal
)
import glob
# local
from .managedata import ManageData
from ..data import TableTypes
from ..models import PayLoadType
from .customref import CustomRef
from ..models import DataBookTableTypes


class TableReference(ManageData):
    """
    Class to load csv/yml/json files
    """

    def __init__(self, custom_ref: Optional[CustomRef] = None):
        # custom ref
        self.custom_ref = custom_ref

        # current path
        current_path = os.path.dirname(__file__)

        # Go back to the parent directory (pyThermoDB)
        parent_path = os.path.abspath(os.path.join(current_path, '..'))

        # Now navigate to the data folder
        data_path = os.path.join(parent_path, 'data')

        # Set the path to the "data" folder
        self.path = data_path
        # super
        ManageData.__init__(self, custom_ref=custom_ref)

    def load_external_csv(self, custom_ref: CustomRef) -> list[str]:
        '''
        Load external csv file paths

        Parameters
        ----------
        custom_ref : CustomRef
            custom ref
        '''
        path_external = custom_ref.csv_paths
        return path_external

    def list_databooks(self):
        '''
        list databooks
        '''
        _, df, _ = self.get_databooks()
        return df

    def list_tables(
        self,
        databook: int | str,
        res_format: Literal[
            'list', 'dataframe', 'json', 'dict'
        ] = 'dataframe'
    ) -> list[list[str]] | pd.DataFrame | str | dict[str, str]:
        '''
        List all tables in the selected databook

        Parameters
        ----------
        databook : int | str
            databook id or name
        res_format : Literal['list', 'dataframe', 'json']
            Format of the returned data. Defaults to 'dataframe'.

        Returns
        -------
        table list : list | pandas.DataFrame | str | dict[str, str]
            list of tables
        '''
        try:
            # manual databook setting
            db, db_name, db_id = self.find_databook(databook)
            # table list
            res = self.get_tables(db_name)
            # check
            if res_format == 'list':
                return res[0]
            elif res_format == 'dataframe':
                return res[1]
            elif res_format == 'json':
                return res[2]
            elif res_format == 'dict':
                return res[3]
            else:
                raise ValueError('Invalid res_format')
        except Exception as e:
            raise Exception("Table loading error!,", e)

    def load_table(
        self,
        databook_id: int,
        table_id: int
    ) -> pd.DataFrame:
        """
        Load a `csv file` from app directory or external reference
        and convert it to a pandas dataframe.
        If the table is a matrix data, it will return a dictionary of dataframes.
        If the table is a data or equations, it will return a single dataframe.

        Parameters
        ----------
        databook_id : int
            databook id (non-zero-based id)
        table_id : int
            table id (non-zero-based id)

        Returns
        -------
        pandas DataFrame
            pandas DataFrame
        """
        try:
            # init vars
            file_data = None
            file_item_data = None
            file_path = None

            # NOTE:
            # table
            tb = self.get_table(databook_id-1, table_id-1)
            # table type
            tb_type = tb['table_type']

            # table name
            table_name = tb['table']
            # table file
            file_name = table_name + '.csv'

            # check table exists in local or external references
            reference_local_no = self.reference_local_no

            # SECTION: table file path
            # local
            if databook_id <= reference_local_no:
                # set file path
                file_path = os.path.join(self.path, file_name)
            else:
                # check
                if self.custom_ref is None:
                    raise ValueError('No custom reference provided')

                # NOTE: load external path
                path_external = self.load_external_csv(self.custom_ref)

                # SECTION: check if the file exists in the external paths
                file_path = None
                # check
                if len(path_external) > 0:
                    # check csv paths
                    # csv file names
                    file_names = [
                        os.path.basename(path) for path in path_external
                    ]
                    # check csv file
                    for item in file_names:
                        if item == file_name:
                            file_path = path_external[file_names.index(item)]
                            break

                # SECTION: load values from custom reference (if exists in the yml/md file)
                # ! check both yml and md files
                if tb_type and file_path is None:
                    # load table data
                    table_data = self.retrieve_data(
                        tb, tb_type)

                    # NOTE: load structure
                    table_structure = tb.get('table_structure', None)

                    # check
                    if table_structure is None:
                        raise Exception(
                            f"Table data is None for {file_name}.")

                    # NOTE: table structure
                    columns = table_structure.get('COLUMNS', None)
                    symbol = table_structure.get('SYMBOL', None)
                    unit = table_structure.get('UNIT', None)

                    # check
                    if columns is None or symbol is None or unit is None:
                        raise Exception(
                            f"Table data is None for {file_name}.")

                    # SECTION: used by matrix data
                    # NOTE: table_values
                    values = tb.get('table_values', None)
                    # NOTE: table_items
                    items = tb.get('table_items', None)

                    # NOTE: load values
                    if tb_type == TableTypes.DATA.value:
                        # ! data & matrix data

                        # check
                        if values is None:
                            raise Exception(
                                f"Table data is None for {file_name}.")

                        # NOTE: add to file data
                        file_data = []
                        # ! add to dataframe header
                        # file_data.append(columns)
                        file_data.append(symbol)
                        file_data.append(unit)
                        file_data.extend(values)

                    elif tb_type == TableTypes.MATRIX_DATA.value:
                        # ! matrix data

                        # NOTE: values or items
                        # check
                        if values is None:
                            # check items
                            if items is None:
                                # ! raise exception as no values or items
                                raise Exception(
                                    f"Table data is None for {file_name}.")

                        # NOTE: matrix data
                        matrix_data = tb.get('matrix_data', None)
                        # check
                        if matrix_data is None:
                            raise Exception(
                                f"Table data is None for {file_name}.")

                        # matrix symbol
                        matrix_symbol = matrix_data.get('MATRIX-SYMBOL', None)

                        # check
                        if matrix_symbol is None:
                            raise Exception(
                                f"Table data is None for {file_name}.")

                        # size of matrix symbols
                        matrix_symbol_len = len(matrix_symbol)

                        # SECTION: values
                        if values and isinstance(values, list):
                            # # size of matrix symbols
                            # component_idx_len = len(values) - 2

                            # # ! No., Name, Formula are necessary for matrix data
                            # header_ = ['None', 'None', 'None']
                            # component_idx = [str(i) for i in range(
                            #     1, component_idx_len+1)]*matrix_symbol_len

                            # # updated header
                            # header_ = header_ + component_idx

                            # # updated values
                            # values_ = [header_, *values]
                            # NOTE: check columns contains Mixture
                            # check
                            if any(col.lower() == 'mixture' for col in columns):
                                # loop through values
                                for i in range(len(values)):
                                    # mixture name
                                    mixture_name = values[i][1]

                                    # split mixture name
                                    mixture_name = mixture_name.split('|')
                                    # check
                                    if len(mixture_name) != 2:
                                        raise Exception(
                                            f"Table data is None for {file_name}.")
                                    # strip keys
                                    mixture_name = [i.strip()
                                                    for i in mixture_name]
                                    # std key format
                                    mixture_name = f"{mixture_name[0]} | {mixture_name[1]}"
                                    # update values
                                    values[i][1] = mixture_name

                            values_ = [*values]

                            # NOTE: add to file data
                            file_data = []
                            # ! add to dataframe header
                            # file_data.append(columns)
                            file_data.append(symbol)
                            file_data.append(unit)
                            file_data.extend(values_)

                    elif tb_type == TableTypes.EQUATIONS.value:
                        # ! equations

                        # check
                        if values is None:
                            raise Exception(
                                f"Table data is None for {file_name}.")

                        # NOTE: make file data
                        file_data = []
                        # ! add to dataframe header
                        # file_data.append(columns)
                        file_data.append(symbol)
                        file_data.append(unit)
                        file_data.extend(values)

            # SECTION
            # check
            if file_path is not None:
                # create dataframe
                return pd.read_csv(file_path)
            elif file_data is not None and file_item_data is None:
                # create dataframe
                return pd.DataFrame(file_data, columns=columns)
            elif file_item_data is not None and file_data is None:
                # create dataframe
                # return df_dict
                raise Exception(
                    f"Table data is None for {file_name}.")
            else:
                raise Exception(f"{file_name} does not exist.")

        except FileNotFoundError:
            raise FileNotFoundError(
                f"File {file_name} not found in {self.path}")
        except Exception as e:
            raise Exception(f"Table loading error {e}")

    def search_tables(
            self,
            databook_id: int,
            table_id: int,
            column_name: str | list[str],
            lookup: str | list[str],
            query: bool = False
    ) -> pd.DataFrame:
        """
        Search tables in this directory

        Parameters
        ----------
        databook_id : int
            databook id
        Parameters
        ----------
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str
            column name
        lookup : str
            value to look up for

        Returns
        -------
        result : pandas Series
            result of search
        """
        try:
            # table type
            tb_type = self.get_table_type(databook_id, table_id)

            # dataframe
            df = None

            # check tb_type
            if (
                tb_type == TableTypes.DATA.value or
                    tb_type == TableTypes.EQUATIONS.value
            ):
                # ! search table
                df = self.search_table(
                    databook_id,
                    table_id,
                    column_name,
                    lookup,
                    query=query
                )
            elif (
                tb_type == TableTypes.MATRIX_DATA.value or
                tb_type == TableTypes.MATRIX_EQUATIONS.value
            ):
                # ! search matrix table
                df = self.search_matrix_table(
                    databook_id,
                    table_id,
                    column_name,
                    lookup,
                    query=query
                )
            else:
                raise Exception(f"Table type {tb_type} is not supported.")

            return df
        except Exception as e:
            raise Exception(f"Table searching error {e}")

    def search_table(
        self,
        databook_id: int,
        table_id: int,
        column_name: str | list,
        lookup: str | list[str],
        query: bool = False
    ) -> pd.DataFrame:
        '''
        Search inside csv file which is converted to pandas dataframe

        Parameters
        ----------
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str | list
            column name
        lookup : str
            value to look up for

        Returns
        -------
        result : pandas DataFrame
            result of search
        '''
        try:
            # SECTION: tb
            # NOTE: load table data/equations (all data)
            df = self.load_table(databook_id, table_id)

            # NOTE: check dataframe
            if isinstance(df, pd.DataFrame):
                # take first three rows
                df_info = df.iloc[:2, :]

                # SECTION: filter
                if (
                    isinstance(column_name, str) and
                    query is False
                ):  # ! search by column name
                    # NOTE: check query
                    # create filter
                    # check lookup
                    if not isinstance(lookup, str):
                        raise ValueError(
                            f"Lookup value must be a string for {databook_id} and {table_id}."
                        )

                    df_filter = df[
                        df[column_name].str.lower() == lookup.lower()
                    ]
                elif (
                    isinstance(column_name, str) and
                    query is True
                ):  # ! search by query
                    # NOTE: check query
                    # create filter
                    df_filter = df.query(column_name, engine='python')

                elif (
                    isinstance(column_name, list) and
                    isinstance(lookup, list) and
                    query is False
                ):  # ! search by list of column names
                    # NOTE: check column names
                    if len(column_name) != len(lookup):
                        raise ValueError(
                            f"Column name and lookup must have the same length for {databook_id} and {table_id}."
                        )

                    # SECTION: use query
                    # use query
                    _query = []

                    # iterate through column names
                    for i in range(len(column_name)):
                        _query.append(
                            f'{column_name[i]}.str.lower() == "{str(lookup[i]).lower()}"'
                        )

                    # make query
                    _query_set = ' and '.join(_query)

                    # NOTE: query
                    df_filter = df.query(_query_set, engine='python')
                else:
                    raise ValueError(
                        f"Column name and lookup formats are not valid for {databook_id} and {table_id}."
                    )

                # SECTION: combine dfs
                result = pd.concat([df_info, df_filter])

                # NOTE: check
                if not df_filter.empty:
                    return result
                else:
                    return pd.DataFrame()
            else:
                raise Exception(
                    f"Table data is not a pandas dataframe for {databook_id} and {table_id}.")
        except Exception as e:
            raise Exception(f"Searching table error {e}")

    def search_matrix_table(
        self,
        databook_id: int,
        table_id: int,
        column_name: str | list[str],
        lookup: str | list[str],
        query: bool = False
    ) -> pd.DataFrame:
        '''
        Search inside csv file which is converted to pandas dataframe

        Parameters
        ----------
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str
            column name
        lookup : str
            value to look up for
        query : bool, optional
            if True, then use query method, by default False

        Returns
        -------
        result : pandas Series
            result of search
        '''
        # NOTE: load tb
        df = self.load_table(databook_id, table_id)

        # NOTE: search mode
        search_mode = False

        # NOTE: check dataframe
        if isinstance(df, pd.DataFrame):
            # NOTE: search matrix table
            # filter
            if (
                isinstance(column_name, str) and
                isinstance(lookup, str) and
                    query is False
            ):
                # create filter
                df_filter = df[df[column_name].str.lower() == lookup.lower()]
            if (
                isinstance(column_name, str) and
                    isinstance(lookup, list)
            ):
                # create filter
                # df_filter = df[df[column_name].isin(lookup)]

                # set
                search_mode = True

                lookup_normalized = [str(x).strip().lower() for x in lookup]
                df_filter = df[df[column_name].str.strip(
                ).str.lower().isin(lookup_normalized)]
            # query
            elif (
                isinstance(column_name, str) and
                query is True
            ):
                # create filter
                df_filter = df.query(column_name)
            # list
            elif (
                isinstance(column_name, list) and
                isinstance(lookup, list)
            ):
                # use query
                _queries = []
                for i in range(len(column_name)):
                    _queries.append(f'`{column_name[i]}` == "{lookup[i]}"')
                # make query
                _query_set = ' & '.join(_queries)
                # query
                df_filter = df.query(_query_set)
            # else:
            #     raise ValueError(
            #         f"Column name and lookup formats are not valid.")

            # NOTE: df_filter analysis
            # check if df_filter is empty
            if df_filter.empty:
                # raise exception
                raise Exception(
                    f"No data found for {databook_id} and {table_id} with column name {column_name} and lookup {lookup}.")

            # records number
            records_number = df_filter.shape[0]

            # FIXME: take first three rows
            if records_number == 2 and search_mode == False:
                df_info = df.iloc[:4, :]
            elif records_number == 2 and search_mode == True:
                # empty df_info
                df_info = pd.DataFrame(columns=df.columns)
            elif records_number == 4:
                df_info = df.iloc[:2, :]
            else:
                df_info = df.iloc[:4, :]

            # NOTE: combine dfs
            result = pd.concat([df_info, df_filter])

            # NOTE: check
            if not df_filter.empty:
                return result
            else:
                return pd.DataFrame()
        else:
            raise Exception(
                f"Table data is not a pandas dataframe for {databook_id} and {table_id}.")

    def make_payload(
        self,
        databook_id: int,
        table_id: int,
        column_name: str | list[str],
        lookup: str | list[str],
        query: bool = False,
        matrix_tb: bool = False
    ) -> PayLoadType | None:
        '''
        Make standard data

        Parameters
        ----------
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str
            column name
        lookup : str
            value to look up for

        Returns
        -------
        payload : PayLoadType | None
            standard data

        Notes
        -----
        header: list
            header
        symbol: list
            symbol
        unit: list
            unit
        records: list
            records, if nan exists then converted to 0
        '''
        try:
            # SECTION: check
            if matrix_tb:
                df = self.search_matrix_table(
                    databook_id,
                    table_id,
                    column_name,
                    lookup=lookup,
                    query=query
                )
            else:
                df = self.search_table(
                    databook_id,
                    table_id,
                    column_name,
                    lookup=lookup,
                    query=query
                )

            # SECTION: check
            if len(df) > 0:
                # payload
                if matrix_tb:
                    records_clean = df.iloc[4, :].fillna(0).to_list()
                else:
                    records_clean = df.iloc[2, :].fillna(0).to_list()

                # payload
                payload: PayLoadType = {
                    "header": df.columns.to_list(),
                    "symbol": df.iloc[0, :].to_list(),
                    "unit": df.iloc[1, :].to_list(),
                    "records": records_clean,
                }

                # res
                return payload
            else:
                return None

        except Exception as e:
            raise Exception(f"Making payload error {e}")

    def search_component(
        self,
        search_terms: list[str],
        search_mode: str,
        column_names: list[str] = ['Name', 'Formula']
    ) -> list[dict]:
        """
        Search a component in all databooks

        Parameters
        ----------
        column_names : list
            the list of column names (default: ['Name', 'Formula'])
        search_terms : list[str]
            search terms for instance a component name or formula

        """
        try:
            # data path
            directory = self.path

            # Initialize an empty list to store results
            results = []

            # Get a list of all CSV files in the directory
            csv_files = glob.glob(directory + '/*.csv')

            # Capitalize the search terms
            search_terms = [term.upper() for term in search_terms]

            # Iterate over each CSV file
            for file in csv_files:
                try:
                    # Read the CSV file
                    df = pd.read_csv(file)

                    # Get existing column names
                    existing_columns = [col for col in column_names if col.lower() in [
                        c.lower() for c in df.columns]]

                    # Skip if no columns exist
                    if not existing_columns:
                        # print(f"No matching columns found in {file}.")
                        continue

                    # Convert existing columns to string and capitalize
                    for col in existing_columns:
                        df[col] = df[col].apply(lambda x: str(x).upper())

                    # Filter rows where any existing column matches the search term(s)
                    if len(search_terms) == 1:
                        # Search both columns with single term
                        # check search mode
                        if search_mode == 'similar':
                            matching_rows = df[df[existing_columns].apply(
                                lambda x: x.str.contains(search_terms[0])).any(axis=1)]
                        elif search_mode == 'exact':
                            matching_rows = df[df[existing_columns].eq(
                                search_terms[0]).any(axis=1)]
                        else:
                            raise ValueError(
                                f"Invalid search mode: {search_mode}")
                    else:
                        # Search specific columns with multiple terms
                        if len(existing_columns) < 2:
                            # print(f"Only one matching column found in {file}.")
                            # check search mode
                            if search_mode == 'similar':
                                matching_rows = df[df[existing_columns[0]
                                                      ].str.contains(search_terms[0])]
                            elif search_mode == 'exact':
                                matching_rows = df[df[existing_columns[0]].eq(
                                    search_terms[0])]
                            else:
                                raise ValueError(
                                    f"Invalid search mode: {search_mode}")
                        else:
                            # check search mode
                            if search_mode == 'similar':
                                matching_rows = df[
                                    (df[existing_columns[0]].str.contains(search_terms[0])) |
                                    (df[existing_columns[1]].str.contains(
                                        search_terms[1]))
                                ]
                            elif search_mode == 'exact':
                                matching_rows = df[
                                    (df[existing_columns[0]].eq(search_terms[0])) &
                                    (df[existing_columns[1]].eq(search_terms[1]))
                                ]

                            else:
                                raise ValueError(
                                    f"Invalid search mode: {search_mode}")

                    # Add results to the list if matches are found
                    if not matching_rows.empty:
                        # csv file
                        # _csv_file = file.split('/')[-1]
                        # csv file
                        _csv_file = os.path.basename(file)
                        # csv file name
                        _table_name, extension = os.path.splitext(_csv_file)
                        # get source
                        _get_source = self.find_table_source(_table_name)
                        # check
                        if not _get_source:
                            raise Exception(
                                f"Source not found for {_table_name}")

                        # source (non-zero-based id)
                        db, db_id, tb_name, tb_id, data_type = _get_source.values()

                        # table-description
                        table_description = self.get_table(db, tb_name)[
                            'description']

                        # save
                        results.append({
                            'search-mode': search_mode,
                            'search-terms': ', '.join(search_terms),
                            'databook-id': db_id,
                            'databook-name': db,
                            'table-id': tb_id,
                            'table-name': _table_name,
                            'table-description': table_description,
                            'data-type': data_type,
                        })
                except pd.errors.EmptyDataError:
                    print(f"{file} is empty.")
                except pd.errors.ParserError:
                    print(f"Error parsing {file}.")

            return results

        except Exception as e:
            raise Exception(f'Searching component error {e}')

    def list_all_components(
        self,
        column_name: str = 'Name'
    ) -> tuple[list[str], list[dict[str, str | int]]]:
        """
        List all components in all databooks.

        Returns
        -------
        components : list
            list of components
        components_info : list
            list of component information
        """
        try:
            # get all components
            components = []
            # component info
            components_info = []

            # data path
            directory = self.path

            # Get a list of all CSV files in the directory
            csv_files = glob.glob(directory + '/*.csv')

            # Iterate over each CSV file
            for file in csv_files:
                # read
                df = pd.read_csv(file)

                # get columns
                columns = df.columns.tolist()

                # check
                if len(columns) > 1:
                    # check column name
                    if column_name in columns:
                        # get component
                        component = df[column_name].tolist()

                        # csv file
                        _csv_file = os.path.basename(file)
                        # csv file name
                        _table_name, extension = os.path.splitext(_csv_file)
                        # get source
                        _get_source = self.find_table_source(_table_name)
                        # check
                        if not _get_source:
                            raise Exception(
                                f"Source not found for {_table_name}")

                        # source
                        db, db_id, tb_name, tb_id, data_type = _get_source.values()

                        # add to list
                        components.extend(component)

                        # component info
                        component_info = {
                            "component": component,
                            "databook": db,
                            "database_id": db_id,
                            "table_name": tb_name,
                            "table_id": tb_id,
                            "data_type": data_type
                        }
                        components_info.append(component_info)

            return components, components_info

        except Exception as e:
            raise Exception(f'Listing all components error {e}')

    def retrieve_data(
            self,
            table_data: DataBookTableTypes,
            table_type: str):
        '''
        Retrieve data from table data based on table type

        Parameters
        ----------
        table_data : Dict
            table data
        table_type : str
            table type
                - data
                - equations
                - matrix-data
                - matrix-equations

        Returns
        -------
        data : list
            data
        '''
        try:
            # check table type
            if table_type == TableTypes.DATA.value:
                # data
                data = table_data['data']
            elif table_type == TableTypes.EQUATIONS.value:
                # data
                data = table_data['equations']
            elif table_type == TableTypes.MATRIX_DATA.value:
                # data
                data = table_data['matrix_data']
            elif table_type == TableTypes.MATRIX_EQUATIONS.value:
                # data
                data = table_data['matrix_equations']
            else:
                raise Exception(f"Table type {table_type} is not supported.")

            # check
            if data is None:
                raise Exception(f"Table data is None.")

            # res
            return data
        except Exception as e:
            raise Exception(f"Retrieving data error {e}")
