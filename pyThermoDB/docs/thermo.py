# import packages/modules
# internal
from pyThermoDB.config.setting import THERMODYNAMICS_DATABOOK


class SettingDatabook():
    '''
    load databook reference
    '''
    # selected databook
    selected_db = None
    # selected table
    selected_tb = None
    
    def __init__(self):
        self.databook = THERMODYNAMICS_DATABOOK

    def get_thermo_databook(self):
        '''
        config pyThermoDB 
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
            val = input("Please choose databook: ")
            # check
            if val.isdigit() == True:
                # choose a table
                if int(val) < databook_no+1 and int(val) > 0:
                    print(f"You chose option {val}.")
                    # load tables
                    self.load_tables(res, int(val))
                    # select a table
                    while True:
                        # input
                        val2 = input("Please choose table: ")
                        # check
                        if val2.isdigit() == True:
                            # choose a table
                            if int(val) < len(self.selected_tb)+1 and int(val) > 0:
                                print(f"You chose option {val}.")
                                break
                            else:
                                print("Your choice is not valid. Please choose a valid option.")
                        elif str(val).lower() == 'q':
                            print("Goodbye!")
                            break
                        else:
                            print("Your choice is not valid. Please choose a valid option.")
                    break
            elif str(val).lower() == 'q':
                print("Goodbye!")
                break
            else:
                print("Your choice is not valid. Please choose a valid option.")
            
    def load_data(self):
        res = [[str(item['id']), item['book'], item['tables']]
               for item in self.databook]

        return res
        # find the maximum length of each column
        # max_length_book = int(max([len(item[1]) for item in res]))
        # max_length = max_length_book + 10
        # # column names
        # column_names = ['id', 'book']
        # data = [column_names, *res]
        # dash = '-' * max_length
        # # print table
        # # table head format
        # table_head = f'{{:^5s}} {{:^{max_length_book}s}}'
        # for i in range(len(data)):
        #     if i == 0:
        #         print(dash)
        #         print(table_head.format(data[i][0], data[i][1]))
        #         print(dash)
        #     else:
        #         print('{:^5s}{:>0s}'.format(data[i][0], data[i][1]))
        # print(dash)
        
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
                print('{:^5s}{:>0s}'.format(data[i][0], data[i][1]))
        print(dash)
        
        
    def load_tables(self, res, val):
        # choose databook tables
        self.selected_db = [item[2]
                            for item in res if item[0] == str(val-1)][0]
        print("The tables in this databook are: ")

        selected_tbs = [[str(item['id']), item['name']]
                        for item in self.selected_db]
        column_names2 = ['id', 'table']
        data2 = [column_names2, *selected_tbs]
        # display
        for i in range(len(data2)):
            if i == 0:
                print(dash)
                print(table_head.format(data2[i][0], data2[i][1]))
                print(dash)
            else:
                print('{:^5s}{:>0s}'.format(data2[i][0], data2[i][1]))
        print(dash)