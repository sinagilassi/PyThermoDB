# import packages/modules
import pandas as pd
import math
import sympy as sp
import numpy as np
# local
from .equationbuilder import EquationBuilder


class TableMatrixEquation:
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
    # bulk data
    __trans_data_pack = {}

    def __init__(self, table_name: str, equations: list, matrix_table=None):
        self.table_name = table_name
        self.equations = equations
        self.matrix_table = matrix_table

    @property
    def trans_data_pack(self):
        return self.__trans_data_pack

    @trans_data_pack.setter
    def trans_data_pack(self, value):
        self.__trans_data_pack = value

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
            equation id - non-zero-based id (from 1 to ...), default is 1

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
        try:
            # build parms dict
            # key: parms name, value: parms matrix (2d array)
            _parms = self.load_parms()
            # execute equation
            # check
            if sympy_format:
                res = self.eqExe_sympy(self.body, _parms, args=args)
            else:
                res = self.eqExe(self.body, _parms, args=args)
            return res
        except Exception as e:
            raise Exception('Calculation failed!, ', e)

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

    def set_params_ij(self, parm_id):
        '''
        Create a params matrix

        Parameters
        ----------
        parm_id : str
            parameter id

        '''
        try:
            pass
        except Exception as e:
            raise Exception('Set params matrix failed!, ', e)

    def load_parms(self):
        '''
        Load parms values and store in a dict,
        These parameters are constant values defined in an equation.
        '''
        try:
            # trans data (taken from csv)
            trans_data_pack = self.trans_data_pack
            # component names
            component_names = list(trans_data_pack.keys())
            # component no
            component_no = len(component_names)

            # check
            if not isinstance(self.matrix_table, pd.DataFrame):
                raise Exception('Matrix table not found!')

            # matrix table columns
            matrix_table_columns = list(self.matrix_table.columns)

            # symbol
            matrix_table_data_symbol = self.matrix_table.iloc[0, :]
            # unit
            matrix_table_data_unit = self.matrix_table.iloc[1, :].to_list()

            # component
            matrix_table_data_component_names = {
                name: i for i, name in enumerate(self.matrix_table['Name']) if name != '-'}
            # reset value to start from 0
            matrix_table_data_component_names = {
                str(i): name for i, name in enumerate(matrix_table_data_component_names.keys())}

            # matrix component no
            matrix_table_data_component_names_no = len(
                matrix_table_data_component_names)

            # set component name id
            component_names_dict = {}
            for i, name in matrix_table_data_component_names.items():
                if name in component_names:
                    component_names_dict[i] = name

            component_names_idx = list(component_names_dict.keys())
            component_names_idx = [int(item) for item in component_names_idx]

            # check
            if component_no > matrix_table_data_component_names_no:
                raise Exception("Check component number!")

            # looping through self.parms
            # check parms
            if isinstance(self.parms, dict):
                # loaded parms (taken from reference)
                _parms_name = list(self.parms.keys())
                # params clean
                _parms_name_clean = [item.split('_')[0]
                                     for item in _parms_name]
                # params column index
                _parms_col_index = []
                for item in matrix_table_columns:
                    if item.split('_')[0] in _parms_name_clean:
                        _parms_col_index.append(
                            matrix_table_columns.index(item))

            # create matrix
            parms_matrix_list = {}
            # component data
            matrix_table_component_data = {}
            # parms data
            matrix_table_component_parms_data = {}
            # looping through matrix table data
            for i, (component_key, component) in enumerate(matrix_table_data_component_names.items()):
                # component data
                _data_get = self.matrix_table[self.matrix_table['Name'].str.match(
                    component, case=False, na=False)]

                # set
                _row_index = int(_data_get.index[0])
                _data = _data_get.to_dict(orient='records')[0]

                # update
                _data['row_index'] = _row_index

                # check
                if len(_data) == 0:
                    raise Exception('Component data not found!')

                # component parms data
                matrix_table_component_parms_data[component] = {}
                # looping through self.parms
                # rename _data keys
                # * method 1:
                for key, value in _data.items():
                    # find parms
                    for item in _parms_name_clean:
                        _find_key = str(key).find(item+'_i')
                        # check
                        if _find_key != -1:
                            # new key
                            _new_key = str(key).replace('i', str(i+1))
                            # log
                            # print("method 1: ", _new_key, value, component)

                            # set value
                            # matrix_table_component_parms_data[component][str(
                            #     _new_key)] = float(value)

                # * method 2:
                # find parms from matrix column index
                # set
                jj = 0
                for item in _parms_col_index:
                    # check
                    if jj > matrix_table_data_component_names_no-1:
                        jj = 0
                    # lopping through data
                    for ii, (key, value) in enumerate(_data.items()):
                        # check
                        if ii == item:
                            # print(ii, item, jj)
                            # new key
                            _new_key = str(key).split(
                                "_")[0]+"_"+f"{i+1}"+"_"+f"{jj+1}"

                            # set unit
                            _unit = float(
                                matrix_table_data_unit[ii] or 1)

                            # log
                            # print("method 2: ", _new_key, value, component)
                            # set value
                            matrix_table_component_parms_data[component][_new_key] = float(
                                value)/_unit
                            # reset
                            jj = jj+1

                matrix_table_component_data[component] = _data

            # looping through parms group
            for i in range(len(_parms_name_clean)):

                # parms key (such as A_i_j)
                _parms_name = _parms_name_clean[i]
                _parms_key = f'{_parms_name}_i_j'

                # 2d array
                # _2d_array = np.zeros(
                #     (component_no, component_no))

                # 2d list
                _2d_list = []

                # looping through component
                for j in range(matrix_table_data_component_names_no):

                    # check
                    if j in component_names_idx:
                        # check component exists in
                        _component = matrix_table_data_component_names[str(j)]

                        # get component data
                        _data = matrix_table_component_data[_component]

                        # get component parms data
                        _parms_data = matrix_table_component_parms_data[_component]

                        # looping through component
                        for k in range(matrix_table_data_component_names_no):
                            # set key
                            _key = f'{_parms_name}_{j+1}_{k+1}'

                            # check
                            if k in component_names_idx:
                                # fill 2d array
                                # _2d_array[j, k] = float(_parms_data[_key])
                                _2d_list.append(float(_parms_data[_key]))

                # reshape list
                _2d_array = np.array(_2d_list).reshape(
                    component_no, component_no)
                # save parms matrix
                parms_matrix_list[_parms_key] = _2d_array

            # log
            # print("A_i_j: ", parms_matrix_list['A_i_j'])
            # print("B_i_j: ", parms_matrix_list['B_i_j'])

            # res
            return parms_matrix_list
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

        Notes
        ------
        Only one equation is used for matrix-equation calculation which is denoted by Eq 1.
        '''
        # set
        # transform_api_data = self.trans_data_pack

        # eq
        Eq_data = 0
        # Eq_data = int(transform_api_data['Eq']['value'])

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
        Execute a function body with provided arguments and parameters.

        Parameters
        ----------
        body : str
            A string containing Python code to execute. Must define a variable `res` for the return value.
        parms : dict
            A dictionary of parameters accessible as `parms` in the function body.
        args : dict
            A dictionary of arguments accessible as `args` in the function body.

        Returns
        -------
        res : float
            The calculation result defined in the `body` (if `res` is set), or None in case of errors.
        '''
        # check body
        if body is None:
            raise Exception('Function body not defined!')

        try:
            # Define a namespace dictionary for eval
            namespace = {'args': args, "parms": parms}
            # Import math module and numpy (np) lib within the function
            namespace['np'] = np
            namespace['math'] = math
            # Execute the body within the namespace
            exec(body, namespace)
            # Return the result
            return namespace['res']
        except Exception as e:
            raise Exception("Calculation failed!, ", e)

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

    def check_custom_integral_equation_body(self, equation_name: str) -> str:
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
