# import packages/modules
# external
import pandas as pd
import math
# internal
from pyThermoDB.config import THERMODYNAMICS_DATABOOK 

class TransData:
    '''
    transform data
    '''
    def __init__(self, api_data, src):
        self.api_data = api_data
        self.src = src
        # eq id
        self.eq_id = -1
        self.function = ''
        self.parms = []
        self.args = []
        self.res = []
        
    def trans(self):
        '''
        step 1: display api data
            data['header'],['records'],['unit']
        step 2: transform to dict 
        '''
        data_trans = {}

        for x,y,z in zip(self.api_data['header'], self.api_data['records'], self.api_data['unit']):
            # check eq exists
            if x == "Eq":
                self.eq_id = y
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
        
    def eq(self):
        '''
        equation used for calculation
        '''
        # equation id
        if self.eq_id == -1:
            return 'no equation exists!'
        else:
            eq = [item for item in self.src['equations'] if item['id'] == self.eq_id][0]
            # extract data
            self.function = eq['function']
            self.parms = eq['parms']
            self.args = eq['args']
            self.res = eq['return']
            # build eq
            
            return eq['function']
        
    def eqExe(self, body, parms, args):
        # Define a namespace dictionary for eval
        namespace = {'args': args, "parms": parms}
        # Import math module within the function
        namespace['math'] = math
        # Execute the body within the namespace
        exec(body, namespace)
        # Return the result
        return namespace['res']