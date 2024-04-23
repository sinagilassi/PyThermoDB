

def log2Col(records, column_names):
    '''
    display data in table format

        args: 
            records: list of records
            column_names: list of column names

        returns:
            None
    '''
    data = [column_names, *records]
    dash = '-' * 40
    # highest column length
    max_length = max(len(data[i][j]) for i in range(len(data)) for j in range(len(data[i])))

    # print table
    for i in range(len(data)):
        if i == 0:
            print(dash)
            print('{:^5s}{:^20s}'.format(data[i][0], data[i][1]))
            print(dash)
        else:
            print('{:<5s}{:>0s}'.format(data[i][0], data[i][1]))
    print(dash)
