# import packages/modules
import pandas as pd
import math
import sympy as sp
# local
from .equationbuilder import EquationBuilder


class TableEquation:
    # vars
    body = ''
    parms = {}
    args = {}
    returns = {}
    body_integral = ''
    body_first_derivative = ''
    body_second_derivative = ''
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
            equation id (from 1 to ...)

        Returns
        -------
        eq_summary : dict
            equation summary
        '''
        try:
            # set id
            id = int(id)-1
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
            # check if exist
            _body_integral = equation.get('BODY-INTEGRAL', None)
            _body_first_derivative = equation.get(
                'BODY-FIRST-DERIVATIVE', None)
            _body_second_derivative = equation.get(
                'BODY-SECOND-DERIVATIVE', None)

            # eq summary
            eq_summary = {
                'id': id,
                'body': _body,
                'args': _args,
                'parms': _parms,
                'return': _return,
                'body_integral': _body_integral,
                'body_first_derivative': _body_first_derivative,
                'body_second_derivative': _body_second_derivative
            }
            return eq_summary
        except Exception as e:
            raise Exception(f'Loading error {e}!')

    def cal(self, sympy_format=False, **args):
        '''
        Execute a function

        Parameters
        ----------
        args : dict
            a dictionary contains variable names and values as

        Returns
        -------
        res : float
            calculation result

        Examples
        --------
        >>> res = cal(T=120,P=1)
        >>> print(res)
        '''
        # build parms dict
        _parms = self.load_parms()
        # execute equation
        # check
        if sympy_format:
            res = self.eqExe_sympy(self.body, _parms, args=args)
        else:
            res = self.eqExe(self.body, _parms, args=args)
        return res

    def cal_integral(self, **args):
        '''
        Calculate integral

        Parameters
        ----------
        args : dict
            a dictionary contains variable names and values

        Returns
        -------
        res : float
            calculation result

        Examples
        --------
        >>> res = cal_integral(T=120,P=1)
        >>> print(res)
        '''
        # build parms dict
        _parms = self.load_parms()
        # execute equation
        res = self.eqExe(self.body_integral, _parms, args=args)
        return res

    def cal_first_derivative(self, **args):
        '''
        Calculate first derivative

        Parameters
        ----------
        args : dict
            a dictionary contains variable names and values

        Returns
        -------
        res : float
            calculation result

        Examples
        --------
        >>> res = cal_first_derivative(T=120,P=1)
        >>> print(res)
        '''
        # build parms dict
        _parms = self.load_parms()
        # execute equation
        res = self.eqExe(self.body_first_derivative, _parms, args=args)
        return res

    def cal_second_derivative(self, **args):
        '''
        Calculate second derivative

        Parameters
        ----------
        args : dict
            a dictionary contains variable names and values

        Returns
        -------
        res : float
            calculation result

        Examples
        --------
        >>> res = cal_second_derivative(T=120,P=1)
        >>> print(res)
        '''
        # build parms dict
        _parms = self.load_parms()
        # execute equation
        res = self.eqExe(self.body_second_derivative, _parms, args=args)
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

    def equation_parms(self, dataframe=True):
        '''
        Display equation parms

        Parameters
        ----------
        value : bool, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        df : dataframe
            equation parms
        '''
        df = pd.DataFrame(self.parms)

        if dataframe:
            return df
        else:
            return self.parms

    def equation_args(self, dataframe=True):
        '''
        Display equation args,

        Parameters
        ----------
        value : bool, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        df : dataframe
            equation args
        '''
        df = pd.DataFrame(self.args)

        if dataframe:
            return df
        else:
            return self.args

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
        df = pd.DataFrame(self.returns)

        if dataframe:
            return df
        else:
            return self.returns

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
        Eq_data = int(transform_api_data['Eq']['value'])

        # load equation
        eq_summary = self.eq_structure(Eq_data)

        # extract data
        _body = eq_summary['body']
        self.body = ';'.join(_body)
        # check
        if eq_summary['parms'] is not None:
            self.parms = eq_summary['parms']
        else:
            self.parms = []
        # check
        if eq_summary['args'] is not None:
            self.args = eq_summary['args']
        else:
            self.args = []
        # check
        if eq_summary['return'] is not None:
            self.returns = eq_summary['return']
        else:
            self.returns = []
        # integral
        body_integral = eq_summary['body_integral']
        self.body_integral = ";".join(body_integral)
        # first derivative
        first_derivative = eq_summary['body_first_derivative']
        self.body_first_derivative = ";".join(first_derivative)
        # second derivative
        second_derivative = eq_summary['body_second_derivative']
        self.body_second_derivative = ";".join(second_derivative)

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

    def eqExe_sympy(self, body, parms, args):
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
        # str input
        str_input = []
        # std body
        body = body.replace("res =", "")
        body = body.replace("res=", "")
        body = body.strip()
        # check
        if self.args is not None:
            # check list
            for key, value in self.args.items():
                if 'symbol' in value:
                    symbol = value['symbol']
                    str_input.append(symbol)
        # check
        if self.parms is not None:
            for key, value in self.parms.items():
                if 'symbol' in value:
                    symbol = value['symbol']
                    str_input.append(symbol)

        # convert to string
        str_input = ' '.join(str_input)
        # init EquationBuilder
        eq_builder = EquationBuilder(str_input)
        # all parameters and variables
        all_parms = {**parms, **args}
        # execute equation
        res = eq_builder.evaluate_expression(body, **all_parms)
        return res
