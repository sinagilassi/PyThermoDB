# import packages/modules
import os
import pandas as pd
# local
from .managedata import ManageData


class TableReference(ManageData):
    """
    Class to load excel files in this directory
    """

    def __init__(self):
        # super
        # self.path = os.path.dirname(os.path.abspath(__file__))

        # Get the absolute path of the current file
        current_file_path = os.path.abspath(__file__)

        # Get the directory of the current file
        current_dir = os.path.dirname(current_file_path)

        # Set the path to the "data" folder
        self.path = os.path.join(current_dir, '..', 'data')
        # super
        ManageData.__init__(self)

    def list_databooks(self):

        _, df = self.get_databooks()
        return df

    def list_tables(self, databook_id):
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
        # table file path
        file_path = os.path.join(self.path, file_name)
        df = pd.read_csv(file_path)
        return df

    def search_table(self, databook_id, table_id, column_name, lookup):
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
        df_filter = df[df[column_name].str.lower() == lookup.lower()]
        # combine dfs
        result = pd.concat([df_info, df_filter])
        if not df_filter.empty:
            return result
        else:
            return pd.DataFrame()

    def make_payload(self, databook_id, table_id, column_name, lookup):
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
        '''
        # dataframe
        df = self.search_table(databook_id, table_id, column_name, lookup)
        # check
        if len(df) > 0:
            # payload
            payload = {
                "header": df.columns.to_list(),
                "symbol": df.iloc[0, :].to_list(),
                "unit": df.iloc[1, :].to_list(),
                "records": df.iloc[2, :].to_list(),
            }
        else:
            payload = {}
        # res
        return payload
