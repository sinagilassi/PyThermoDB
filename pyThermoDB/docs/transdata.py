# import packages/modules
# external
import pandas as pd
import math
# internal
from ..config import THERMODYNAMICS_DATABOOK


class TransData:
    '''
    Transform class
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

    def get_prop(self, symbol):
        '''
        Choose a property, then get its value,
        This symbol is the one defined in the displayed data

        args:
            symbol {str}: property symbol (ideal gas enthalpy of formation: EnFo_IG)

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

    def equation_exe(self, args):
        '''
        Execute a function

        args:
            **args {dict}: a dictionary contains variable names and values
                args = {"T": 120, "P": 1}

        return:
            res {float}: calculation result, return value is -1 in case of errors
        '''
        if self.eq_id != -1:
            # build parms dict
            _parms = self.load_parms()
            # execute equation
            res = self.eqExe(self.body, _parms, args=args)
            return res
        else:
            print("This property has no equation.")
            return -1

    def load_parms(self):
        '''
        Load parms values and store in a dict, 
        These parameters are constant values defined in an equation.
        '''
        _parms_name = [item['name'] for item in self.parms]
        _parms = {key: float(value['value'] or 0)/float(value['unit'] or 1)
                  for key, value in self.data_trans.items() if key in _parms_name}
        return _parms

    def equation_body(self, value=False):
        '''
        Display equation body,

        args:
            value {bool}: if it is True, returns data

        return:
            equation body {str}
        '''
        if self.eq_id != -1:
            print(self.body)
        else:
            print("This property has no equation.")

        if value:
            return self.body
        else:
            return None

    def equation_parms(self, value=False):
        '''
        Display equation parms,

        args:
            value {bool}: if it is True, returns data

        return:
            equation parms {dataframe}
        '''
        if self.eq_id != -1:
            df = pd.DataFrame(self.parms)
            print(df)
        else:
            print("This property has no equation.")

        if value:
            return df
        else:
            return None

    def equation_args(self, value=False):
        '''
        Display equation args,

        args:
            value {bool}: if it is True, returns data

        return:
            equation args {dataframe}
        '''
        if self.eq_id != -1:
            df = pd.DataFrame(self.args)
            print(df)
        else:
            print("This property has no equation.")

        if value:
            return df
        else:
            return None

    def equation_return(self, value=False):
        '''
        Display equation return,

        args:
            value {bool}: if it is True, returns data

        return:
            equation return {dataframe}
        '''
        if self.eq_id != -1:
            df = pd.DataFrame(self.res)
            print(df)
        else:
            print("This property has no equation.")

        if value:
            return df
        else:
            return None

    def eqSet(self):
        '''
        Set the equation used for calculation
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
        '''
        Execute the function having args, parameters and body

        args:
            body {str}: function body
            parms {dict}: parameters
            args {dict}: args 

        return:
            res {float}: calculation result
        '''
        # Define a namespace dictionary for eval
        namespace = {'args': args, "parms": parms}
        # Import math module within the function
        namespace['math'] = math
        # Execute the body within the namespace
        exec(body, namespace)
        # Return the result
        return namespace['res']
