# import packages/modules
# external
import pandas as pd

class TransData:
    '''
    transform data
    '''
    def __init__(self, api_data):
        self.api_data = api_data
        
    def trans(self):
        '''
        step 1: display api data
            data['header'],['records'],['unit']
        step 2: transform to dict 
        '''
        data_trans = {}

        for x,y,z in zip(self.api_data['header'], self.api_data['records'], self.api_data['unit']):
            data_trans[str(x)] = {"value": y, "unit": z}
            
        # data table
        data_trans['data'] = self.api_data

        return data_trans
    
    def view(self):
        '''
        display data in a table (pandas dataframe)
        '''
        df = pd.DataFrame(self.api_data)
        print(df)