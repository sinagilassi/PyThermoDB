# import packages/modules
# internal
from pyThermoDB.config.setting import THERMODYNAMICS_DATABOOK


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
        _selected_db = self.selected_db[1]
        print(f"databook: {_selected_db}")
        _selected_tb = self.selected_tb
        print(f"table: {_selected_tb}")

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
                        self.selected_tb = self.available_tbs[val - 1][1]
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
        _selected_db = [item[2] for item in res if item[0] == str(val)][0]
        self.selected_db = [*_selected_db]

        # get available tables
        _available_tbs = [[item['id'], item['name']] for item in _selected_db]
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
