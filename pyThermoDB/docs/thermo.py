# import packages/modules

# internal
from ..config import THERMODYNAMICS_DATABOOK, API_URL
from ..api import Manage
from ..utils import isNumber, uppercaseStringList
from .transdata import TransData
from .managedata import ManageData
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
                self.selected_databook = self.databook[databook]
            elif isinstance(databook, str):
                # find databook
                self.selected_databook = next(
                    (item for item in self.databook if item == databook.strip()), None)
                if self.selected_databook is None:
                    raise ValueError(
                        f"No matching databook found for '{databook}'")
            else:
                raise ValueError("databook must be int or str")
        except ValueError as e:
            # Log or print the error for debugging purposes
            print(f"An error occurred: {e}")
            # Optionally, re-raise the exception if needed for higher-level error handling
            # raise

    def list_tables(self):
        '''
        List all tables in the selected databook

        Returns
        -------

        '''
        try:
            # selected databook

        except Exception as e:
            raise Exception(e)

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
            API_URL, self.selected_databook[0], self.selected_tb[0])
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
                    if component_name.upper() in compListUpper:
                        print(f"{component_name} is available.")
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
            API_URL, self.selected_databook[0], self.selected_tb[0])
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
            db = [item for item in THERMODYNAMICS_DATABOOK if item['id']
                  == databook_id][0]
            tb = [item for item in db['tables'] if item['id'] == table_id][0]
            eqs = tb['equations']
        return eqs
