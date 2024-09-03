# MANAGE DATA
# ===============

# import packages/modules
import os
import yaml
import pandas as pd
# local


class ManageData():
    # main data
    __reference = {}
    # databook bulk
    __databook_bulk = {}
    # databook
    __databook = []
    # table
    __tables = []

    def __init__(self):
        # load reference
        self.__reference = self.load_reference()

        # databook bulk
        self.__databook_bulk = self.get_databook_bulk()

        # databook
        self.__databook = list(self.__databook_bulk.keys())

    @property
    def reference(self):
        return self.__reference

    @property
    def databook(self):
        return self.__databook

    @databook.setter
    def databook(self, value):
        self.__databook = []
        self.__databook = value

    @property
    def databook_bulk(self):
        return self.__databook_bulk

    @databook_bulk.setter
    def databook_bulk(self, value):
        self.__databook_bulk = {}
        self.__databook_bulk = value

    @property
    def tables(self):
        return self.__tables

    @tables.setter
    def tables(self, value):
        self.__tables = []
        self.__tables = value

    def load_reference(self):
        '''
        load reference data from file
        '''
        config_path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), '..', 'config', 'reference.yml')

        with open(config_path, 'r') as f:
            reference = yaml.load(f, Loader=yaml.FullLoader)

        return reference

    def get_databook_bulk(self):
        '''
        Get databook bulk

        Returns
        -------
        databook_list : dict
            databook dict
        '''
        try:
            databook_list = {}
            references = self.__reference['REFERENCES']

            for databook, databook_data in references.items():
                tables = []
                for table, table_data in databook_data.get('TABLES', {}).items():
                    # check EQUATIONS exists
                    if 'EQUATIONS' in table_data:
                        # eq
                        _eq = []
                        for eq, eq_data in table_data['EQUATIONS'].items():
                            # save
                            _eq.append(eq_data)

                        # save
                        tables.append({
                            'table': table,
                            'equations': _eq,
                            'data': None
                        })
                        # reset
                        _eq = []
                    # check DATA
                    elif 'DATA' in table_data:
                        # save
                        tables.append({
                            'table': table,
                            'equations': None,
                            'data': table_data['DATA']
                        })
                databook_list[databook] = tables
            # return
            return databook_list
        except Exception as e:
            raise Exception(e)

    def get_databooks(self):
        '''
        Get a list of databook

        Parameters
        ----------
        None

        Returns
        -------
        databook : list
            list of databook
        '''
        try:
            # databook list
            _db = list(self.__databook_bulk.keys())
            # add id
            res = [(db, f"[{i+1}]") for i, db in enumerate(_db)]
            # dataframe
            # column name
            column_name = "Databooks"
            databook_df = pd.DataFrame(res, columns=[column_name, "id"])
            # return
            return _db, databook_df

        except Exception as e:
            raise Exception(f"databook loading error! {e}")

    def get_tables(self, databook):
        '''
        Get a table list of selected databook

        Parameters
        ----------
        databook : str
            databook name

        Returns
        -------
        tables : list
            table list of selected databook

        '''
        try:
            # list tables
            if isinstance(databook, str):
                _dbs = self.__databook_bulk[databook]
            elif isinstance(databook, int):
                _dbs = self.__databook_bulk[self.__databook[databook]]
            # list
            tables = []
            # check table and equations
            for i, tb in enumerate(_dbs):
                if tb['equations'] is not None:
                    tables.append([tb['table'], "equation",
                                  f"[{i+1}]"])
                else:
                    tables.append(
                        [tb['table'], "data", f"[{i+1}]"])
            # dataframe
            # column name
            column_name = f"Tables in {databook}"
            tables_df = pd.DataFrame(
                tables, columns=[column_name, "Type", "Id"])
            # return
            return tables, tables_df
        except Exception as e:
            raise Exception(f"table loading err! {e}")

    def get_table(self, databook, table_id):
        '''
        Get a table list of selected databook

        Parameters
        ----------
        databook : str
            databook name
        table_id : int
            table id

        Returns
        -------
        tables : list
            table list of selected databook
        '''
        try:
            # select databook
            if isinstance(databook, str):
                databook = self.databook_bulk[databook]
            elif isinstance(databook, int):
                databook = self.databook_bulk[self.__databook[databook]]

            # list
            selected_tb = {}
            # check table and equations
            for i, tb in enumerate(databook):
                # check table id
                if i == table_id:
                    selected_tb = tb

            # return
            return selected_tb
        except Exception as e:
            raise Exception(f"table loading err! {e}")

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
