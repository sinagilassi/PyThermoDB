# import packages/modules
import os
import pandas as pd
# local
from .managedata import ManageData


class TableReference(ManageData):
    """
    Class to load excel files in this directory
    """

    def __init__(self, custom_ref=None):
        # custom ref
        self.custom_ref = custom_ref

        # Get the absolute path of the current file
        # current_file_path = os.path.realpath(__file__)

        # Get the directory of the current file
        # current_dir = os.path.dirname(current_file_path)

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

    def load_external_csv(self, custom_ref):
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

    def list_tables(self, databook_id):
        '''
        List tables
        '''
        _, df = self.get_tables(databook_id-1)
        return df

    def load_table(self, databook_id, table_id):
        """
        Load a csv file in this directory

        Parameters
        ----------
        databook_id : int
            databook id
        table_id : int
            table id

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
            file_path = os.path.join(self.path, file_name)
        else:
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

    def search_table(self, databook_id, table_id, column_name, lookup, query=False):
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

    def make_payload(self, databook_id, table_id, column_name, lookup,
                     query=False):
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
        payload : dict
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
        # dataframe
        df = self.search_table(databook_id, table_id,
                               column_name, lookup, query=query)
        # check
        if len(df) > 0:
            # payload
            # records
            records_clean = df.iloc[2, :].fillna(0).to_list()
            payload = {
                "header": df.columns.to_list(),
                "symbol": df.iloc[0, :].to_list(),
                "unit": df.iloc[1, :].to_list(),
                "records": records_clean,
            }
        else:
            payload = {}
        # res
        return payload
