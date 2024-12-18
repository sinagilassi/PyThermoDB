# import packages/modules
import pandas as pd
import math
import sympy as sp
import yaml
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
    __prop_equation = {}
    __parms_values = {}
    # custom integral
    _custom_integral = {}
    # selected equation id
    eq_id: int = -1

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

    @property
    def prop_equation(self):
        return self.__prop_equation

    @property
    def parms_values(self):
        return self.__parms_values

    @property
    def custom_integral(self):
        return self._custom_integral

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

            # res
            return _return
        except Exception as e:
            raise Exception(f'Loading error {e}!')

    def cal(self, message: str = '', decimal_accuracy: int = 4, sympy_format: bool = False, **args):
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

        # build parms dict
        _parms = self.load_parms()
        # execute equation
        # check
        if sympy_format:
            res = self.eqExe_sympy(self.body, _parms, args=args)
        else:
            res = self.eqExe(self.body, _parms, args=args)

        if res is not None:
            res = round(res, decimal_accuracy)

        # set message
        if message == '':
            message = 'No message'

        # dict
        eq_data = {'value': res, **eq_info, 'message': message}

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
