# import packages/modules
import os
import pandas as pd
from typing import Optional
import glob
# local
from .managedata import ManageData
from ..data import TableTypes
from ..models import PayLoadType
from .customref import CustomRef


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
        _, df = self.get_databooks()
        return df

    def list_tables(self, databook_id: int) -> pd.DataFrame:
        '''
        List tables

        Parameters
        ----------
        databook_id : int
            databook id
        '''
        _, df = self.get_tables(databook_id-1)
        return df

    def load_table(self, databook_id: int, table_id: int) -> pd.DataFrame:
        """
        Load a `csv file` in this directory

        Parameters
        ----------
        databook_id : int
            databook id (non-zero-based id)
        table_id : int
            table id (non-zero-based id)

        Returns
        -------
        df : pandas DataFrame
            dataframe of excel file
        """
        # table
        tb = self.get_table(databook_id-1, table_id-1)
        # table name
        table_name = tb['table']
        # table file
        file_name = table_name + '.csv'

        # check table exists in local or external references
        reference_local_no = self.reference_local_no

        # table file path
        # local
        if databook_id <= reference_local_no:
            # set file path
            file_path = os.path.join(self.path, file_name)
        else:
            # check
            if self.custom_ref is None:
                raise ValueError('No custom reference provided')
            # load external path
            path_external = self.load_external_csv(self.custom_ref)
            # csv file names
            file_names = [os.path.basename(path) for path in path_external]
            # check csv file
            for item in file_names:
                if item == file_name:
                    file_path = path_external[file_names.index(item)]
                    break
            # check
            if file_path is None:
                raise Exception(f"{file_name} does not exist.")
        # create dataframe
        df = pd.read_csv(file_path)
        return df

    def search_tables(self, databook_id: int, table_id: int, column_name: str | list[str], lookup: str | list[str], query: bool = False) -> pd.DataFrame:
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
            if tb_type == TableTypes.DATA.value or tb_type == TableTypes.EQUATIONS.value:
                df = self.search_table(databook_id, table_id,
                                       column_name, lookup, query=query)
            elif tb_type == TableTypes.MATRIX_DATA.value or tb_type == TableTypes.MATRIX_EQUATIONS.value:
                df = self.search_matrix_table(databook_id, table_id,
                                              column_name, lookup, query=query)
            else:
                raise Exception(f"Table type {tb_type} is not supported.")

            return df
        except Exception as e:
            raise Exception(f"Table searching error {e}")

    def search_table(self, databook_id: int, table_id: int, column_name: str | list, lookup: str, query: bool = False) -> pd.DataFrame:
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
        # tb
        df = self.load_table(databook_id, table_id)
        # take first three rows
        df_info = df.iloc[:2, :]
        # filter
        if isinstance(column_name, str) and query is False:
            # create filter
            df_filter = df[df[column_name].str.lower() == lookup.lower()]
        # query
        elif isinstance(column_name, str) and query is True:
            # create filter
            df_filter = df.query(column_name)
        # list
        elif isinstance(column_name, list) and isinstance(lookup, list):
            # use query
            _querys = []
            for i in range(len(column_name)):
                _querys.append(f'`{column_name[i]}` == "{lookup[i]}"')
            # make query
            _query_set = ' & '.join(_querys)
            # query
            df_filter = df.query(_query_set)

            # combine dfs
        result = pd.concat([df_info, df_filter])
        if not df_filter.empty:
            return result
        else:
            return pd.DataFrame()

    def search_matrix_table(self, databook_id: int, table_id: int, column_name: str | list[str], lookup: str, query: bool = False) -> pd.DataFrame:
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

        Returns
        -------
        result : pandas Series
            result of search
        '''
        # tb
        df = self.load_table(databook_id, table_id)
        # take first three rows
        df_info = df.iloc[:4, :]

        # search matrix table
        # filter
        if isinstance(column_name, str) and query is False:
            # create filter
            df_filter = df[df[column_name].str.lower() == lookup.lower()]
        # query
        elif isinstance(column_name, str) and query is True:
            # create filter
            df_filter = df.query(column_name)
        # list
        elif isinstance(column_name, list) and isinstance(lookup, list):
            # use query
            _querys = []
            for i in range(len(column_name)):
                _querys.append(f'`{column_name[i]}` == "{lookup[i]}"')
            # make query
            _query_set = ' & '.join(_querys)
            # query
            df_filter = df.query(_query_set)

            # combine dfs
        result = pd.concat([df_info, df_filter])
        if not df_filter.empty:
            return result
        else:
            return pd.DataFrame()

    def make_payload(self, databook_id: int, table_id: int, column_name: str | list[str], lookup: str,
                     query: bool = False, matrix_tb: bool = False) -> PayLoadType | None:
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
            # check
            if matrix_tb:
                df = self.search_matrix_table(databook_id, table_id,
                                              column_name, lookup=lookup, query=query)
            else:
                df = self.search_table(databook_id, table_id,
                                       column_name, lookup=lookup, query=query)
            # check
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

    def search_component(self, search_terms: list[str], column_names: list[str] = ['Name', 'Formula']):
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
                        print(f"No matching columns found in {file}.")
                        continue

                    # Convert existing columns to string and capitalize
                    for col in existing_columns:
                        df[col] = df[col].apply(lambda x: str(x).upper())

                    # Filter rows where any existing column matches the search term(s)
                    if len(search_terms) == 1:
                        # Search both columns with single term
                        matching_rows = df[df[existing_columns].apply(
                            lambda x: x.str.contains(search_terms[0])).any(axis=1)]
                    else:
                        # Search specific columns with multiple terms
                        if len(existing_columns) < 2:
                            # print(f"Only one matching column found in {file}.")
                            matching_rows = df[df[existing_columns[0]
                                                  ].str.contains(search_terms[0])]
                        else:
                            matching_rows = df[
                                (df[existing_columns[0]].str.contains(search_terms[0])) |
                                (df[existing_columns[1]].str.contains(
                                    search_terms[1]))
                            ]

                    # Add results to the list if matches are found
                    if not matching_rows.empty:
                        results.append({
                            # Get only the file name
                            'file_name': file.split('/')[-1],
                            'matching_rows': matching_rows
                        })
                except pd.errors.EmptyDataError:
                    print(f"{file} is empty.")
                except pd.errors.ParserError:
                    print(f"Error parsing {file}.")

            return results

        except Exception as e:
            raise Exception(f'Searching component error {e}')
