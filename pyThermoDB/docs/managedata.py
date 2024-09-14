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
    # reference local
    __reference_local_no = 0
    # databook bulk
    __databook_bulk = {}
    # databook
    __databook = []
    # databook local
    __databook_local = []
    # table
    __tables = []

    def __init__(self, custom_ref=None):
        # external reference
        self.custom_ref = custom_ref
        # load reference
        self.__reference = self.load_reference(custom_ref)

        # databook bulk
        self.__databook_bulk = self.get_databook_bulk()

        # databook
        self.__databook = list(self.__databook_bulk.keys())

    @property
    def reference(self):
        return self.__reference

    @property
    def reference_local_no(self):
        return self.__reference_local_no

    @reference_local_no.setter
    def reference_local_no(self, value):
        self.__reference_local_no = value

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

    def load_reference(self, custom_ref):
        '''
        load reference data from file
        '''
        # Get the directory of the current script
        # script_dir = os.path.dirname(os.path.realpath(__file__))

        # Construct the path to the YAML file
        # config_path = os.path.join(script_dir, '..', 'config', 'reference.yml')

        # config_path = os.path.join(os.path.abspath(
        #     os.path.dirname(__file__)), '..', 'config', 'reference.yml')

        # relative
        # config_path = os.path.join(os.path.dirname(
        #     os.path.realpath(__file__)), '..', 'config', 'reference.yml')

        # current dir
        current_path = os.path.join(os.path.dirname(__file__))

        # Go back to the parent directory (pyThermoDB)
        parent_path = os.path.abspath(os.path.join(current_path, '..'))

        # Now navigate to the data folder
        data_path = os.path.join(parent_path, 'config')

        # relative
        config_path = os.path.join(data_path, 'reference.yml')

        with open(config_path, 'r') as f:
            reference = yaml.load(f, Loader=yaml.FullLoader)

        # update reference local
        self.__reference_local_no = len(reference['REFERENCES'])

        # check custom reference
        if custom_ref:
            # get data
            custom_reference = custom_ref.load_ref()
            # merge data
            reference['REFERENCES'].update(custom_reference)

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
