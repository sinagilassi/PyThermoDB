# import packages/modules
import logging
import pandas as pd
import math
import json
from typing import Literal, Optional, List, Dict, Any
# local
from ..models import EquationResult, PropertyMatch, EquationRangeResult
from ..utils import format_eq_data, is_number
from ..models.tables import TableEquationBlock
from .table_util import TableUtil
# ! deps
from ..config.deps import get_config

# NOTE: logger
logger = logging.getLogger(__name__)


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

    def __init__(
        self,
        databook_name,
        table_name,
        equations,
        table_values: Optional[List | Dict] = None,
        table_structure: Optional[Dict[str, Any]] = None
    ):
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
        # NOTE: get config
        config = get_config()
        # ! include data tables based on config
        self.include_data = config.include_data
        # logging
        logger.debug(
            f"TableData initialized with include_data={self.include_data}"
        )

        # NOTE: set attributes
        self.databook_name = databook_name
        self.table_name = table_name

        # NOTE: equation list structures (yml file)
        self.equations = equations
        # number of equations
        self.eq_num = len(equations)

        # NOTE: set data
        # table values (yml)
        self.__table_values = table_values if table_values else None
        # table structure (yml)
        self.__table_structure = table_structure if table_structure else None

        # SECTION: set data only if include_data is True
        if self.include_data is False:
            # logging
            logger.info(
                f"Data tables are excluded as per configuration. "
                f"Table data for '{self.table_name}' will not include property data."
            )
            self.__table_values = None

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
                'BODY-FIRST-DERIVATIVE'
            )
            _body_second_derivative = equation.get(
                'BODY-SECOND-DERIVATIVE'
            )
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
    def table_columns(
        self,
        column_name: str = 'COLUMNS',
    ) -> List[str]:
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
                logger.error('Table structure not defined!')
                raise

            # res
            columns = table_structure.get(column_name, None)
            # check columns
            if columns is None:
                logger.error(f'Column {column_name} not found!')
                raise

            # res
            return columns

        except Exception as e:
            logger.error(f'Loading error {e}!')
            return []

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
            logger.error(f'Loading error {e}!')
            return []

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
            logger.error(f'Loading error {e}!')
            return []

    def get_arg_symbols(self):
        '''Get argument symbols.'''
        try:
            # get arg symbols
            _arg_symbols = self.arg_symbols

            # extract symbols
            symbols = []

            # iterate through arg_symbols
            for key, value in _arg_symbols.items():
                symbols.append(value['symbol'])

            return symbols
        except Exception as e:
            raise Exception(f'Loading error {e}!')

    def eq_info(self):
        '''Get equation information.'''
        try:
            # get return
            _return = self.returns

            # check length
            # for dict
            if isinstance(_return, dict):
                return list(_return.values())[0]
            elif isinstance(_return, list):
                return _return[0]

            # if len(_return) == 1:
            #     return list(_return.values())[0]
            else:
                raise Exception("Every equation has only one return")
        except Exception as e:
            raise Exception(f'Loading error {e}!')

    def get_variable_range_values(
            self,
    ):
        '''
        Get variable range values for given variable names.

        Parameters
        ----------
        None

        Returns
        -------
        Dict[str, List[float]]
            A dictionary with variable names as keys and their range values as lists.

        Examples
        --------
        >>> res = get_variable_range_values(variable_names=['T', 'P'])
        >>> print(res)

        ```python
            {
            'T': [100.0, 500.0],
            'P': [1.0, 10.0]
            }
        ```
        '''
        try:
            def parse_min_max(var_name: str) -> dict:
                if var_name.endswith("min"):
                    return {"base": var_name[:-3], "type": "min"}
                elif var_name.endswith("max"):
                    return {"base": var_name[:-3], "type": "max"}
                else:
                    return {"base": var_name, "type": None}

            # SECTION: table structure
            table_structure = self.table_structure

            # check table structure
            if table_structure is None:
                raise Exception('Table structure not defined!')

            # SECTION: get range names in the table structure
            # NOTE: symbol
            symbols = table_structure.get('SYMBOL', [])
            # >> check
            if not symbols:
                logger.error('No symbols found in table structure!')
                return {}

            # NOTE: return variable names
            args_symbols = self.get_arg_symbols()

            # >> check
            if not args_symbols:
                logger.error('No argument symbols found!')
                return {}

            # NOTE: get valid variable range names
            valid_variables = TableUtil.get_variable_range(
                variable_names=args_symbols,
                symbol_names=symbols
            )
            # >> check
            if not valid_variables:
                logger.error('No valid variable range names found!')
                return {}

            # SECTION: extract variable range values
            # NOTE: table data
            # ! values for the component
            data = self.trans_data

            # res
            variable_ranges = {}

            # iterate through variable names
            for var_name, var_range_names in valid_variables.items():
                # create key
                variable_ranges[var_name] = {}

                # iterate through range names
                for range_name in var_range_names:
                    # extract range data
                    dt_ = data.get(range_name, None)

                    if dt_ is None:
                        logger.warning(
                            f'No data found for range name: {range_name}!'
                        )
                        continue

                    # find min and max in range_name
                    parse_key = parse_min_max(range_name)
                    key_id = parse_key['type']

                    variable_ranges[var_name][key_id] = dt_

            return variable_ranges
        except Exception as e:
            logger.error(f'Loading error {e}!')
            return {}

    def cal(
        self,
        message: str = '',
        decimal_accuracy: int = 4,
        **args
    ) -> EquationResult:
        '''
        Execute a function

        Parameters
        ----------
        message : str
            message to be printed
        decimal_accuracy : int
            decimal accuracy (default is 4)
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
        try:
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
            _parms = self.load_parms_v2()
            # execute equation
            # res
            res = None

            # NOTE: execute equation
            # check body
            if self.body is None or self.body == 'None':
                raise Exception('Equation body not defined!')

            res = self.eqExe(self.body, _parms, args=args)

            if res is not None:
                res = round(res, decimal_accuracy)
            else:
                res = 'Error'

            # format data
            eq_data = format_eq_data(res, eq_info, message or 'No message')

            # res
            return eq_data
        except Exception as e:
            logger.error(f'Calculation error {e}!')
            raise Exception(f'Calculation error {e}!')

    def cal_range(
        self,
        variable_id: str,
        variable_range_values: List[float],
        message: str = '',
        decimal_accuracy: int = 4,
        **args,
    ) -> EquationRangeResult:
        """
        Calculate over a specified range for a given variable.

        Parameters
        ----------
        variable_id : str
            The name or symbol of the variable to calculate over.
        variable_range_values : List[float]
            A list containing the range values for the variable.
        message : str
            A message to be printed.
        decimal_accuracy : int
            Decimal accuracy (default is 4).
        args : dict
            A dictionary containing other variable names and values.

        Returns
        -------
        res: EquationRangeResult
            Calculation results over the specified range.
            - x: List of variable values.
            - y: List of calculated results.
            - name: Name of the calculated property.
            - unit: Unit of the calculated property.
            - symbol: Symbol of the calculated property.
            - databook_name: Name of the databook.
            - table_name: Name of the table.
            - message: Message associated with the calculation.
        """
        try:
            # SECTION: validate inputs
            if not variable_id:
                raise Exception('Variable name not defined!')

            if not variable_range_values or len(variable_range_values) < 2:
                raise Exception('Variable range values not properly defined!')

            # NOTE: check variable availability
            # variable symbol
            variable_symbol = None

            # iterate over args_symbols
            for arg_k, arg_v in self.arg_symbols.items():
                # check both name and symbol
                if variable_id == arg_v['symbol']:
                    # found
                    variable_symbol = arg_v['symbol']
                    break
                elif variable_id == arg_v['name']:
                    # found
                    variable_symbol = arg_v['symbol']
                    break

            # >> check
            if variable_symbol is None:
                raise Exception(f'Variable {variable_id} not found!')

            # SECTION: calculation over range
            # init res
            res = {
                'x': [],
                'y': [],
                'name': '',
                'unit': '',
                'symbol': '',
                'databook_name': self.databook_name,
                'table_name': self.table_name,
                'message': message or 'No message'
            }

            # NOTE: loop over range values
            for var_value in variable_range_values:
                # build args
                calc_args = args.copy()
                calc_args[variable_symbol] = var_value

                # perform calculation
                res_ = self.cal(
                    message=message,
                    decimal_accuracy=decimal_accuracy,
                    **calc_args
                )

                # store result
                res['x'].append(var_value)
                res['y'].append(res_['value'])

            # set name, unit, symbol
            res['unit'] = res_['unit']
            res['symbol'] = res_['symbol']
            res['name'] = res_.get('name', None) or res_.get(
                'equation_name', None)

            # NOTE: convert to EquationRangeResult
            res = EquationRangeResult(**res)

            # res
            return res
        except Exception as e:
            logger.error(f'Calculation over range error {e}!')
            raise Exception(f'Calculation over range error {e}!')

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
        try:
            # build parms dict
            _parms = self.load_parms_v2()
            # execute equation
            res = self.eqExe(
                body=self.body_integral,
                parms=_parms,
                args=args
            )

            return res
        except Exception as e:
            raise Exception('Loading integral calculation failed!, ', e)

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
            _parms = self.load_parms_v2()

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
            if (
                self.body_first_derivative is None or
                self.body_first_derivative == 'None'
            ):
                print('The first derivative not defined!')

            # build parms dict
            _parms = self.load_parms_v2()

            # execute equation
            res = self.eqExe(
                body=self.body_first_derivative,
                parms=_parms,
                args=args
            )

            # res
            return res
        except Exception as e:
            logger.error(f'Derivation calculation failed!, {e}')
            return None

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
            if (self.body_second_derivative is None or
                    self.body_second_derivative == 'None'):
                print('The second derivative not defined!')

            # build parms dict
            _parms = self.load_parms_v2()
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
                # NOTE: loaded parms (taken from reference)
                _parms_name = list(self.parms.keys())
                # from symbol
                _parms_name = [
                    value['symbol']
                    for key, value in self.parms.items()
                ]

                # NOTE: create params dict
                _parms = {
                    value['symbol']:
                    float(value['value'] or 0)/float(value['unit'] or 1)
                    for key, value in trans_data.items() if value['symbol'] in _parms_name
                }
            else:
                _parms = {}
            return _parms
        except Exception as e:
            raise Exception("Loading equation parameters failed!, ", e)

    def load_parms_v2(self):
        """
        Load parameter values and store in a dict.
        These parameters are constant values defined in an equation.
        """
        try:
            trans_data = self.trans_data

            if isinstance(self.parms, dict):
                # Get the list of symbols we need
                parm_symbols = [v["symbol"] for v in self.parms.values()]

                def safe_float(x, default=1.0):
                    """Return float(x) if numeric, else default."""
                    try:
                        return float(x)
                    except (ValueError, TypeError):
                        return default

                # Build params dict
                parms = {
                    v["symbol"]: float(v.get("value", 0)) /
                    safe_float(v.get("unit"), 1.0)
                    for v in trans_data.values()
                    if v["symbol"] in parm_symbols
                }
            else:
                parms = {}

            return parms

        except Exception as e:
            raise Exception("Loading equation parameters failed!") from e

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

        # REVIEW: extract data
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
            self.__parms_values = self.load_parms_v2()

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

    def make_identifiers(
            self,
            param_id: Literal['arg', 'return'],
            mode: Literal['name', 'symbol'] = 'symbol'
    ) -> List[str]:
        '''
        Get return identifiers.

        Returns
        -------
        List[str]
            List of return symbols.
        '''
        try:
            # SECTION: get symbols source
            if param_id == 'arg':
                # arg symbols
                symbols_source = self.arg_symbols
            elif param_id == 'return':
                # return symbols
                symbols_source = self.return_symbols
            else:
                logger.error("Invalid param_id! Use 'arg' or 'return'.")
                return []

            # NOTE: validate mode
            if mode not in ['name', 'symbol']:
                logger.error("Invalid mode! Use 'name' or 'symbol'.")
                return []

            # NOTE: empty check
            if not symbols_source:
                logger.warning(f"No {param_id} symbols found!")
                return []

            # NOTE: type
            if not isinstance(symbols_source, dict):
                logger.error(f"{param_id} symbols is not a dictionary!")
                return []

            # SECTION: build symbol list
            # extract symbols
            symbols = []

            # iterate through return_symbols
            for key, value in symbols_source.items():
                if mode == 'symbol':
                    symbols.append(value['symbol'])
                elif mode == 'name':
                    symbols.append(value['name'])
                else:
                    raise Exception("Invalid mode! Use 'name' or 'symbol'.")

            return symbols
        except Exception as e:
            raise Exception(f'Loading error {e}!')

    def is_symbol_available(self, symbol: str):
        '''
        Check if a symbol is available in the table data. This method is case-insensitive.

        Parameters
        ----------
        symbol : str
            Symbol to check.

        Returns
        -------
        bool
            True if the symbol is available, False otherwise.
        '''
        try:
            # NOTE: get symbols
            symbols = self.table_symbols

            # SECTION: check if symbol exists (case-sensitive)
            return TableUtil.is_symbol_available(symbol, symbols)
        except Exception as e:
            logger.error(f"Error checking symbol availability: {e}")
            return PropertyMatch(
                prop_id=symbol,
                availability=False,
                search_mode='SYMBOL',
            )

    def is_column_name_available(self, column_name: str):
        '''
        Check if a column name is available in the table data.

        Parameters
        ----------
        column_name : str
            Column name to check.

        Returns
        -------
        bool
            True if the column name is available, False otherwise.
        '''
        try:
            # NOTE: get column names
            column_names = self.table_columns

            # SECTION: check if column exists (case-sensitive)
            return TableUtil.is_column_name_available(column_name, column_names)
        except Exception as e:
            logger.error(f"Error checking column name availability: {e}")
            return PropertyMatch(
                prop_id=column_name,
                availability=False,
                search_mode='COLUMN',
            )

    def is_property_available(
            self,
            prop_id: str,
            search_mode: Literal['SYMBOL', 'COLUMN', 'BOTH'] = 'BOTH'
    ) -> PropertyMatch:
        '''
        Check if a property is available in the table data.

        Parameters
        ----------
        prop_id : str
            Property ID to check.
        search_mode : Literal['SYMBOL', 'COLUMN', 'BOTH'], optional
            Search mode (default: 'BOTH'). Can be 'SYMBOL', 'COLUMN', or 'BOTH'.

        Returns
        -------
        bool
            True if the property is available, False otherwise.
        '''
        try:
            # NOTE: check inputs
            if not isinstance(prop_id, str):
                logger.error(
                    "Invalid property ID input! Property ID must be a string.")
                return False

            # SECTION: get property names
            if search_mode == 'SYMBOL':
                # ! symbol only
                return self.is_symbol_available(prop_id)
            elif search_mode == 'COLUMN':
                # ! column name only
                return self.is_column_name_available(prop_id)
            elif search_mode != 'BOTH':
                logger.error(
                    "Invalid search mode! Must be 'SYMBOL', 'COLUMN', or 'BOTH'."
                )
                return False

            # SECTION: check both symbol and column name
            # NOTE: check symbols (true/false)
            check_symbol_res = self.is_symbol_available(prop_id)

            # NOTE: check column names (true/false)
            check_column_res = self.is_column_name_available(prop_id)

            # check
            if check_symbol_res.availability or check_column_res.availability:
                return PropertyMatch(
                    prop_id=prop_id,
                    availability=True,
                    search_mode='BOTH'
                )
            else:
                return PropertyMatch(
                    prop_id=prop_id,
                    availability=False,
                    search_mode='BOTH'
                )

        except Exception as e:
            logger.error(f"Error checking property availability: {e}")
            return PropertyMatch(
                prop_id=prop_id,
                availability=False,
                search_mode=search_mode,
            )

    def normalized_fn_body(
            self,
            eq_id: int
    ) -> Optional[TableEquationBlock]:
        '''
        Get normalized function body with appropriate parameter units.

        Parameters
        ----------
        eq_id : int
            Equation ID for which to normalize the function body (non-zero Id).

        Returns
        -------
        Optional[TableEquationBlock]
            Normalized function body with parameter units, or None if table structure is not defined.

        Notes
        -----
        This method retrieves the equation structure for the specified equation ID,
        extracts the parameter units, and constructs a normalized function body, finally returning all equation data including the normalized body, parameters, arguments, and returns.
        '''
        try:
            # SECTION: retrieve equation structure
            # NOTE: equations
            equations: Dict[str, Any] = self.eq_structure(eq_id)
            # NOTE: parms
            parms_src: Dict = equations.get('parms', {})
            # >> parms
            parms_id = list(parms_src.keys())
            # NOTE: body
            body_lines: List = equations.get('body', [])

            # SECTION: retrieve structure data
            # NOTE init block
            parms_unit_block = []

            # iterate through parms to create parms/unit block
            for parm_key in parms_id:
                # parm details
                parm_details = parms_src.get(parm_key, {})
                parm_symbol = parm_details.get('symbol', '')
                parm_unit = parm_details.get('unit', '')

                # ! check numeric unit
                if is_number(parm_unit) is False:
                    continue

                # create parms/unit line
                if parm_symbol and parm_unit:
                    # create block line
                    block_line = f"parms['{parm_symbol}'] = parms['{parm_symbol}'] / {parm_unit}"
                    parms_unit_block.append(block_line)

            # SECTION: normalize function body (merge blocks)
            if len(parms_unit_block) > 0:
                # append parms/unit block to body
                normalized_body_lines = parms_unit_block + body_lines
            else:
                normalized_body_lines = body_lines

            # normalized body
            # normalized_body = ';'.join(normalized_body_lines)

            # set id (non-zero to zero)
            eq_id -= eq_id

            # SECTION: construct equation data
            eq_summary = {
                'id': eq_id,
                'body': normalized_body_lines,
                'args': equations.get('args', {}),
                'parms': equations.get('parms', {}),
                'returns': equations.get('return', {}),
                'body_integral': equations.get('body_integral', None),
                'body_first_derivative': equations.get(
                    'body_first_derivative', None
                ),
                'body_second_derivative': equations.get(
                    'body_second_derivative', None
                ),
                'custom_integral': equations.get('custom_integral', None)
            }

            # NOTE: set TableEquationBlock
            eq_summary = TableEquationBlock(**eq_summary)

            return eq_summary
        except Exception as e:
            logger.error(f'Normalizing function body error: {e}!')
            return None

    def normalized_fns(
            self
    ):
        """
        Get normalized function bodies for all equations in the table.

        Returns
        -------
        Optional[List[TableEquationBlock]]
            List of normalized function bodies with parameter units for all equations,
            or None if table structure is not defined.
        """
        try:
            # SECTION: retrieve equations
            eqs_src = self.eqs_structure(res_format='dict')

            # >> check
            if not isinstance(eqs_src, dict):
                return None

            # SECTION: normalize each equation body
            normalized_equations: List[TableEquationBlock] = []

            for i, (eq_id_str, eq_data) in enumerate(eqs_src.items()):
                # convert eq_id to int
                eq_id = int(i)
                # non-zero conversion
                eq_id += 1

                # get normalized body
                normalized_eq = self.normalized_fn_body(eq_id)

                if normalized_eq is not None:
                    # set
                    normalized_equations.append(normalized_eq)

            return normalized_equations
        except Exception as e:
            logger.error(f'Normalizing all function bodies error: {e}!')
            return None
