# MANAGE DATA
# ===============

# import packages/modules
import os
import yaml
import pandas as pd
from typing import TypedDict, List, Optional
import json
# local
from ..data import TableTypes
from ..models import DataBookTableTypes
from .customref import CustomRef


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

    def __init__(self, custom_ref: Optional[CustomRef] = None):
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

    def load_reference(self, custom_ref: CustomRef) -> dict[str, dict]:
        '''
        load reference data from file

        Parameters
        ----------
        custom_ref : str
            custom reference file path to reference file

        Returns
        -------
        reference : dict
            reference data
        '''
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

        # log
        # <class 'dict'>
        # print(type(reference))
        return reference

    def get_databook_bulk(self) -> dict[str, list[DataBookTableTypes]]:
        '''
        Get databook bulk

        Parameters
        ----------
        None

        Returns
        -------
        databook_list : dict
            databook dict
        '''
        try:
            databook_list = {}
            references = self.__reference['REFERENCES']

            for databook, databook_data in references.items():
                # log
                # <class 'str'> <class 'dict'>
                # print(type(databook), type(databook_data))
                tables = []
                for table, table_data in databook_data.get('TABLES', {}).items():
                    # log
                    # <class 'str' > <class 'dict' >
                    # print(type(table), type(table_data))
                    # * check
                    # ! check EQUATIONS exists
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
                            'data': None,
                            'matrix_equations': None,
                            'matrix_data': None,
                        })
                        # reset
                        _eq = []
                    # ! check MATRIX-EQUATION
                    elif 'MATRIX-EQUATIONS' in table_data:
                        # eq
                        _eq = []
                        for eq, eq_data in table_data['MATRIX-EQUATIONS'].items():
                            # save
                            _eq.append(eq_data)

                        # save
                        tables.append({
                            'table': table,
                            'equations': None,
                            'data': None,
                            'matrix_equations': _eq,
                            'matrix_data': None,
                        })
                        # reset
                        _eq = []
                    # ! check DATA
                    elif 'DATA' in table_data:
                        # data
                        data = table_data['DATA']
                        # save
                        tables.append({
                            'table': table,
                            'equations': None,
                            'data': data,
                            'matrix_equations': None,
                            'matrix_data': None,
                        })
                    # ! check MATRIX-DATA
                    elif 'MATRIX-DATA' in table_data:
                        # matrix-data
                        matrix_data = table_data['MATRIX-DATA']
                        # save
                        tables.append({
                            'table': table,
                            'equations': None,
                            'data': None,
                            'matrix_equations': None,
                            'matrix_data': matrix_data
                        })

                # save
                databook_list[databook] = tables
                # log
                # print(type(databook_list))
            # return
            return databook_list
        except Exception as e:
            raise Exception(f"databook loading error! {e}")

    def get_databooks(self) -> tuple[list[str], pd.DataFrame, str]:
        '''
        Get a list of databook

        Parameters
        ----------
        None

        Returns
        -------
        _db : list
            databook list
        databook_df : pd.DataFrame
            databook dataframe
        databook_json : str
            databook json

        Notes
        ------
        1. _db is the name of all books (databooks)
        '''
        try:
            # databook list
            _db = list(self.__databook_bulk.keys())
            # add id
            res = [(db, f"[{i+1}]") for i, db in enumerate(_db)]

            # create dict
            databook_dict = {f"databook-{i+1}": str(db)
                             for i, db in enumerate(_db)}
            # create json
            databook_json = json.dumps(databook_dict, indent=4)

            # dataframe
            # column name
            column_name = "Databooks"
            databook_df = pd.DataFrame(res, columns=[column_name, "Id"])
            # return
            return _db, databook_df, databook_json

        except Exception as e:
            raise Exception(f"databook loading error! {e}")

    def get_tables(self, databook) -> tuple[list[list[str]], pd.DataFrame, str]:
        '''
        Get a table list of selected databook

        Parameters
        ----------
        databook : str
            databook name

        Returns
        -------
        tables : list | pandas.DataFrame | str
            table list of selected databook
        '''
        try:
            # list tables
            if isinstance(databook, str):
                _dbs = self.__databook_bulk[databook]
            elif isinstance(databook, int):
                _dbs = self.__databook_bulk[self.__databook[databook]]
            # list
            tables: list[list[str]] = []
            # check table and equations
            for i, tb in enumerate(_dbs):
                # check
                # ! equation
                if tb['equations'] is not None:
                    tables.append([tb['table'], "equation",
                                  f"[{i+1}]"])
                # ! data
                elif tb['data'] is not None:
                    tables.append([tb['table'], "data", f"[{i+1}]"])
                # ! matrix-data
                elif tb['matrix_data'] is not None:
                    tables.append(
                        [tb['table'], "matrix-data", f"[{i+1}]"])
                # ! matrix-equation
                elif tb['matrix_equations'] is not None:
                    tables.append(
                        [tb['table'], "matrix-equation", f"[{i+1}]"])
                else:
                    raise Exception("data type unknown!")

            # dataframe
            # column name
            column_name = f"Tables in {databook} databook"

            # convert to json
            tables_dict = {f"table-{i+1}": tb[0]
                           for i, tb in enumerate(tables)}
            # convert to json
            tables_json = json.dumps(tables_dict, indent=4)

            # ! set table dataframe
            tables_df = pd.DataFrame(
                tables, columns=[column_name, "Type", "Id"])
            # return
            return tables, tables_df, tables_json
        except Exception as e:
            raise Exception(f"table loading err! {e}")

    def get_table_type(self, databook: int, table_id: int) -> str:
        '''
        Get a table type

        Parameters
        ----------
        databook : int
            databook id (non-zero-based)
        table_id : int
            table id (non-zero-based)

        Returns
        -------
        table_type : str
            table type
        '''
        try:
            # get table
            tb = self.get_table(databook-1, table_id-1)

            # filter
            filter_keys = [enum.value for enum in TableTypes]

            # table data type
            tb_bulk = {key: value for key, value in tb.items(
            ) if key in filter_keys and value is not None}

            # table type
            tb_type = ''

            # check
            if len(tb_bulk) == 1:
                tb_type, _ = tb_bulk.popitem()
            else:
                raise Exception("table type unknown!")

            # return
            return tb_type

        except Exception as e:
            raise Exception(f"table info loading err! {e}")

    def get_table(self, databook: str | int | list[DataBookTableTypes], table_id: int) -> DataBookTableTypes:
        '''
        Get a table list of selected databook

        Parameters
        ----------
        databook : str | int | list
            databook name or id (zero-based id)
        table_id : int
            table id (zero-based id)

        Returns
        -------
        tables : list
            table list of selected databook
        '''
        try:
            # select databook
            if isinstance(databook, str):
                databook_set = self.databook_bulk[databook]
            elif isinstance(databook, int):
                databook_set = self.databook_bulk[self.__databook[databook]]
            else:
                databook_set = databook

            # ! if databook list
            # list
            selected_tb = {}
            # check table and equations
            for i, tb in enumerate(databook_set):
                # check table id
                if i == table_id:
                    selected_tb = tb

            # return
            return selected_tb
        except Exception as e:
            raise Exception(f"table loading err! {e}")

    def find_databook(self, databook: str | int) -> tuple[list[DataBookTableTypes], str, int]:
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

        Notes
        -----
        if databook is int, the zero-based id is returned
        '''
        try:
            # set
            databook_name = ''

            # check
            if isinstance(databook, int):
                # convert to zero-based id
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
            raise Exception(f"databook finding err! {e}")

    def find_table(self, databook: str | int, table: str | int) -> tuple[int, str]:
        '''
        Finds table id through searching databook id and table name

        Parameters
        ----------
        databook : int | str
            databook id or name
        table : id | str
            table name

        Returns
        -------
        table_id : int
            table id (zero-based)
        table_name : str
            table name

        Notes
        -----
        if table is int, the zero-based id is returned
        '''
        try:
            # set
            table_id, table_name = 0, ''

            # find databook zero-base id (real)
            selected_databook, databook_name, databook_id = self.find_databook(
                databook)

            # check table
            if isinstance(table, int):
                # convert to zero-based id
                table_id = table-1
                # table name
                table_name = selected_databook[table_id]['table']
            elif isinstance(table, str):
                # find table id
                for i, tb in enumerate(selected_databook):
                    if tb['table'] == table.strip():
                        table_id = i
                        # table name
                        table_name = tb['table']
                        break
            else:
                raise ValueError("table must be int or str")

            # return
            return table_id, table_name

        except Exception as e:
            raise Exception('Finding table id failed!, ', e)
