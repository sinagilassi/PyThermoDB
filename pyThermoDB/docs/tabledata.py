# import packages/modules
import pandas as pd


class TableData:
    def __init__(self, table_name, data):
        self.table_name = table_name
        self.data = data

    def sample(self):
        '''
        Return a random sample row from data
        '''
        # dataframe
        df = pd.DataFrame(self.data)
        return df.sample()
