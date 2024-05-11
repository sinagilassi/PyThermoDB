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
        self.data_trans = {}
        self.src = src
        # eq id
        self.eq_id = -1
        self.body = ''
        self.parms = []
        self.args = []
        self.res = []

    def trans(self):
        '''
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

    def get_prop(self, symbol):
        '''
        choose a property, then get its value

        args:
            symbol: property symbol (ideal gas enthalpy of formation: EnFo_IG)

        return:
            property value
        '''
        _value = -1
        if len(symbol) > 0:
            # find prop
            _prop = [(value['symbol'], value['value']) for key, value in self.data_trans.items()
                     if value['symbol'] == symbol][0]
            # get value
            _symbol, _value = _prop

        return _value

    def view(self):
        '''
        display data in a table (pandas dataframe)
        '''
        df = pd.DataFrame(self.api_data)
        print(df)

    def equation_exe(self, args):
        '''
        execute function

        args:
            **args: a dictionary contains variable names and values
                args = {"T": 120, "P": 1}
        '''
        if self.eq_id != -1:
            # build parms dict
            _parms = self.load_parms()
            # execute equation
            res = self.eqExe(self.body, _parms, args=args)
            return res
        else:
            print("This property has no equation.")

    def load_parms(self):
        '''
        load parms values and store in a dict
        '''
        _parms_name = [item['name'] for item in self.parms]
        _parms = {key: float(value['value'])/float(value['unit'])
                  for key, value in self.data_trans.items() if key in _parms_name}
        return _parms

    def equation_body(self):
        '''
        display equation body
        '''
        if self.eq_id != -1:
            print(self.body)
        else:
            print("This property has no equation.")

    def equation_parms(self):
        '''
        display equation parms
        '''
        if self.eq_id != -1:
            df = pd.DataFrame(self.parms)
            print(df)
        else:
            print("This property has no equation.")

    def equation_args(self):
        '''
        display equation args
        '''
        if self.eq_id != -1:
            df = pd.DataFrame(self.args)
            print(df)
        else:
            print("This property has no equation.")

    def equation_return(self):
        '''
        display equation return
        '''
        if self.eq_id != -1:
            df = pd.DataFrame(self.res)
            print(df)
        else:
            print("This property has no equation.")

    def eqSet(self):
        '''
        equation used for calculation
        '''
        # equation id
        if self.eq_id != -1:
            # extract equation
            eq = [item for item in self.src['equations']
                  if item['id'] == self.eq_id][0]
            # extract data
            self.body = eq['function']
            self.parms = eq['parms']
            self.args = eq['args']
            self.res = eq['return']

    def eqExe(self, body, parms, args):
        # Define a namespace dictionary for eval
        namespace = {'args': args, "parms": parms}
        # Import math module within the function
        namespace['math'] = math
        # Execute the body within the namespace
        exec(body, namespace)
        # Return the result
        return namespace['res']
