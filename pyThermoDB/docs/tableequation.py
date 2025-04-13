# import packages/modules
import pandas as pd
import math
import sympy as sp
import yaml
import json
from typing import Literal, Optional, List, Dict, Any
# local
from ..models import EquationResult
from .equationbuilder import EquationBuilder
from ..utils import format_eq_data


class TableEquation:
    # vars
    body = ''
    parms = {}
    args = {}
    arg_symbols = {}
    returns = {}
    return_symbols = {}
    _summary = {}
    body_integral = ''
    body_first_derivative = ''
    body_second_derivative = ''
    __trans_data = {}
    __prop_equation = {}
    __parms_values = {}
    # custom integral
    _custom_integral = {}
    # selected equation id
    eq_id: int = -1

    def __init__(self, databook_name, table_name, equations,
                 table_values: Optional[List | Dict] = None,
                 table_structure: Optional[Dict[str, Any]] = None):
        '''
        Initialize the TableEquation class.

        Parameters
        ----------
        databook_name : str
            Name of the databook.
        table_name : str
            Name of the table.
        equations : list
            List of equations.
        table_values : list, optional
            Values for the table (default is None), if provided in yml file.
        table_structure : dict, optional
            Structure of the table (default is None), if provided in yml file.
        '''
        self.databook_name = databook_name
        self.table_name = table_name
        self.equations = equations  # equation list structures (yml file)
        # number of equations
        self.eq_num = len(equations)
        # table values (yml)
        self.__table_values = table_values if table_values else None
        # table structure (yml)
        self.__table_structure = table_structure if table_structure else None

    @property
    def trans_data(self):
        return self.__trans_data

    @trans_data.setter
    def trans_data(self, value):
        self.__trans_data = {}
        self.__trans_data = value

    @property
    def prop_equation(self):
        return self.__prop_equation

    @property
    def parms_values(self):
        return self.__parms_values

    @property
    def custom_integral(self):
        return self._custom_integral

    @property
    def summary(self):
        return {
            'databook_name': self.databook_name,
            'table_name': self.table_name,
            'eq_id': self.eq_id,
            'args': self.args,
            'arg_symbols': self.arg_symbols,
            'parms': self.parms,
            'returns': self.returns,
            'return_symbols': self.return_symbols,
            'body': self.body,
            'body_integral': self.body_integral,
            'body_first_derivative': self.body_first_derivative,
            'body_second_derivative': self.body_second_derivative,
            'custom_integral': self._custom_integral
        }

    @property
    def table_values(self):
        '''Get table values from yml file (if exists)'''
        if self.__table_values:
            return self.__table_values
        else:
            msg = f"""No table values found in the following reference \n
            ::: {self.databook_name}
            :::  {self.table_name}!
            """
            print(msg)
            return None

    @property
    def table_structure(self):
        '''Get table structure from yml file (if exists)'''
        if self.__table_structure:
            return self.__table_structure
        else:
            msg = f"""No table structure found in the following reference \n
            ::: {self.databook_name}
            :::  {self.table_name}!
            """
            print(msg)
            return None

    def eq_structure(self, id=1):
        '''
        Display equation details

        Parameters
        ----------
        id : int
            equation id (from 1 to ...), default is 1

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
            _body_integral = equation.get('BODY-INTEGRAL')
            _body_first_derivative = equation.get(
                'BODY-FIRST-DERIVATIVE')
            _body_second_derivative = equation.get(
                'BODY-SECOND-DERIVATIVE')
            # custom integral
            _custom_integral = equation.get('CUSTOM-INTEGRAL')

            # eq summary
            eq_summary = {
                'id': id,
                'body': _body,
                'args': _args,
                'parms': _parms,
                'return': _return,
                'body_integral': _body_integral,
                'body_first_derivative': _body_first_derivative,
                'body_second_derivative': _body_second_derivative,
                'custom_integral': _custom_integral
            }
            return eq_summary
        except Exception as e:
            raise Exception(f'Loading error {e}!')

    def eqs_structure(self, res_format: Literal['dict', 'json'] = 'dict'):
        '''
        Display all equations details

        Parameters
        ----------
        None

        Returns
        -------
        eq_summary : dict
            equation summary
        '''
        try:
            # equation list
            eq_num = self.eq_num

            # eq summary
            eq_summary = {}

            # looping through equations
            for id in range(eq_num):
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
                _body_integral = equation.get('BODY-INTEGRAL')
                _body_first_derivative = equation.get(
                    'BODY-FIRST-DERIVATIVE')
                _body_second_derivative = equation.get(
                    'BODY-SECOND-DERIVATIVE')
                # custom integral
                _custom_integral = equation.get('CUSTOM-INTEGRAL')

                # eq summary
                eq_summary[f"equation-{id+1}"] = {
                    'id': id,
                    'body': _body,
                    'args': _args,
                    'parms': _parms,
                    'return': _return,
                    'body_integral': _body_integral,
                    'body_first_derivative': _body_first_derivative,
                    'body_second_derivative': _body_second_derivative,
                    'custom_integral': _custom_integral
                }

            # check format
            if res_format == 'dict':
                return eq_summary
            elif res_format == 'json':
                return json.dumps(eq_summary, indent=4)

        except Exception as e:
            raise Exception(f'Loading error {e}!')

    @property
    def table_columns(self, column_name: str = 'COLUMNS'):
        '''
        Display table columns defined in `yml file`

        Parameters
        ----------
        column_name : str, optional
            column name (default is 'COLUMNS')

        Returns
        -------
        columns : list
            table columns
        '''
        try:
            # table structure
            table_structure = self.table_structure

            # check table structure
            if table_structure is None:
                raise Exception('Table structure not defined!')

            # res
            columns = table_structure.get(column_name, None)
            # check columns
            if columns is None:
                raise Exception(f'Column {column_name} not found!')

            # res
            return columns

        except Exception as e:
            raise Exception(f'Loading error {e}!')

    @property
    def table_units(self, unit_name: str = 'UNIT'):
        '''
        Display table units defined in `yml file`

        Parameters
        ----------
        unit_name : str, optional
            unit name (default is 'UNIT')

        Returns
        -------
        units : list
            table units
        '''
        try:
            # table structure
            table_structure = self.table_structure

            # check table structure
            if table_structure is None:
                raise Exception('Table structure not defined!')

            # res
            units = table_structure.get(unit_name, None)
            # check units
            if units is None:
                raise Exception(f'Unit {unit_name} not found!')

            # res
            return units

        except Exception as e:
            raise Exception(f'Loading error {e}!')

    @property
    def table_symbols(self, symbol_name: str = 'SYMBOL'):
        '''
        Display table symbols defined in `yml file`

        Parameters
        ----------
        symbol_name : str, optional
            symbol name (default is 'SYMBOL')

        Returns
        -------
        symbols : list
            table symbols
        '''
        try:
            # table structure
            table_structure = self.table_structure

            # check table structure
            if table_structure is None:
                raise Exception('Table structure not defined!')

            # res
            symbols = table_structure.get(symbol_name, None)
            # check symbols
            if symbols is None:
                raise Exception(f'Symbol {symbol_name} not found!')

            # res
            return symbols

        except Exception as e:
            raise Exception(f'Loading error {e}!')

    def eq_info(self):
        '''Get equation information.'''
        try:
            # get return
            _return = self.returns

            # check length
            if len(_return) == 1:
                return list(_return.values())[0]
            else:
                raise Exception("Every equation has only one return")
        except Exception as e:
            raise Exception(f'Loading error {e}!')

    def cal(self, message: str = '', decimal_accuracy: int = 4, sympy_format: bool = False, **args) -> EquationResult:
        '''
        Execute a function

        Parameters
        ----------
        message : str
            message to be printed
        decimal_accuracy : int
            decimal accuracy (default is 4)
        sympy_format : bool
            @deprecated() whether to return sympy format (default is False)
        args : dict
            a dictionary contains variable names and values as

        Returns
        -------
        eq_data : dict
            calculation result

        Examples
        --------
        >>> res = cal(message=f'{comp1} Vapor Pressure', T=120,P=1)
        >>> print(res)
        '''
        # equation info
        eq_info = self.eq_info()
        # databook and table name
        eq_src = {
            'databook_name': self.databook_name,
            'table_name': self.table_name,
        }
        # update
        eq_info.update(eq_src)

        # build parms dict
        _parms = self.load_parms()
        # execute equation
        # res
        res = None
        # check
        if sympy_format:
            res = self.eqExe_sympy(self.body, _parms, args=args)
        else:
            res = self.eqExe(self.body, _parms, args=args)

        if res is not None:
            res = round(res, decimal_accuracy)
        else:
            res = 'Error'

        # format data
        eq_data = format_eq_data(res, eq_info, message or 'No message')

        # res
        return eq_data

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
        >>> # heat capacity integral
        >>> res = cal_integral(T1=120,T2=150)
        >>> print(res)
        '''
        # build parms dict
        _parms = self.load_parms()
        # execute equation
        res = self.eqExe(self.body_integral, _parms, args=args)
        return res

    def cal_custom_integral(self, equation_name: str, **args):
        '''
        Calculate custom integral

        Parameters
        ----------
        equation_name : str
            equation name
        args : dict
            a dictionary contains variable names and values

        Returns
        -------
        res : float
            calculation result

        Examples
        --------
        >>> res = cal_custom_integral('Cp/RT',T1=120,T2=150)
        >>> print(res)
        '''
        try:
            # check
            if equation_name is None:
                raise Exception('Equation name not defined!')

            # check equation name exists
            if equation_name not in self._custom_integral:
                raise Exception('Equation name not found!')

            # build parms dict
            _parms = self.load_parms()

            # check
            if len(self._custom_integral) > 0:
                # body
                _body_lines = self._custom_integral[equation_name]
                # stringify
                _body = ";".join(_body_lines)
            else:
                _body = None
            # execute equation
            res = self.eqExe(_body, _parms, args=args)
            return res
        except Exception as e:
            raise Exception('Loading custom integral failed!, ', e)

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
        try:
            # check
            if self.body_first_derivative is None or self.body_first_derivative == 'None':
                print('The first derivative not defined!')

            # build parms dict
            _parms = self.load_parms()
            # execute equation
            res = self.eqExe(self.body_first_derivative, _parms, args=args)
            return res
        except Exception as e:
            raise Exception("Derivation calculation failed!, ", e)

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
        try:
            # check
            if self.body_second_derivative is None or self.body_second_derivative == 'None':
                print('The second derivative not defined!')

            # build parms dict
            _parms = self.load_parms()
            # execute equation
            res = self.eqExe(self.body_second_derivative, _parms, args=args)
            return res
        except Exception as e:
            raise Exception('Derivation calculation failed!, ', e)

    def load_parms(self):
        '''
        Load parms values and store in a dict,
        These parameters are constant values defined in an equation.
        '''
        try:
            # trans data (taken from csv)
            trans_data = self.trans_data
            # looping through self.parms
            # check parms
            if isinstance(self.parms, dict):
                # loaded parms (taken from reference)
                _parms_name = list(self.parms.keys())
                _parms = {value['symbol']: float(value['value'] or 0)/float(value['unit'] or 1)
                          for key, value in trans_data.items() if value['symbol'] in _parms_name}
            else:
                _parms = {}
            return _parms
        except Exception as e:
            raise Exception("Loading equation parameters failed!, ", e)

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
        # save eq id
        self.eq_id = Eq_data

        # load equation
        eq_summary = self.eq_structure(Eq_data)

        # extract data
        _body = eq_summary['body']
        self.body = ';'.join(_body)
        # check
        if eq_summary['parms'] is not None:
            self.parms = eq_summary['parms']
            # REVIEW
            # params value
            # self.__parms_values = self.load_parms()
        else:
            self.parms = []
        # check
        if eq_summary['args'] is not None:
            self.args = eq_summary['args']
            # make arg symbols
            self.arg_symbols = self.make_arg_symbols(self.args)
        else:
            self.args = []
        # check
        if eq_summary['return'] is not None:
            self.returns = eq_summary['return']
            # make return symbols
            self.return_symbols = self.make_return_symbols(self.returns)
        else:
            self.returns = []
        # integral
        body_integral = eq_summary['body_integral']
        # check
        if body_integral is not None and body_integral != 'None':
            self.body_integral = ";".join(body_integral)
        else:
            self.body_integral = None
        # first derivative
        first_derivative = eq_summary['body_first_derivative']
        # check
        if first_derivative is not None and first_derivative != 'None':
            self.body_first_derivative = ";".join(first_derivative)
        else:
            self.body_first_derivative = None
        # second derivative
        second_derivative = eq_summary['body_second_derivative']
        # check
        if second_derivative is not None and second_derivative != 'None':
            self.body_second_derivative = ";".join(second_derivative)
        else:
            self.body_second_derivative = None
        # custom integral
        custom_integral = eq_summary['custom_integral']
        # check
        if custom_integral is not None and custom_integral != 'None':
            self._custom_integral = custom_integral
        else:
            self._custom_integral = {}

        # update __prop_equation
        self.__prop_equation = {
            'BODY': self.body,
            'PARMS': self.parms,
            'ARGS': self.args,
            'RETURNS': self.returns,
            'BODY-INTEGRAL': self.body_integral,
            'BODY-FIRST-DERIVATIVE': self.body_first_derivative,
            'BODY-SECOND-DERIVATIVE': self.body_second_derivative,
            'CUSTOM-INTEGRAL': self._custom_integral
        }

        # check params
        if len(self.parms) > 0:
            self.__parms_values = self.load_parms()

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
        # check body
        if body is None:
            print('Function body not defined!')
            return None

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

    def to_dict(self):
        '''
        Convert equation to dict

        Parameters
        ----------
        None.

        Returns
        -------
        res : str
            equation in dict
        '''
        # create dict
        res = self.__prop_equation
        # yml
        # _eq_yml = _eq
        # convert to yml
        # res = yaml.dump(_eq_yml)

        return res

    def check_custom_integral_equation_body(self, equation_name) -> str:
        '''
        Displays the equation body of custom integral by equation name

        Parameters
        ----------
        equation_name : str
            equation name

        Returns
        -------
        body : str
            equation body

        Examples
        --------
        >>> body = custom_integral_equation_body('Cp/RT')
        '''
        try:
            # check
            if self._custom_integral is None:
                raise Exception('Custom integral not defined!')

            if equation_name is None:
                raise Exception('Equation name not defined!')

            if equation_name not in self._custom_integral:
                raise Exception('Equation name not found!')
            # get equation body
            body = self._custom_integral.get(equation_name, 'None')
            return body
        except Exception as e:
            raise Exception("Loading custom integral body failed!, ", e)

    def make_arg_symbols(self, args) -> dict:
        '''
        Make argument symbols

        Parameters
        ----------
        args : dict
            arguments

        Returns
        -------
        None.
        '''
        try:
            # reset
            arg_symbols = {}

            # check
            if args is not None:
                if isinstance(args, dict):
                    for key, value in args.items():
                        # symbol
                        _symbol = args[key].get('symbol')
                        # set
                        arg_symbols[_symbol] = {
                            'name': args[key].get('name'),
                            'symbol': _symbol,
                            'unit': args[key].get('unit'),
                        }

                    # return
                    return arg_symbols

            return {}
        except Exception as e:
            raise Exception("Making argument symbols failed!, ", e)

    def make_return_symbols(self, returns) -> dict:
        '''
        Make return symbols

        Parameters
        ----------
        returns : dict
            returns

        Returns
        -------
        None.
        '''
        try:
            # reset
            return_symbols = {}

            # check
            if returns is not None:
                if isinstance(returns, dict):
                    for key, value in returns.items():
                        # symbol
                        _symbol = returns[key].get('symbol')
                        # set
                        return_symbols[_symbol] = {
                            'name': returns[key].get('name'),
                            'symbol': _symbol,
                            'unit': returns[key].get('unit'),
                        }

                # return
                return return_symbols

            return {}
        except Exception as e:
            raise Exception("Making return symbols failed!, ", e)
