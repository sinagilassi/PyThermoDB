# import packages/modules
# external
import pandas as pd
import math
# internal


class TransData:
    '''
    Transform class
    '''

    def __init__(self, api_data):
        self.api_data = api_data
        self.data_trans = {}

    def trans(self):
        '''
        Transform the data loaded from API, 
        It consists of:
            step 1: display api data
                data['header'],['records'],['unit']
            step 2: transform to dict 
        '''
        self.data_trans = {}

        for x, y, z, w in zip(self.api_data['header'], self.api_data['records'], self.api_data['unit'], self.api_data['symbol']):
            # check eq exists
            if x == "Eq":
                self.eq_id = y
            self.data_trans[str(x)] = {"value": y, "unit": z, "symbol": w}

        # data table
        self.data_trans['data'] = self.api_data
        return self.data_trans

    def view(self, value=False):
        '''
        Display data in a table (pandas dataframe)

        args:
            value: display value
        '''
        df = pd.DataFrame(self.api_data)
        print(df)
        # check
        if value:
            return df
        else:
            return None
