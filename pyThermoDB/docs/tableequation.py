# import packages/modules
import pandas as pd
import math
import sympy as sp


class TableEquation:
    # vars
    body = ''
    parms = []
    args = []
    res = []
    __trans_data = {}

    def __init__(self, table_name, equations):
        self.table_name = table_name
        self.equations = equations

    @property
    def trans_data(self):
        return self.__trans_data

    @trans_data.setter
    def trans_data(self, value):
        self.__trans_data = {}
        self.__trans_data = value

    def eq_structure(self, id):
        '''
        Display equation details

        Parameters
        ----------
        id : int
            equation id (fromm 0 to ...)

        Returns
        -------
        eq_summary : dict
            equation summary
        '''
        try:
            # equation id
            equation = self.equations[id]
            # equation body
            _body = equation['BODY']
            # equation args
            _args = equation['ARGS']
            # equation params
            _parms = equation['PARMS']
            # equation src
            _return = equation['RETURNS']

            # eq summary
            eq_summary = {
                'id': id,
                'body': _body,
                'args': _args,
                'parms': _parms,
                'return': _return
            }
            return eq_summary
        except Exception as e:
            raise Exception(f'Loading error {e}!')

    def cal(self, args):
        '''
        Execute a function

        Parameters
        ----------
        args : dict
            a dictionary contains variable names and values as: args = {"T": 120, "P": 1}


        Returns
        -------
        res : float
            calculation result
        '''
        # build parms dict
        _parms = self.load_parms()
        # execute equation
        res = self.eqExe(self.body, _parms, args=args)
        return res

    def cal_integral(self, args):
        '''
        Calculate integral

        Parameters
        ----------
        args : dict
            a dictionary contains variable names and values as: args = {"T": 120, "P": 1}

        Returns
        -------
        res : float
            calculation result
        '''
        # build parms dict
        _parms = self.load_parms()
        # execute equation
        res = self.eqExe_integral(self.body, _parms, args=args)
        return res

    def load_parms(self):
        '''
        Load parms values and store in a dict, 
        These parameters are constant values defined in an equation.
        '''
        # trans data
        trans_data = self.trans_data
        # looping through self.parms
        # check parms
        if isinstance(self.parms, dict):
            _parms_name = list(self.parms.keys())
            _parms = {key: float(value['value'] or 0)/float(value['unit'] or 1)
                      for key, value in trans_data.items() if key in _parms_name}
        else:
            _parms = {}
        return _parms

    def equation_body(self):
        '''
        Display equation body

        Parameters
        ----------
        None

        Returns
        -------
        body : str
            equation body
        '''
        return self.body

    def equation_parms(self, dataframe=False):
        '''
        Display equation parms

        Parameters
        ----------
        value : bool, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        df : dataframe
            equation parms
        '''
        df = pd.DataFrame(self.parms)

        if dataframe:
            return df
        else:
            return None

    def equation_args(self, dataframe=False):
        '''
        Display equation args,

        Parameters
        ----------
        value : bool, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        df : dataframe
            equation args
        '''
        df = pd.DataFrame(self.args)

        if dataframe:
            return df
        else:
            return None

    def equation_return(self, dataframe=True):
        '''
        Display equation return,

        Parameters
        ----------
        value : bool, optional
            DESCRIPTION. The default is True.


        Returns
        -------
        df : dataframe
            equation return
        '''
        df = pd.DataFrame(self.res)

        if dataframe:
            return df
        else:
            return None

    def eqSet(self):
        '''
        Set the equation used for calculation

        Parameters
        ----------
        transform_api_data : dict
            transform api data

        Returns
        -------
        None.
        '''
        # set
        transform_api_data = self.trans_data

        # eq
        Eq_data = 0
        Eq_data = int(transform_api_data['Eq']['value'])-1

        # load equation
        eq_summary = self.eq_structure(Eq_data)

        # extract data
        _body = eq_summary['body']
        self.body = ';'.join(_body)
        self.parms = eq_summary['parms']
        self.args = eq_summary['args']
        self.res = eq_summary['return']

    def eqExe(self, body, parms, args):
        '''
        Execute the function having args, parameters and body

        Parameters
        ----------
        body : str
            function body
        parms : dict
            parameters
        args : dict
            args

        Returns
        -------
        res : float
            calculation result
        '''
        # Define a namespace dictionary for eval
        namespace = {'args': args, "parms": parms}
        # Import math module within the function
        namespace['math'] = math
        # Execute the body within the namespace
        exec(body, namespace)
        # Return the result
        return namespace['res']

    def eqExe_integral(self, body, parms, args):
        '''
        Execute the integral of a function having args, parameters and body

        Parameters
        ----------
        body : str
            function body
        parms : dict
            parameters
        args : dict
            args

        Returns
        -------
        res : float
            calculation result
        '''
        # Define a namespace dictionary for eval
        namespace = {'args': args, "parms": parms}
        # Import math module within the function
        namespace['math'] = math
        # Execute the body within the namespace
        exec(body, namespace)
        # Return the result
        res = namespace['res']

        # Convert the result to a sympy expression
        T = sp.symbols('T')  # Define a symbolic variable
        expr = sp.sympify(res)  # Convert the result to a sympy expression

        # lower bound
        Tmin = args['Tmin']
        # upper bound
        Tmax = args['Tmax']
        # Calculate the definite integral
        integral = sp.integrate(expr, (T, Tmin, Tmax))

        # return
        return integral
