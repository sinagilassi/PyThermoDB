# import packages/modules
import pandas as pd
# internal
from ..config import API_URL
from ..api import Manage
from ..utils import isNumber, uppercaseStringList
from ..data import TableReference
from .transdata import TransData
from .managedata import ManageData
from .tableequation import TableEquation
from .tabledata import TableData
#


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

    def list_databooks(self, dataframe=True):
        '''
        List all databooks

        Returns
        -------
        res: dict | pandas dataframe
            databook list
        '''
        try:
            # databook list
            res = self.get_databooks()
            # check
            if dataframe:
                return res[1]
            else:
                return res[0]
        except Exception as e:
            raise Exception(f"databooks loading error! {e}")

    def list_tables(self, databook, dataframe=True):
        '''
        List all tables in the selected databook

        Parameters
        ----------
        databook : int | str
            databook id or name
        dataframe: book
            if True, return a dataframe

        Returns
        -------
        table list : list
            list of tables
        '''
        try:
            # manual databook setting
            db, db_name, db_id = self.find_databook(databook)
            # table list
            res = self.get_tables(db_name)
            # check
            if dataframe:
                return res[1]
            else:
                return res[0]
        except Exception as e:
            raise Exception(e)

    def select_table(self, databook, table):
        '''
        select a table

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
        None
        '''
        try:
            # find databook
            db, db_name, db_id = self.find_databook(databook)
            # find table
            if isinstance(table, int):
                # tb
                tb = self.get_table(db_name, table-1)
            elif isinstance(table, str):
                # get tables
                tables = self.list_tables(databook=db_name, dataframe=False)
                # looping
                for i, item in enumerate(tables):
                    if item == table.strip():
                        tb_id = i
                        break
                # tb
                tb = self.get_table(db, tb_id-1)
            else:
                raise ValueError("table must be int or str")

            # dataframe
            # res
            return tb

        except Exception as e:
            # Log or print the error for debugging purposes
            print(f"An error occurred: {e}")

    def table_info(self, databook, table, dataframe=True):
        '''
        Display table header columns and other info

        Parameters
        ----------
        tb : object
            table object

        Returns
        -------
        None.
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
            # data no
            data_no = 0
            # get the tb
            tb = self.select_table(databook, table)

            # check
            if tb:
                # table name
                table_name = tb['table']
                # check data/equations
                tb_type = 'Equation' if tb['equations'] is not None else 'Data'

                # check equations
                if tb_type == 'Equation':
                    for item in tb['equations']:
                        table_equations.append(item)

                    # equation no
                    equation_no = len(table_equations)
                # check data
                if tb_type == 'Data':
                    table_data = [*tb['data']]

                    # data no
                    data_no = 1

                # data
                _tb_summary = {
                    "Table Name": table_name,
                    "Type": tb_type,
                    "Equations": equation_no,
                    "Data": data_no
                }

            if dataframe:
                # column names
                column_names = ['Table Name', 'Type', 'Equations', 'Data']
                # dataframe
                df = pd.DataFrame([_tb_summary], columns=column_names)
                return df
            else:
                return _tb_summary
        except Exception as e:
            raise Exception(f"Table loading error {e}")

    def equation_load(self, databook, table):
        '''
        Display table header columns and other info

        Parameters
        ----------
        tb : object
            table object

        Returns
        -------
        object
        '''
        try:
            # table type
            tb_type = ''
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
                tb_type = 'Equation' if tb['equations'] is not None else 'Data'

                # check equations
                if tb_type == 'Equation':
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

    def data_load(self, databook, table):
        '''
        Display table header columns and other info

        Parameters
        ----------
        tb : object
            table object

        Returns
        -------
        object
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
                tb_type = 'Equation' if tb['equations'] is not None else 'Data'

                # check data
                if tb_type == 'Data':
                    table_data = tb['data']

                    # data no
                    return TableData(table_name, table_data)
                else:
                    raise Exception('Table loading error!')
        except Exception as e:
            raise Exception(f"Table loading error {e}")

    def check_component(self, component_name, databook_id, table_id, column_name='Name'):
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
                # check
                if self.data_source == 'api':
                    self.check_component_api(
                        component_name, databook_id, table_id)
                elif self.data_source == 'local':
                    self.check_component_local(
                        component_name, databook_id, table_id, column_name)
                else:
                    raise Exception('Data source error!')

        except Exception as e:
            raise Exception(f"Component check error! {e}")

    def check_component_api(self, component_name, databook_id, table_id, column_name='Name'):
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
                    databook_name = self.list_databooks(dataframe=False)[
                        databook_id-1]
                    # get table
                    table_name = self.list_tables(databook=databook_id, dataframe=False)[
                        table_id-1][0]
                    # check
                    if component_name.upper() in compListUpper:
                        print(
                            f"[{component_name}] available in [{table_name}] | [{databook_name}]")
                    else:
                        print(f"{component_name} is not available.")
                else:
                    print("API error. Please try again later.")
        except Exception as e:
            print(e)

    def check_component_local(self, component_name, databook_id, table_id, column_name='Name'):
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
                TableReferenceC = TableReference(custom_ref=self.custom_ref)
                # search
                df = TableReferenceC.search_table(
                    databook_id, table_id, column_name, component_name)
                # check availability
                if len(df) > 0:
                    # get databook
                    databook_name = self.list_databooks(dataframe=False)[
                        databook_id-1]
                    # get table
                    table_name = self.list_tables(databook=databook_id, dataframe=False)[
                        table_id-1][0]
                    # log
                    print(
                        f"[{component_name}] available in [{table_name}] | [{databook_name}]")
                else:
                    print(f"{component_name} is not available.")
            else:
                print("databook and table id required!")
        except Exception as e:
            raise Exception(f'Reading data error {e}')

    def get_component_data(self, component_name, databook_id, table_id, column_name='Name', dataframe=False):
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

        Returns
        -------
        component_data : object | pandas dataframe
            component data
        '''
        try:
            # set
            component_name = str(component_name).strip()
            # check datasource
            if self.data_source == 'api':
                component_data = self.get_component_data_api(
                    component_name, databook_id, table_id, column_name, dataframe)
            elif self.data_source == 'local':
                component_data = self.get_component_data_local(
                    component_name, databook_id, table_id, column_name, dataframe)
            else:
                raise Exception('Data source error!')
            # res
            return component_data
        except Exception as e:
            raise Exception(f"Loading data failed {e}")

    def get_component_data_api(self, component_name, databook_id, table_id, column_name='Name', dataframe=False):
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

    def get_component_data_local(self, component_name, databook_id, table_id, column_name='Name', dataframe=False):
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
            column name

        Returns
        -------
        comp_info : str
            component information
        '''
        try:
            # check databook_id and table_id are number or not
            if isNumber(databook_id) and isNumber(table_id):
                # set api
                TableReferenceC = TableReference(custom_ref=self.custom_ref)
                # search
                payload = TableReferenceC.make_payload(
                    databook_id, table_id, column_name, component_name)
                # check availability
                if len(payload) > 0:
                    # check
                    if dataframe:
                        df = pd.DataFrame(payload, columns=[
                            'header', 'symbol', 'records', 'unit'])
                        return df
                    else:
                        return payload
                else:
                    print(f"Data for {component_name} not available!")
                    return {}
            else:
                print("databook and table id required!")
        except Exception as e:
            raise Exception(f'Reading data error {e}')

    def build_equation(self, component_name, databook_id, table_id, column_name='Name'):
        '''
        Build equation for as:
            step1: get thermo data for a component
            step2: get equation for the data (parameters)

        Parameters
        ----------
        component_name : str
            string of component name (e.g. 'Carbon dioxide')
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str | list
            column name (e.g. 'Name') | list as ['Name','state']

        Returns
        -------
        eqs: object
            equation object
        '''
        # get data from api
        component_data = self.get_component_data(
            component_name, databook_id, table_id, dataframe=False, column_name=column_name)

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
                print("Data for {} not available!".format(component_name))
        else:
            print("API error. Please try again later.")
            raise Exception("Building equation failed!")

    def build_data(self, component_name, databook_id, table_id, column_name='Name'):
        '''
        Build data as:
            step1: get thermo data for a component

        Parameters
        ----------
        component_name : str
            string of component name (e.g. 'Carbon dioxide')
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str | list
            column name (e.g. 'Name') | list as ['Name','state']

        Returns
        -------
        dt: object
            data object
        '''
        # get data from api
        component_data = self.get_component_data(
            component_name, databook_id, table_id, column_name=column_name)

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

                # ! build data
                # check eq exists
                dts = self.data_load(
                    databook_id, table_id)

                # check
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
                print("Data for {} not available!".format(component_name))
        else:
            print("API error. Please try again later.")
            raise Exception("Building data failed!")
