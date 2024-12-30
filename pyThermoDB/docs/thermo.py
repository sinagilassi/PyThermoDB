# import packages/modules
import pandas as pd
from typing import List, Dict, Optional, Literal
import json
# internal
from ..config import API_URL
from ..api import Manage
from ..utils import isNumber, uppercaseStringList
from .tableref import TableReference
from .transdata import TransData
from .transmatrixdata import TransMatrixData
from .managedata import ManageData
from .tableequation import TableEquation
from .tablematrixequation import TableMatrixEquation
from .tabledata import TableData
from .tablematrixdata import TableMatrixData
from ..data import TableTypes
from ..models import DataBookTableTypes


class SettingDatabook(ManageData):
    '''
    Setting class
    '''
    # selected databook
    __selected_databook = ''
    # selected table
    __selected_tb = ''

    def __init__(self, custom_ref=None, data_source='local'):
        self.data_source = data_source
        self.custom_ref = custom_ref
        # ManageData init
        ManageData.__init__(self, custom_ref=custom_ref)

    @property
    def selected_databook(self):
        return self.__selected_databook

    @selected_databook.setter
    def selected_databook(self, value):
        self.__selected_databook = value

    @property
    def selected_tb(self):
        return self.__selected_tb

    @selected_tb.setter
    def selected_tb(self, value):
        self.__selected_tb = value

    def list_databooks(self, res_format: Literal['list', 'dataframe', 'json'] = 'dataframe'):
        '''
        List all databooks

        Parameters
        -----------
        res_format : Literal['list', 'dataframe', 'json']
            Format of the returned data. Defaults to 'dataframe'.

        Returns
        -------
        res : list | pandas.DataFrame | str
            Databook list in the specified format.
            - 'list': List of dictionaries containing databook information.
            - 'dataframe': Pandas DataFrame containing databook information.
            - 'json': JSON string representing the databook list.
        '''
        try:
            # databook list
            res = self.get_databooks()
            # check
            if res_format == 'list':
                return res[0]
            elif res_format == 'dataframe':
                return res[1]
            elif res_format == 'json':
                return res[2]
            else:
                raise ValueError('Invalid res_format')
        except Exception as e:
            raise Exception(f"databooks loading error! {e}")

    def list_tables(self, databook: int | str, res_format: Literal['list', 'dataframe', 'json'] = 'dataframe') -> list[list[str]] | pd.DataFrame | str:
        '''
        List all tables in the selected databook

        Parameters
        ----------
        databook : int | str
            databook id or name
        res_format : Literal['list', 'dataframe', 'json']
            Format of the returned data. Defaults to 'dataframe'.

        Returns
        -------
        table list : list | pandas.DataFrame | str
            list of tables
        '''
        try:
            # manual databook setting
            db, db_name, db_id = self.find_databook(databook)
            # table list
            res = self.get_tables(db_name)
            # check
            if res_format == 'list':
                return res[0]
            elif res_format == 'dataframe':
                return res[1]
            elif res_format == 'json':
                return res[2]
            else:
                raise ValueError('Invalid res_format')
        except Exception as e:
            raise Exception("Table loading error!,", e)

    def select_table(self, databook: int | str, table: int | str) -> DataBookTableTypes:
        '''
        Select a table

        Parameters
        ----------
        databook : int | str
            databook id or name
        table : int | str
            table id or name (non-zero-based id)
        dataframe: book
            if True, return a dataframe

        Returns
        -------
        tb : DataBookTableTypes
            table object
        '''
        try:
            # set
            tb_id = -1
            tb_name = ''

            # find databook
            db, db_name, db_id = self.find_databook(databook)

            # find table
            if isinstance(table, int):
                # tb
                tb = self.get_table(db_name, table-1)
            elif isinstance(table, str):
                # get tables
                tables = self.list_tables(databook=db_name, res_format='list')
                # check
                if isinstance(tables, list):
                    # looping
                    for i, item in enumerate(tables):
                        # check
                        if isinstance(item, list):
                            # table name
                            tb_name = item[0]
                            if tb_name == table.strip():
                                # zero-based id
                                tb_id = i
                                break
                        else:
                            raise ValueError(f"list {item} not found.")
                    # tb
                    # FIXME
                    tb = self.get_table(db, tb_id)
                else:
                    raise ValueError(f"table {table} not found.")
            else:
                raise ValueError("table must be int or str.")

            # res
            return tb
        except Exception as e:
            # Log or print the error for debugging purposes
            raise Exception(
                f"An error occurred while selecting the table: {e}")

    def table_info(self, databook: int | str, table: int | str, res_format: Literal['dict', 'dataframe', 'json'] = 'dataframe') -> dict | pd.DataFrame | str:
        '''
        Gives table contents as:

            * Table type
            * Data and equations numbers

        Parameters
        ----------
        databook : int | str
            databook id or name
        table : int | str
            table id or name
        dataframe: book
            if True, return a dataframe

        Returns
        -------
        tb_summary : dict | pandas.DataFrame | str
            table summary

        Notes
        -----
        1. The default value of dataframe is True, the return value (tb_summary) is Pandas Dataframe
        '''
        try:
            # table type
            tb_type = ''
            # table name
            table_name = ''
            # table equations
            table_equations = []
            # table data
            table_data = []
            # equation no
            equation_no = 0
            matrix_equation_no = 0
            # data no
            data_no = 0
            matrix_data_no = 0
            # get the tb
            tb = self.select_table(databook, table)

            # check
            if tb:
                # table name
                table_name: str = tb['table']
                # check
                if table_name is None:
                    raise Exception(f"table name {table_name} not found!")

                # check data/equations and matrix-data/matrix-equation
                # tb_type = 'Equation' if tb['equations'] is not None else 'Data'

                if tb['data'] is not None:
                    tb_type = 'Data'
                if tb['equations'] is not None:
                    tb_type = 'Equation'
                if tb['matrix_equations'] is not None:
                    tb_type = 'Matrix-Equation'
                if tb['matrix_data'] is not None:
                    tb_type = 'Matrix-Data'

                # ! check equations
                if tb_type == 'Equation' and tb['equations'] is not None:
                    for item in tb['equations']:
                        table_equations.append(item)

                    # equation no
                    equation_no = len(table_equations)

                # ! check data
                if tb_type == 'Data' and tb['data'] is not None:
                    table_data = [*tb['data']]

                    # data no
                    data_no = 1

                # ! check matrix-equation
                if tb_type == 'Matrix-Equation' and tb['matrix_equations'] is not None:
                    for item in tb['matrix_equations']:
                        table_equations.append(item)

                    # equation no
                    matrix_equation_no = len(table_equations)

                # ! check matrix-data
                if tb_type == 'Matrix-Data' and tb['matrix_data'] is not None:
                    # set
                    table_data = [*tb['matrix_data']]

                    # data no
                    matrix_data_no = 1

                # data
                tb_summary: dict = {
                    "Table Name": table_name,
                    "Type": tb_type,
                    "Equations": equation_no,
                    "Data": data_no,
                    "Matrix-Equations": matrix_equation_no,
                    "Matrix-Data": matrix_data_no
                }

                # json
                tb_summary_json = json.dumps(tb_summary)

            else:
                raise ValueError("No such table")

            if res_format == 'dataframe':
                # column names
                column_names = ['Table Name', 'Type', 'Equations',
                                'Data', 'Matrix-Equations', 'Matrix-Data']
                # dataframe
                df = pd.DataFrame([tb_summary], columns=column_names)
                return df
            elif res_format == 'json':
                return tb_summary_json
            elif res_format == 'dict':
                return tb_summary
            else:
                raise ValueError("Invalid res_format")
        except Exception as e:
            raise Exception(f"Table loading error {e}")

    def table_data(self, databook, table) -> pd.DataFrame:
        '''
        Get all table elements (display a table)

        Parameters
        ----------
        databook : str
            databook name
        table : str
            table name

        Returns
        -------
        tb_data : Pandas.DataFrame
            table data dataframe
        '''
        try:
            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id
            databook_id = db_rid + 1

            # find table zero-based id
            tb_id, tb_name = self.find_table(databook, table)
            # table id
            table_id = tb_id + 1

            # set api
            TableReferenceC = TableReference(custom_ref=self.custom_ref)
            # load table
            tb_data = TableReferenceC.load_table(databook_id, table_id)

            return tb_data
        except Exception as e:
            raise Exception(f"Loading matrix data failed {e}")

    def equation_load(self, databook: int | str, table: int | str) -> TableEquation:
        '''
        Display table header columns and other info

        Parameters
        ----------
        databook : int | str
            databook id or name
        table : str
            table name

        Returns
        -------
        object: TableEquation

        Notes
        -----
        1. table should be a string
        '''
        try:
            # table type
            # tb_type = ''
            # table name
            table_name = ''
            # table equations
            table_equations = []
            # get the tb
            tb = self.select_table(databook, table)

            # check
            if tb:
                # table name
                table_name = tb['table']
                # check data/equations
                if tb['equations'] is not None:
                    # set table type
                    # tb_type = 'equation'

                    # looping through equations
                    for item in tb['equations']:
                        table_equations.append(item)

                    # create table equation
                    return TableEquation(table_name, table_equations)

                else:
                    raise Exception('Table loading error!')
            else:
                raise Exception('Table loading error!')

        except Exception as e:
            raise Exception(f"Table loading error {e}")

    def data_load(self, databook: int | str, table: int | str) -> TableData:
        '''
        Display table header columns and other info

        Parameters
        ----------
        databook : int | str
            databook id or name
        table : str
            table name

        Returns
        -------
        object : TableData
            table object with data loaded
        '''
        try:
            # table type
            tb_type = ''
            # table name
            table_name = ''
            # table data
            table_data = []
            # get the tb
            tb = self.select_table(databook, table)

            # check
            if tb:
                # table name
                table_name = tb['table']

                # check data/equations
                if tb['data'] is not None:
                    tb_type = TableTypes.DATA.value

                # check data
                if tb_type == 'data':
                    table_data = tb['data']

                    # data no
                    return TableData(table_name, table_data)
                else:
                    raise Exception('Table loading error!')
            else:
                raise Exception('Table loading error!')
        except Exception as e:
            raise Exception(f"Table loading error {e}")

    def matrix_equation_load(self, databook: int | str, table: int | str) -> TableMatrixEquation:
        '''
        Display table header columns and other info

        Parameters
        ----------
        databook : int | str
            databook id or name
        table : str
            table name

        Returns
        -------
        object: TableMatrixEquation

        Notes
        -----
        1. table should be a string
        '''
        try:
            # table type
            # tb_type = ''
            # table name
            table_name = ''
            # table equations
            table_equations = []
            # get the tb
            tb = self.select_table(databook, table)

            # check
            if tb:
                # table name
                table_name = tb['table']

                # matrix-data/matrix-equation
                if tb['matrix_equations'] is not None:
                    # tb_type = TableTypes.MATRIX_EQUATIONS.value

                    for item in tb['matrix_equations']:
                        table_equations.append(item)

                    # create table equation
                    return TableMatrixEquation(table_name, table_equations)
                else:
                    raise Exception('Table loading error!')
            else:
                raise Exception('Table loading error!')

        except Exception as e:
            raise Exception(f"Table loading error {e}")

    def matrix_data_load(self, databook: int | str, table: int | str) -> TableMatrixData:
        '''
        Gives table contents as:

            * Table type
            * Data and equations numbers

        Parameters
        ----------
        databook : int | str
            databook id or name
        table : str
            table name

        Returns
        -------
        object : TableMatrixData
            table object with data loaded
        '''
        try:
            # table type
            # tb_type = ''
            # table name
            table_name = ''
            # table data
            table_data = []
            # get the tb
            tb = self.select_table(databook, table)

            # check
            if tb:
                # table name
                table_name = tb['table']

                # matrix-data/matrix-equation
                if tb['matrix_data'] is not None:
                    # tb_type = TableTypes.MATRIX_DATA.value

                    # table data
                    table_data = tb['matrix_data']

                    # data no
                    return TableMatrixData(table_name, table_data)
                else:
                    raise Exception('Table loading error!')
            else:
                raise Exception('Table not found!')
        except Exception as e:
            raise Exception(f"Table loading error {e}")

    def check_component(self, component_name: str | list[str], databook: int | str, table: int | str, column_name: Optional[str | list[str]] = None, query: bool = False) -> str:
        '''
        Check a component availability in the selected databook and table

        Parameters
        ----------
        component_name : str | list
            string of component name (e.g. 'Carbon dioxide') | list as ['Carbon dioxide','g']
        databook : int | str
            databook id or name
        table : int | str
            table id or name
        column_name : str | list
            column name (e.g. 'Name') | list as ['Name','state']
        query : str
            query to search a dataframe

        Returns
        -------
        res_json : str
            summary of the component availability
        '''
        try:
            # check search option
            if column_name is None:
                column_name = 'Name'

            # check
            if query:
                column_name = column_name

            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id (non-zero-based id)
            databook_id = db_rid + 1

            # find table zero-based id
            tb_id, tb_name = self.find_table(databook, table)
            # table id (non-zero-based id)
            table_id = tb_id + 1

            # res
            res = False

            # check databook_id and table_id are number or not
            if isNumber(databook_id) and isNumber(table_id):
                # check
                if self.data_source == 'api':
                    # res = self.check_component_api(
                    #     component_name, databook_id, table_id)
                    pass
                elif self.data_source == 'local':
                    res = self.check_component_local(
                        component_name, databook_id, table_id,
                        column_name, query=query)
                else:
                    raise Exception('Data source error!')
            else:
                raise Exception("databook and table id required!")

            # res
            res_dict = {
                'databook_id': databook_id,
                'table_id': table_id,
                'component_name': component_name,
                'availability': res
            }

            # json
            res_json = json.dumps(res_dict, indent=4)

            # res
            return res_json
        except Exception as e:
            raise Exception(f"Component check error! {e}")

    def check_component_api(self, component_name: str | list, databook_id: int, table_id: int):
        '''
        Check component availability in the selected databook and table

        Parameters
        ----------
        component_name : str | list
            string of component name (e.g. 'Carbon dioxide') | list as ['Carbon dioxide','g']
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str | list
            column name (e.g. 'Name') | list as ['Name','state']

        Returns
        -------
        comp_info : str
            component information
        '''
        try:
            # check databook_id and table_id are number or not
            if isNumber(databook_id) and isNumber(table_id):
                # set api
                ManageC = Manage(API_URL, databook_id, table_id)
                # search
                compList = ManageC.component_list()
                # check availability
                # uppercase list
                compListUpper = uppercaseStringList(compList)
                if len(compList) > 0:
                    # get databook
                    databook_name = self.list_databooks(res_format='list')[
                        databook_id-1]
                    # get table
                    table_name = self.list_tables(databook=databook_id, res_format='list')[
                        table_id-1][0]
                    # check
                    if component_name.upper() in compListUpper:
                        print(
                            f"[{component_name}] available in [{table_name}] | [{databook_name}]")
                    else:
                        print(f"{component_name} is not available.")
                else:
                    print("API error. Please try again later.")
            else:
                raise Exception(
                    "Invalid input. Please check the input type (databook_id and table_id).")
        except Exception as e:
            raise Exception(f'Checking data error {e}')

    def check_component_local(self, component_name: str | list, databook_id: int, table_id: int,
                              column_name: str | list[str], query: bool = False, verbose: bool = False) -> bool:
        '''
        Check component availability in the selected databook and table

        Parameters
        ----------
        component_name : str | list
            string of component name (e.g. 'Carbon dioxide') | list as ['Carbon dioxide','g']
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str
            column name (e.g. 'Name') | list
        query : str
            query string (e.g. 'Name == "Carbon dioxide"')

        Returns
        -------
        object : bool
            component information
        '''
        try:
            # check databook_id and table_id are number or not
            if isNumber(databook_id) and isNumber(table_id):
                # set api
                TableReferenceC = TableReference(custom_ref=self.custom_ref)
                # search
                df = TableReferenceC.search_tables(
                    databook_id, table_id, column_name, component_name,
                    query=query)
                # check availability
                if len(df) > 0:
                    # get databook
                    databook_name = self.list_databooks(res_format='list')[
                        databook_id-1]
                    # get table
                    table_name = self.list_tables(databook=databook_id, res_format='list')[
                        table_id-1][0]
                    # log
                    if verbose:
                        print(
                            f"[{component_name}] available in [{table_name}] | [{databook_name}]")

                    # res
                    return True
                else:
                    # log
                    if verbose:
                        print(f"{component_name} is not available.")
                    # res
                    return False
            else:
                raise Exception("databook and table id required!")
        except Exception as e:
            raise Exception(f'Reading data error {e}')

    def get_component_data(self, component_name: str, databook_id: int, table_id: int,
                           column_name: Optional[str | list[str]] = None, dataframe: bool = False, query: bool = False, matrix_tb: bool = False):
        '''
        Get component data from database (api|local csvs)

        Parameters
        ----------
        component_name : str
            string of component name (e.g. 'Carbon dioxide')
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str
            column name
        dataframe : bool
            return dataframe or not
        query : bool
            query or not

        Returns
        -------
        component_data : object | pandas dataframe
            component data
        '''
        try:
            # check search option
            if column_name is None:
                column_name = 'Name'

            # set
            component_name = str(component_name).strip()
            # check datasource
            if self.data_source == 'api':
                # component_data = self.get_component_data_api(
                #     component_name, databook_id, table_id, column_name,
                #     dataframe=dataframe)
                pass
            elif self.data_source == 'local':
                component_data = self.get_component_data_local(
                    component_name, databook_id, table_id, column_name,
                    dataframe=dataframe, query=query, matrix_tb=matrix_tb)
            else:
                raise Exception('Data source error!')
            # res
            return component_data
        except Exception as e:
            raise Exception(f"Loading data failed {e}")

    def get_component_data_api(self, component_name, databook_id, table_id,
                               dataframe=False):
        '''
        Get component data from database (api)
        It consists of:
            step1: get thermo data for a component,
            step2: get equation for the data (parameters).

        Parameters
        ----------
        component_name : str
            string of component name (e.g. 'Carbon dioxide')
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str
            column name
        dataframe : bool
            return dataframe or not

        Returns
        -------
        component_data : object | pandas dataframe
            component data
        '''
        # set api
        ManageC = Manage(API_URL, databook_id, table_id)
        # search
        component_data = ManageC.component_info(component_name)
        # check availability
        if len(component_data) > 0:
            # check
            if dataframe:
                df = pd.DataFrame(component_data, columns=[
                    'header', 'symbol', 'records', 'unit'])
                return df
            else:
                return component_data
        else:
            print(f"Data for {component_name} not available!")
            return {}

    def get_component_data_local(self, component_name: str, databook_id: int, table_id: int,
                                 column_name: str | list[str], dataframe: bool = False, query: bool = False, matrix_tb: bool = False):
        '''
        Get component data from database (local csv files)

        Parameters
        ----------
        component_name : str
            string of component name (e.g. 'Carbon dioxide')
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str
            column name | query to find a record from a dataframe
        dataframe : bool
            return dataframe or not
        query : bool
            query or not
        matrix_tb : bool
            matrix table or not

        Returns
        -------
        payload : dict | pandas dataframe
            component information
        '''
        try:
            # check databook_id and table_id are number or not
            if isNumber(databook_id) and isNumber(table_id):
                # set api
                TableReferenceC = TableReference(custom_ref=self.custom_ref)
                # search
                payload = TableReferenceC.make_payload(
                    databook_id, table_id, column_name, component_name,
                    query=query, matrix_tb=matrix_tb)
                # check availability
                if payload:
                    # check
                    if len(payload) > 0:
                        if dataframe:
                            df = pd.DataFrame(payload, columns=[
                                'header', 'symbol', 'records', 'unit'])
                            return df
                        else:
                            return payload
                    else:
                        raise Exception(
                            "Data for {} not available!".format(component_name))
                else:
                    raise Exception(
                        "Data for {} not available!".format(component_name))
            else:
                print("databook and table id required!")
        except Exception as e:
            raise Exception(f'Reading data error {e}')

    def build_equation(self, component_name: str, databook: int | str, table: int | str,
                       column_name: Optional[str | list[str]] = None, query: bool = False) -> TableEquation:
        '''
        Build equation for as:
            step1: get thermo data for a component
            step2: get equation for the data (parameters)

        Parameters
        ----------
        component_name : str
            string of component name (e.g. 'Carbon dioxide')
        databook : int | str
            databook id or name
        table : int | str
            table id or name
        column_name : str | list
            column name (e.g. 'Name') | list as ['Name','state']

        Returns
        -------
        eqs: TableEquation
            equation object
        '''
        try:
            # check search option
            if column_name is None:
                column_name = 'Name'

            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id
            databook_id = db_rid + 1

            # find table zero-based id
            tb_id, tb_name = self.find_table(databook, table)
            # table id
            table_id = tb_id + 1

            # get data from api
            component_data = self.get_component_data(
                component_name, databook_id, table_id, column_name=column_name,
                query=query)

            # check loading state
            if component_data:
                # check availability
                if len(component_data) > 0:
                    # ! trans data
                    TransDataC = TransData(component_data)
                    # transform api data
                    TransDataC.trans()
                    # transformed api data
                    transform_api_data = TransDataC.data_trans
                    # check data type
                    _data_type = TransDataC.data_type

                    # ! check datatype compatibility
                    if _data_type != 'equation':
                        print("The selected table contains no data for building\
                            equation! check table id and try again.")

                        raise Exception('Building equation failed!')

                    # ! build equation
                    # check eq exists
                    eqs = self.equation_load(
                        databook_id, table_id)

                    # update trans_data
                    eqs.trans_data = transform_api_data

                    # equation init
                    eqs.eqSet()
                    # res
                    return eqs
                else:
                    raise Exception(
                        "Data for {} not available!".format(component_name))
            else:
                raise Exception("Building equation failed!")
        except Exception as e:
            raise Exception(f'Building equation error {e}')

    def build_data(self, component_name: str, databook: int | str, table: int | str,
                   column_name: Optional[str | list[str]] = None, query: bool = False) -> TableData:
        '''
        Build data as:
            step1: get thermo data for a component

        Parameters
        ----------
        component_name : str
            string of component name (e.g. 'Carbon dioxide')
        databook : int | str
            databook id or name
        table : int | str
            table id or name
        column_name : str | list
            column name (e.g. 'Name') | list as ['Name','state']

        Returns
        -------
        dt: object
            data object
        '''
        try:
            # check search option
            if column_name is None:
                column_name = 'Name'

            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id
            databook_id = db_rid + 1

            # find table zero-based id
            tb_id, tb_name = self.find_table(databook, table)
            # table id
            table_id = tb_id + 1

            # get data from api
            component_data = self.get_component_data(
                component_name, databook_id, table_id, column_name=column_name,
                query=query)

            # check loading state
            if component_data:
                # check availability
                if len(component_data) > 0:
                    # ! trans data
                    TransDataC = TransData(component_data)
                    # transform api data
                    TransDataC.trans()
                    # transformed api data
                    transform_api_data = TransDataC.data_trans

                    # ! check data type
                    _data_type = TransDataC.data_type
                    if _data_type != 'data':
                        print(
                            "The selected table contains no data for building data!\
                            check table id and try again.")

                        raise Exception('Building data failed!')

                    # ! build data
                    # * construct template
                    # check eq exists
                    dts = self.data_load(
                        databook_id, table_id)

                    # ! check
                    if dts is not None:
                        # update trans_data
                        dts.trans_data = transform_api_data
                        # prop data
                        dts.prop_data = transform_api_data
                    else:
                        raise Exception('Building data failed!')

                    # res
                    return dts
                else:
                    raise Exception(
                        "Data for {} not available!".format(component_name))
            else:
                raise Exception("Building data failed!")
        except Exception as e:
            raise Exception(f'Building data error {e}')

    def build_matrix_equation(self, component_names: list[str], databook: int | str, table: int | str,
                              column_name: Optional[str | list[str]] = None, query: bool = False) -> TableMatrixEquation:
        '''
        Build matrix-equation for as:
            step1: get thermo data for a component
            step2: get equation for the data (parameters)

        Parameters
        ----------
        component_names : list[str]
            component name list (e.g. ['Methanol','Ethanol'])
        databook : int | str
            databook id or name
        table : int | str
            table id or name
        column_name : str | list
            column name (e.g. 'Name') | list as ['Name','state']

        Returns
        -------
        eqs: TableMatrixEquation
            matrix-equation object
        '''
        try:
            # check search option
            if column_name is None:
                column_name = 'Name'

            # component no
            component_no = len(component_names)
            # check
            if component_no <= 1:
                raise Exception('At least two components are required')

            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id
            databook_id = db_rid + 1

            # find table zero-based id
            tb_id, tb_name = self.find_table(databook, table)
            # table id
            table_id = tb_id + 1

            # ! retrieve all data from matrix-table (csv file)
            # matrix table
            matrix_table = self.table_data(databook, table)

            # get data from api
            component_data_pack = []
            for component_name in component_names:
                component_data = self.get_component_data(component_name.strip(),
                                                         databook_id, table_id,
                                                         column_name=column_name,
                                                         query=query, matrix_tb=True)
                # save
                component_data_pack.append({
                    'component_name': str(component_name).strip(),
                    'data': component_data
                })

            # check loading state
            if component_data_pack:
                # check availability
                if len(component_data_pack) > 0:
                    # ! trans data
                    TransDataC = TransMatrixData(component_data_pack)
                    # transform api data
                    TransDataC.trans()
                    # transformed api data
                    transform_api_data = TransDataC.data_trans_pack
                    # check data type
                    _data_type = TransDataC.data_type

                    # ! check datatype compatibility
                    if _data_type != 'matrix-equations':
                        print("The selected table contains no data for building\
                            equation! check table id and try again.")

                        raise Exception('Building matrix-equation failed!')

                    # ! build equation
                    # ! reading yml reference
                    # check eq exists
                    eqs = self.matrix_equation_load(
                        databook_id, table_id)

                    # update trans_data
                    eqs.trans_data_pack = transform_api_data
                    # matrix table (data template)
                    eqs.matrix_table = matrix_table

                    # equation init
                    eqs.eqSet()
                    # res
                    return eqs
                else:
                    raise Exception("Data for {} not available!".format(
                        ",".join(component_names)))
            else:
                raise Exception("Building matrix-equation failed!")
        except Exception as e:
            raise Exception(f'Building matrix-equation error {e}')

    def build_matrix_data(self, component_names: list[str], databook: int | str, table: int | str,
                          column_name: Optional[str | list[str]] = None, query: bool = False) -> TableMatrixData:
        '''
        Build matrix data as:
            step1: get thermo matrix data

        Parameters
        ----------
        component_names : list[str]
            component name list (e.g. ['Methanol','Ethanol'])
        databook : int | str
            databook id or name
        table : int | str
            table id or name
        column_name : str | list
            column name (e.g. 'Name') | list as ['Name','state']

        Returns
        -------
        dt: object
            data object
        '''
        try:
            # check component list
            if not isinstance(component_names, list):
                raise Exception('Component names must be a list')

            # check component name
            if not all(isinstance(name, str) for name in component_names):
                raise Exception('Component names must be strings')

            # check search option
            if column_name is None:
                column_name = 'Name'

            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id
            databook_id = db_rid + 1

            # find table zero-based id
            tb_id, tb_name = self.find_table(databook, table)
            # table id
            table_id = tb_id + 1

            # matrix table
            # ! retrieve all data from matrix-table
            # ? usually matrix-table data are limited
            matrix_table = self.table_data(databook, table)

            # get data from api
            component_data_pack = []
            for component_name in component_names:
                component_data = self.get_component_data(component_name.strip(),
                                                         databook_id, table_id,
                                                         column_name=column_name,
                                                         query=query, matrix_tb=True)
                # save
                component_data_pack.append({
                    'component_name': str(component_name).strip(),
                    'data': component_data
                })

            # check loading state
            if component_data_pack:
                # check availability
                if len(component_data_pack) > 0:
                    # ! trans data
                    TransMatrixDataC = TransMatrixData(component_data_pack)
                    # transform api data
                    TransMatrixDataC.trans()
                    # transformed api data
                    transform_api_data = TransMatrixDataC.data_trans_pack

                    # ! check data type
                    _data_type = TransMatrixDataC.data_type
                    if _data_type != 'matrix-data':
                        print(
                            "The selected table contains no data for building matrix-data! check table id and try again.")

                        raise Exception('Building data failed!')

                    # ! build data
                    # check eq exists
                    dts = self.matrix_data_load(
                        databook_id, table_id)

                    # ! check
                    if dts is not None:
                        # check type
                        if isinstance(dts, TableMatrixData):
                            if hasattr(dts, 'trans_data_pack') and hasattr(dts, 'prop_data_pack'):
                                # update trans_data
                                dts.trans_data_pack = transform_api_data
                                # prop data
                                dts.prop_data_pack = transform_api_data
                                # matrix table
                                dts.matrix_table = matrix_table

                                # res
                                return dts
                            else:
                                raise Exception('Building data failed!')
                        else:
                            raise Exception('Building data failed!')
                    else:
                        raise Exception('Building data failed!')
                else:
                    raise Exception("Data for {} not available!".format(
                        ', '.join(component_names)))
            else:
                raise Exception("Building data failed!")
        except Exception as e:
            raise Exception(f'Building matrix data error {e}')
