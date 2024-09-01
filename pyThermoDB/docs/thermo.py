# import packages/modules
import pandas as pd
# internal
from ..config import THERMODYNAMICS_DATABOOK, API_URL
from ..api import Manage
from ..utils import isNumber, uppercaseStringList
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

    def __init__(self):
        # ManageData init
        ManageData.__init__(self)

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

    def databooks(self, dataframe=True):
        '''
        List all databooks

        Returns
        -------

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

    def find_databook(self, databook):
        '''
        Find a databook

        Parameters
        ----------
        databook : str | int
            databook name/id

        Returns
        -------
        selected_databook: object
            selected databook
        databook_name: str
            databook name
        databook_id: int
            databook id
        '''
        try:
            if isinstance(databook, int):
                # databook id
                databook_id = databook-1
                databook_name = self.databook[databook_id]
            elif isinstance(databook, str):
                # find databook
                for i, item in enumerate(self.databook):
                    if item == databook.strip():
                        databook_id = i
                        databook_name = item
                        break
            else:
                raise ValueError("databook must be int or str")

            # set databook
            selected_databook = self.databook_bulk[databook_name]
            # res
            return selected_databook, databook_name, databook_id
        except Exception as e:
            raise Exception(e)

    def select_databook(self, databook):
        '''
        Select a databook from databook_list

        Parameters
        ----------
        databook : int | str
            databook id or name

        Returns
        -------
        None
        '''
        try:
            if isinstance(databook, int):
                self.selected_databook = self.databook[databook-1]
            elif isinstance(databook, str):
                # find databook
                self.selected_databook = next(
                    (item for item in self.databook if item == databook.strip()), None)
                if self.selected_databook is None:
                    raise ValueError(
                        f"No matching databook found for '{databook}'")
            else:
                raise ValueError("databook must be int or str")
            # log
            print(f"Selected databook: {self.selected_databook}")
        except ValueError as e:
            # Log or print the error for debugging purposes
            raise Exception(e)
            # Optionally, re-raise the exception if needed for higher-level error handling
            # raise

    def tables(self, databook=None, dataframe=True):
        '''
        List all tables in the selected databook

        Parameters
        ----------
        databook : int
            databook id
        dataframe: book
            if True, return a dataframe

        Returns
        -------
        table list : list
            list of tables
        '''
        try:
            # table list
            if databook is None:
                res = self.get_tables(self.selected_databook)
            else:
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

    def table(self, databook, table):
        '''
        Get a table 

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
                tables = self.tables(databook=db_name, dataframe=False)
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
            tb = self.table(databook, table)

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
                    data_no = len(table_data)

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

    def table_load(self, databook, table, dataframe=True):
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
            # table data
            table_data = []
            # get the tb
            tb = self.table(databook, table)

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
                # check data
                if tb_type == 'Data':
                    table_data = [*tb['data']]

                    # data no
                    return TableData(table_name, table_data)

        except Exception as e:
            raise Exception(f"Table loading error {e}")

    def check_component_availability(self, component_name):
        '''
        Check a component exists in a databook and table

        Parameters
        ----------
        component_name : str
            string of component name (e.g. 'Carbon dioxide')


        Returns
        -------
        None.
        '''
        # set api
        ManageC = Manage(
            API_URL, self.selected_databook, self.selected_tb)
        # search
        compList = ManageC.component_list()
        # check availability
        if len(compList) > 0:
            if component_name in compList:
                print(f"{component_name} is available.")
            else:
                print(f"{component_name} is not available.")
        else:
            print("API error. Please try again later.")

    def check_component_availability_manual(self, component_name, databook_id, table_id):
        '''
        Check component availability manually, 
        The difference with `check_component_availability` function is to set 
        manually databook and table ids.

        Parameters
        ----------
        component_name : str
            string of component name (e.g. 'Carbon dioxide')
        databook_id : int
            databook id
        table_id : int
            table id


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
                    databook_name = self.databooks(dataframe=False)[
                        databook_id-1]
                    # get table
                    table_name, id = self.tables(databook=databook_id, dataframe=False)[
                        table_id-1]
                    # check
                    if component_name.upper() in compListUpper:
                        print(
                            f"{component_name} available in [{table_name}] | [{databook_name}]")
                    else:
                        print(f"{component_name} is not available.")
                else:
                    print("API error. Please try again later.")
        except Exception as e:
            print(e)

    def get_data(self, component_name):
        '''
        Get data, 
        It consists of:
            step1: get thermo data for a component,
            step2: get equation for the data (parameters).

        args:
            component_name {str}: string of component name (e.g. 'Carbon dioxide')

        '''
        # set api
        ManageC = Manage(
            API_URL, self.selected_databook, self.selected_tb)
        # search
        compInfo = ManageC.component_info(component_name)
        # check availability
        if len(compInfo) > 0:
            print(f"data for {component_name} is available.")
            return compInfo
        else:
            print("API error. Please try again later.")
            return []

    def get_data_manual(self, component_name, databook_id, table_id):
        '''
        Get data manually, 
        The difference with `get_data` is to set databook and table ids manually.
        It consists of:
            step1: get thermo data for a component
            step2: get equation for the data (parameters)

        args:
            component_name {str}: string of component name (e.g. 'Carbon dioxide')
            databook_id {int}: databook id
            table_id {int}: table id

        return:
            comp_info: component information
        '''
        # set api
        ManageC = Manage(API_URL, databook_id, table_id)
        # search
        compInfo = ManageC.component_info(component_name)
        # equation (if exist)
        # check availability
        if len(compInfo) > 0:
            # check eq exists
            eqs = self.find_equation(compInfo, databook_id, table_id)
            # src
            src = {}
            src['equations'] = eqs
            src['component_name'] = component_name
            print(f"data for {component_name} is available.")
            # ! trans data
            tData = TransData(compInfo, src)
            # trans
            tData.trans()
            # equation init
            tData.eqSet()
            return tData
        else:
            print("API error. Please try again later.")
            return TransData([], {})

    def find_equation(self, api_data, databook_id, table_id):
        '''
        Find an equation from a thermodynamics databook

        Parameters
        ----------
        api_data : dict
            api data - dict ['header'],['records'],['unit'],['symbol']
        databook_id : int
            thermodynamic databook id
        table_id : int
            table id

        Returns
        -------
        eqs : list
            equation list
        '''
        # equation list
        eqs = []
        # api data structure
        header = api_data['header']

        # check equation exists in header
        if "Eq" in header:
            # find equation
            eqs = self.table_load(databook_id, table_id)

        return eqs
