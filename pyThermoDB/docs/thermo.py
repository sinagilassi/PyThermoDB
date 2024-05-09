# import packages/modules
# internal
from pyThermoDB.config.setting import THERMODYNAMICS_DATABOOK, API_URL
from pyThermoDB.api import Manage
from pyThermoDB.utils import isNumber
from pyThermoDB.docs.transdata import TransData


class SettingDatabook():
    '''
    load databook reference
    '''
    # selected databook
    selected_db = []
    # available tables
    available_tbs = []
    # selected table
    selected_tb = []

    def __init__(self):
        self.databook = THERMODYNAMICS_DATABOOK

    def config(self):
        '''
        display config
        '''
        # column names
        column_names = ['id', 'selected databook']
        # databook
        _selected_db_id = str(self.selected_db[0])
        _selected_db = self.selected_db[1]
        # table
        _selected_tb_id = str(self.selected_tb[0])
        _selected_tb = self.selected_tb[1]
        # data
        data = [[_selected_db_id, _selected_db], [_selected_tb_id, _selected_tb]]
        # max length
        max_length = int(max(len(_selected_db), len(_selected_tb)))
        # log databook
        self.log_data(data, max_length, column_names)
    
    def get_databook(self):
        return self.selected_db[0], self.selected_db[1]
    
    def get_table(self):
        return self.selected_tb[0], self.selected_tb[1]
    
    def init(self):
        '''
        config pyThermoDB to use databook reference and table reference
        '''
        # load databook reference
        res = self.load_data()
        # number of databook
        databook_no = len(res)
        # find the maximum length of each column
        max_length_book = int(max([len(item[1]) for item in res]))
        # column name
        column_names = ['id', 'book']
        # log databook
        self.log_data(res, max_length_book, column_names)

        while True:
            # input
            userInput_1 = input("Please choose databook: ")
            if SettingDatabook.validate_input(userInput_1, 1, databook_no):
                # log
                print(f"You chose {userInput_1}.")
                # * check options
                if str(userInput_1).lower() == 'q':
                    print("Goodbye!")
                    break
                # get the value
                val = int(userInput_1)
                # * load tables
                self.load_tables(res, int(val))
                # number of tables
                table_no = len(self.available_tbs)
                # find the maximum length of each column
                max_length_book = int(
                    max([len(item[1]) for item in self.available_tbs]))
                # column name
                column_names = ['id', 'table']
                # log databook
                self.log_data(self.available_tbs,
                              max_length_book, column_names)

                # check table exists in the selected databook
                if table_no == 0:
                    print("There is no table in the selected databook.")
                    break
                # * choose a table
                while True:
                    # input
                    userInput_2 = input(
                        "Please choose table id or q to quit: ")
                    # check
                    if SettingDatabook.validate_input(userInput_2, 1, table_no):
                        # choose a table
                        print(f"You chose option {userInput_2}.")
                        val = int(userInput_2)
                        # get the table
                        self.selected_tb = self.available_tbs[val - 1]
                        break
                break
            else:
                print("Your choice is not valid. Please choose a valid option.")

    def load_data(self):
        res = [[str(item['id']), item['book'], item['tables']]
               for item in self.databook]
        return res

    def log_data(self, res, max_length_header, column_names):
        # find the maximum length of each column
        max_length = max_length_header + 10
        # update data
        data = [column_names, *res]
        dash = '-' * max_length
        # print table
        # table head format
        table_head = f'{{:^5s}} {{:^{max_length_header}s}}'
        for i in range(len(data)):
            if i == 0:
                print(dash)
                print(table_head.format(data[i][0], data[i][1]))
                print(dash)
            else:
                print('{:^5s}{:>0s}'.format(str(data[i][0]), data[i][1]))
        print(dash)

    def load_tables(self, res, val):
        '''
        set available tables from selected databook

        args:   
            res: list of databook reference
            val: id of selected databook

        returns:
            None
        '''
        # choose databook
        self.selected_db = []
        _selected_db = [item for item in res if item[0] == str(val)][0]
        self.selected_db = [*_selected_db]
        
        # tables
        _tables = _selected_db[2]

        # get available tables
        _available_tbs = [[item['id'], item['name']] for item in _tables]
        self.available_tbs = []
        self.available_tbs = [*_available_tbs]

    @staticmethod
    def validate_input(input_str, min_value, max_value):
        try:
            # Convert input to integer
            num = int(input_str)
            # Check if the number is between 1 and 9
            if min_value <= num <= max_value:
                return True
            else:
                return False
        except ValueError:
            # Check if the input is the letter 'q'
            if input_str.lower() == 'q':
                return True
            else:
                return False

    def check_component_availability(self, component_name):
        '''
        check component availability
        
        args:
            component_name: string of component name (e.g. 'Carbon dioxide')
            
        '''
        # set api
        ManageC = Manage(API_URL, self.selected_db[0], self.selected_tb[0])
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
        check component availability manually
        
        args:
            component_name: string of component name (e.g. 'Carbon dioxide')
            databook_id: databook id
            table_id: table id
            
        return:
            comp_info: component information
        '''
        try:
            # check databook_id and table_id are number or not
            if isNumber(databook_id) and isNumber(table_id):
                # set api
                ManageC = Manage(API_URL, databook_id, table_id)
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
        except Exception as e:
            print(e)
        
    def get_data(self, component_name):
        '''
        step1: get thermo data for a component
        
        step2: get equation for the data (parameters)
        
        args:
            component_name: string of component name (e.g. 'Carbon dioxide')
            
        '''
        # set api
        ManageC = Manage(API_URL, self.selected_db[0], self.selected_tb[0])
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
        step1: get thermo data for a component
        
        step2: get equation for the data (parameters)
        
        args:
            component_name: string of component name (e.g. 'Carbon dioxide')
            databook_id: databook id
            table_id: table id
        
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
            eqs = self.findEq(compInfo, databook_id, table_id)
            # src
            src = {}
            src['equations'] = eqs
            print(f"data for {component_name} is available.")
            tData = TransData(compInfo, src)
            # trans
            tData.trans()
            return tData
        else:
            print("API error. Please try again later.")
            return TransData([], {})
        
    def findEq(self, api_data, databook_id, table_id):
        '''
        find equation from thermodynamics databook
        
        args:
            api_data: api data - dict ['header'],['records'],['unit']
            databook_id: thermodynamic databook id
            table_id: table id
        '''
        # equation list
        eqs = []
        # api data structure
        header = api_data['header']
        # check equation exists in header
        if "Eq" in header:
            db = [item for item in THERMODYNAMICS_DATABOOK if item['id'] == databook_id][0]
            tb = [item for item in db['tables'] if item['id'] == table_id][0]
            eqs = tb['equations']
        return eqs