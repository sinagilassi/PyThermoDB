# MANAGE DATA
# ===============

# import packages/modules
import os
import yaml
import pandas as pd
import logging
from typing import (
    List,
    Optional,
    Literal,
    Dict,
    Any
)
import json
import re
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
    # symbol list
    __symbols = {}
    # description
    __description = {}

    def __init__(self, custom_ref: Optional[CustomRef] = None):
        # external reference
        self.custom_ref = custom_ref
        # load reference
        self.__reference = self.load_reference(custom_ref)

        # symbols
        self.__symbols = self.load_symbols(custom_ref)

        # description
        self.__description = self.load_descriptions()

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
    def symbols(self):
        return self.__symbols

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

    def load_reference(self, custom_ref: CustomRef | None) -> dict[str, dict]:
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

    @staticmethod
    def load_custom_reference(
        custom_ref: CustomRef,
        save_to_file: bool = False,
        file_format: Literal['txt', 'yml'] = 'txt',
        file_name: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any] | None:
        '''
        Load custom reference data from file

        Parameters
        ----------
        custom_ref : CustomRef | None
            custom reference object
        save_to_file : bool, optional
            If True, save the custom reference to a txt file, by default False
        file_format : Literal['txt', 'yml'], optional
            Format of the file to save the custom reference, by default 'txt'. Options are 'txt' or 'yml'.
        file_name : str, optional
            Name of the file to save the custom reference, by default None.
        output_dir : str, optional
            Directory to save the custom reference file, by default None.

        Returns
        -------
        dict[str, dict]
            custom reference data
        '''
        try:
            # NOTE: check custom_ref
            if not isinstance(custom_ref, CustomRef):
                logging.warning("Custom reference is not provided or invalid!")
                return {}

            # NOTE: load custom reference
            if custom_ref:
                # check if directory is provided
                if output_dir is None:
                    # use current working directory
                    output_dir = os.getcwd()

                # check if directory exists
                if not os.path.exists(output_dir):
                    # create directory
                    os.makedirs(output_dir)

                # SECTION: load custom reference
                ref = custom_ref.load_ref()

                # check if ref is empty
                if not ref:
                    logging.warning("Custom reference is empty!")
                    return {}

                # check if file_name is provided
                if file_name is None:
                    # use default file name
                    if file_format == 'txt':
                        file_name = "custom_reference.txt"
                    elif file_format == 'yml':
                        file_name = "custom_reference.yml"
                    else:
                        logging.warning(
                            "Invalid file format! Use 'txt' or 'yml'.")
                        return {}
                else:
                    # set name
                    file_name = file_name.strip() + f".{file_format}"

                if save_to_file:
                    # build the full file path using directory and file_name
                    file_path = os.path.join(output_dir, file_name)

                    # check file format
                    if file_format == 'txt':
                        # ! to txt file
                        with open(file_path, "w") as f:
                            # `indent=4` for nice formatting
                            json.dump(ref, f, indent=4)
                    elif file_format == 'yml':
                        # ! to yaml file
                        with open(file_path, "w") as f:
                            # `default_flow_style=False` for nice formatting
                            yaml.dump(ref, f, sort_keys=False)
                    else:
                        logging.warning(
                            "Invalid file format! Use 'txt' or 'yml'.")

                return ref
            else:
                return {}
        except Exception as e:
            logging.error(f"Error loading custom reference: {e}")
            return {}

    def select_reference(self, reference: str) -> dict:
        '''
        Select a reference from the loaded references

        Parameters
        ----------
        reference : str
            reference name

        '''
        try:
            # check
            if reference not in self.__reference['REFERENCES']:
                raise ValueError(f"Reference {reference} not found!")

            # get reference
            selected_ref = self.__reference['REFERENCES'][reference]

            # return
            return selected_ref
        except Exception as e:
            raise Exception(f"select reference error! {e}")

    def load_symbols(self, custom_ref: CustomRef | None) -> dict:
        '''
        Load symbols used in the databooks

        Parameters
        ----------
        None

        Returns
        -------
        symbols : list
            list of symbols
        '''
        try:
            # current dir
            current_path = os.path.join(os.path.dirname(__file__))

            # Go back to the parent directory (pyThermoDB)
            parent_path = os.path.abspath(os.path.join(current_path, '..'))

            # Now navigate to the data folder
            data_path = os.path.join(parent_path, 'config')

            # relative
            config_path = os.path.join(data_path, 'symbols.yml')

            with open(config_path, 'r') as f:
                symbols = yaml.load(f, Loader=yaml.FullLoader)

            # check custom symbols
            if custom_ref:
                # get data
                custom_symbols = custom_ref.load_symbols()
                # check
                if len(custom_symbols) > 0:
                    # merge data
                    symbols['SYMBOLS'].update(custom_symbols)

            # return
            return symbols
        except Exception as e:
            raise Exception(f"symbol loading error! {e}")

    def load_descriptions(self):
        """
        Load reference descriptions for databooks
        """
        try:
            # references
            references = self.__reference['REFERENCES']

            # descriptions
            descriptions = {}

            for key, value in references.items():
                # databook name
                databook_name = key
                # databook id
                DATABOOK_ID = value.get('DATABOOK-ID', None)

                # init
                descriptions[databook_name] = {}
                # set
                descriptions[databook_name]['DATABOOK-ID'] = DATABOOK_ID

                # check tables
                for table, table_data in value.get('TABLES', {}).items():
                    # check
                    if 'DESCRIPTION' in table_data:
                        descriptions[databook_name][table] = {
                            'DATABOOK-ID': DATABOOK_ID,
                            'TABLE-ID': table_data.get('TABLE-ID', None),
                            'DESCRIPTION': table_data['DESCRIPTION']
                        }
                    else:
                        descriptions[databook_name][table] = {
                            'DATABOOK-ID': DATABOOK_ID,
                            'TABLE-ID': table_data.get('TABLE-ID', None),
                            'DESCRIPTION': None
                        }

            # return
            return descriptions
        except Exception as e:
            raise Exception(f"load_descriptions error! {e}")

    def get_symbols(self) -> tuple[dict, list, str, pd.DataFrame]:
        '''
        Get symbols

        Parameters
        ----------
        None

        Returns
        -------
        symbols : dict
            symbols
        '''
        try:
            # dict
            res = self.symbols['SYMBOLS']
            # list
            res_list = [(value, key) for key, value in res.items()]
            # json
            res_json = json.dumps(res, indent=4)
            # dataframe
            res_df = pd.DataFrame(res_list, columns=['Symbol', 'Description'])

            # res
            return res, res_list, res_json, res_df

        except Exception as e:
            raise Exception(f"symbol loading error! {e}")

    def get_descriptions(self) -> tuple[dict, list, str, pd.DataFrame]:
        '''
        Get databook descriptions
        '''
        try:
            # dict
            res = self.__description
            # list
            res_list = [(value, key) for key, value in res.items()]
            # json
            res_json = json.dumps(res, indent=4)
            # dataframe
            res_df = pd.DataFrame(res_list, columns=['Tables', 'Descriptions'])

            # res
            return res, res_list, res_json, res_df
        except Exception as e:
            raise Exception(f"description loading error! {e}")

    def get_descriptions_by_databook(self, databook: str) -> dict:
        '''
        Get descriptions by databook

        Parameters
        ----------
        databook : str
            databook name

        Returns
        -------
        descriptions : dict
            descriptions of the databook
        '''
        try:
            # check
            if databook not in self.__description:
                raise ValueError(f"Databook {databook} not found!")

            # get descriptions
            descriptions = self.__description[databook]

            # return
            return descriptions
        except Exception as e:
            raise Exception(f"description loading error! {e}")

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
                # databook name
                # databook_name = databook

                # databook id
                # databook_id = databook_data.get('DATABOOK-ID', None)

                tables = []
                for table, table_data in databook_data.get('TABLES', {}).items():
                    # log
                    # <class 'str' > <class 'dict' >
                    # print(type(table), type(table_data))

                    # NOTE: description
                    description = table_data.get('DESCRIPTION', None)

                    # NOTE: table id
                    table_id = table_data.get('TABLE-ID', -1)

                    # NOTE: table values
                    table_values = table_data.get('VALUES', None)

                    # NOTE: table structure
                    table_structure = table_data.get('STRUCTURE', None)

                    # NOTE: table reference
                    external_references = table_data.get(
                        'EXTERNAL-REFERENCES', None)

                    # SECTION: reference indicators
                    # ? DATA,
                    # ? EQUATIONS,
                    # ? MATRIX-DATA OR MATRIX-SYMBOL,
                    # ? MATRIX-EQUATIONS
                    # ! check EQUATIONS exists
                    if 'EQUATIONS' in table_data:
                        # eq
                        _eq = []
                        for eq, eq_data in table_data['EQUATIONS'].items():
                            # save
                            _eq.append(eq_data)

                        # NOTE: parse equations
                        _eq_formatted = self.__eq_formatter(_eq)

                        # save
                        tables.append({
                            'table_id': table_id,
                            'table': table,
                            'description': description,
                            'equations': _eq_formatted,
                            'data': None,
                            'matrix_equations': None,
                            'matrix_data': None,
                            'table_type': TableTypes.EQUATIONS.value,
                            'table_values': table_values,
                            'table_structure': table_structure,
                            'external_references': external_references
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
                            'table_id': table_id,
                            'table': table,
                            'description': description,
                            'equations': None,
                            'data': None,
                            'matrix_equations': _eq,
                            'matrix_data': None,
                            'table_type': TableTypes.MATRIX_EQUATIONS.value,
                            'table_values': table_values,
                            'table_structure': table_structure,
                            'external_references': external_references
                        })
                        # reset
                        _eq = []
                    # ! check DATA
                    elif 'DATA' in table_data:
                        # data
                        data = table_data.get('DATA', [])

                        # REVIEW: generate table structure
                        table_structure = data if table_structure is None else table_structure
                        # set
                        if isinstance(data, list):
                            # check data
                            if len(data) == 0:
                                data = table_structure

                        # save
                        tables.append({
                            'table_id': table_id,
                            'table': table,
                            'description': description,
                            'equations': None,
                            'data': data,
                            'matrix_equations': None,
                            'matrix_data': None,
                            'table_type': TableTypes.DATA.value,
                            'table_values': table_values,
                            'table_structure': table_structure,
                            'external_references': external_references
                        })
                    # ! check MATRIX-DATA
                    elif ('MATRIX-DATA' in table_data) or ('MATRIX-SYMBOL' in table_data):
                        # matrix-data (data)
                        # NOTE: matrix-data
                        # including COLUMNS, SYMBOL, UNIT, CONVERSION, MATRIX-SYMBOL
                        matrix_data = table_data.get('MATRIX-DATA', {})

                        # NOTE: matrix-symbol
                        matrix_symbol = table_data.get('MATRIX-SYMBOL', None)

                        # embedded symbol
                        if matrix_symbol:
                            matrix_data['MATRIX-SYMBOL'] = matrix_symbol

                        # NOTE: table items
                        table_items = table_data.get('ITEMS', None)

                        # embedded symbol
                        if table_items:
                            matrix_data['ITEMS'] = table_items

                        # NOTE: table structure
                        if table_structure is not None:
                            # update
                            for k, v in table_structure.items():
                                # update
                                matrix_data[k] = v

                        # save
                        tables.append({
                            'table_id': table_id,
                            'table': table,
                            'description': description,
                            'equations': None,
                            'data': None,
                            'matrix_equations': None,
                            'matrix_data': matrix_data,
                            'table_type': TableTypes.MATRIX_DATA.value,
                            'table_values': table_values,
                            'table_structure': table_structure,
                            'table_items': table_items,
                            'external_references': external_references
                        })

                # save
                databook_list[databook] = tables

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

    def get_databook_id(
        self,
        databook: str,
        res_format: Literal[
            'str', 'json', 'dict', 'int'
        ] = 'json'
    ) -> str | int | dict[str, str]:
        '''
        Get databook id

        Parameters
        ----------
        databook : str | int | dict
            databook name

        Returns
        -------
        databook_id : str
            databook id

        Notes
        -----
        1. databook id is non-zero-based
        2. if databook is not found, 'Databook not found!' is returned
        '''
        try:
            # check
            if not isinstance(databook, str):
                raise Exception("databook must be string!")

            # find
            for i, db in enumerate(self.__databook):
                if db == databook:
                    db_id = str(i+1)

                    # check
                    if res_format == 'str':
                        return db_id
                    elif res_format == 'int':
                        return int(db_id)
                    elif res_format == 'json':
                        return json.dumps({"databook_id": db_id}, indent=4)
                    elif res_format == 'dict':
                        return {"databook_id": db_id}
                    else:
                        raise ValueError(
                            "res_format must be 'str', 'json', or 'dict'!")
            # return
            return 'Databook not found!'
        except Exception as e:
            raise Exception(f"databook id loading error! {e}")

    def get_tables(self, databook) -> tuple[list[list[str]], pd.DataFrame, str, dict[str, str]]:
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
            return tables, tables_df, tables_json, tables_dict
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

    def get_table(self,
                  databook: str | int | list[DataBookTableTypes],
                  table: int | str) -> DataBookTableTypes:
        '''
        Get a table with respect to databook and table id or name

        Parameters
        ----------
        databook : str | int | list
            databook name or id (zero-based id)
        table : int
            table id (zero-based id) or name

        Returns
        -------
        table : DataBookTableTypes
            selected table based on databook and table id or name
        '''
        try:
            # select databook
            if isinstance(databook, str):
                databook_set = self.databook_bulk[databook]
            elif isinstance(databook, int):
                databook_set = self.databook_bulk[self.__databook[databook]]
            else:
                # for previously extracted databook
                databook_set = databook

            # ! if databook list
            # list
            # selected_tb: DataBookTableTypes
            selected_tb = None

            # SECTION: set table type
            def set_table_type(tb):
                # check table type
                if 'equations' in tb and tb['equations'] is not None:
                    return TableTypes.EQUATIONS.value
                elif 'data' in tb and tb['data'] is not None:
                    return TableTypes.DATA.value
                elif 'matrix_data' in tb and tb['matrix_data'] is not None:
                    return TableTypes.MATRIX_DATA.value
                elif 'matrix_equations' in tb and tb['matrix_equations'] is not None:
                    return TableTypes.MATRIX_EQUATIONS.value
                else:
                    raise Exception("table type unknown!")

            # by table id
            if isinstance(table, int):
                # check table and equations
                for i, tb in enumerate(databook_set):
                    # check table id
                    if i == table:
                        selected_tb = DataBookTableTypes(**tb)
                        # NOTE: check table type
                        # tb_name_ = selected_tb['table']
                        # set
                        selected_tb['table_type'] = set_table_type(tb)
                        break
            # by table name
            elif isinstance(table, str):
                # check table name
                for i, tb in enumerate(databook_set):
                    # check table name
                    if tb['table'] == table:
                        selected_tb = DataBookTableTypes(**tb)
                        # NOTE: check table type
                        # tb_name_ = selected_tb['table']
                        # set
                        selected_tb['table_type'] = set_table_type(tb)
                        break
            else:
                raise Exception("Invalid table type")

            # NOTE: check selected table
            if selected_tb is None:
                raise Exception("table not found!")
            # return
            return selected_tb
        except Exception as e:
            raise Exception(f"table loading err! {e}")

    def get_table_id(self,
                     databook: str | int,
                     table: str,
                     res_format: Literal[
                         'str', 'json', 'dict'
                     ] = 'json') -> str | dict[str, str]:
        '''
        Get table id

        Parameters
        ----------
        databook : str | int
            databook name or id
        table : str
            table name

        Returns
        -------
        table_id : str | dict[str, str]
            table id
        '''
        try:
            # select databook
            if isinstance(databook, str):
                databook_set = self.databook_bulk[databook]
            elif isinstance(databook, int):
                databook_set = self.databook_bulk[self.__databook[databook]]
            else:
                raise ValueError("databook must be str or int!")

            # table id
            table_id = 'Table id not found!'

            # check table and equations
            for i, tb in enumerate(databook_set):
                # check table id
                if tb['table'] == table:
                    table_id = str(i+1)
                    break

            # check
            if res_format == 'str':
                return table_id
            elif res_format == 'json':
                return json.dumps({"table_id": table_id}, indent=4)
            elif res_format == 'dict':
                return {"table_id": table_id}
            else:
                raise ValueError("res_format must be 'str' or 'json'!")

        except Exception as e:
            raise Exception(f"table id loading err! {e}")

    def get_table_values(self, databook: str | int, table: str | int):
        '''
        Get table values

        Parameters
        ----------
        databook : str | int
            databook name or id
        table : str | int
            table name or id

        Returns
        -------
        table_values : list
            table values
        '''
        try:
            # NOTE: find databook
            db, db_name, db_id = self.find_databook(databook)

            # NOTE: find table
            tb_id, tb_name = self.find_table(db_name, table)

            # NOTE: get table
            tb = self.get_table(db_name, tb_name)

            return tb

        except Exception as e:
            raise Exception(f"table values loading err! {e}")

    def find_databook(self,
                      databook: str | int
                      ) -> tuple[list[DataBookTableTypes], str, int]:
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

    def find_table_source(self, table: str | int) -> dict[str, str | int]:
        """
        Find table source (databook name and id)

        Parameters
        ----------
        table : str | int
            table name or id (non-zero-based)

        Returns
        -------
        dict :
            databook_name : str
                databook name
            databook_id : int
                databook id
            table_name : str
                table name
            table_id : int
                table id

        """
        try:
            # set
            table_id, table_name = 0, ''
            databook_id = 0
            db = ''

            # check table
            for i, db in enumerate(self.databook):
                # get databook name and id
                # databook_name, databook_id = db['name'], i
                databook_id = self.get_databook_id(db, res_format='int')
                # check
                if not isinstance(databook_id, int):
                    raise ValueError("databook id must be int!")
                if databook_id == 0:
                    raise ValueError("databook id must be non-zero-based!")

                # find table
                for j, tb in enumerate(self.databook_bulk[db]):
                    if isinstance(table, int):

                        # check
                        if table == 0:
                            raise ValueError(
                                "table id must be non-zero-based!")

                        # check
                        if tb['table_id'] == table:
                            table_id = tb['table_id']
                            table_name = tb['table']

                            # check
                            if not table_id:
                                raise ValueError("table id not found!")

                            # get data type
                            data_type = self.get_table_type(
                                databook_id, int(table_id))

                            # return
                            return {
                                'databook_name': db,
                                'databook_id': databook_id,
                                'table_name': table_name,
                                'table_id': table_id,
                                'data_type': data_type
                            }

                    elif isinstance(table, str):
                        # check
                        if tb['table'] == table.strip():
                            table_id = tb['table_id']
                            table_name = tb['table']

                            # check
                            if not table_id:
                                raise ValueError("table id not found!")

                            # get data type
                            data_type = self.get_table_type(
                                databook_id, int(table_id))

                            # return
                            return {
                                'databook_name': db,
                                'databook_id': databook_id,
                                'table_name': table_name,
                                'table_id': table_id,
                                'data_type': data_type
                            }
                    else:
                        raise ValueError("table must be int or str")

            # return
            return {}
        except Exception as e:
            raise Exception('Finding table source failed!', e)

    def __parse_equation(self, eq_data: List[str]):
        '''
        Parse equation data into a dictionary including equation args, parameters, returns

        Parameters
        ----------
        eq_data : dict
            equation data
        '''
        try:
            # check
            if not isinstance(eq_data, list):
                raise ValueError("eq_data must be a list!")

            # init
            eq_dict = {}
            eq_dict['ARGS'] = {}
            eq_dict['PARMS'] = {}
            eq_dict['RETURNS'] = {}
            eq_dict['BODY'] = []

            # NOTE: value generator
            def val_generator(d):
                '''Generate value'''
                # check 3 |
                if "|" in d:
                    # split
                    match_res = d.split("|")
                    # check
                    if len(match_res) != 3:
                        raise ValueError(
                            f"{d} must be 3 elements!")

                    # key
                    key = match_res[0].strip()
                    # name
                    name = key
                    # symbol
                    symbol = match_res[1].strip()
                    # unit
                    unit = match_res[2].strip()

                    # set
                    val = {
                        'name': name,
                        'symbol': symbol,
                        'unit': unit
                    }
                else:
                    raise Exception(
                        f"Invalid value format! {d} must be 3 elements!")

                return key, val

            # SECTION: parse equation data
            # loop through eq_data
            for eq in eq_data:
                # check
                if isinstance(eq, str):
                    # parse equation body
                    body_ = eq

                    # NOTE: parse to extract args
                    # regex
                    regex = r"args\['([^']+)'\]"
                    # find all matches
                    matches = re.findall(regex, body_)
                    # check
                    if matches:
                        # loop through matches
                        for match in matches:
                            # ! val generator
                            key, val = val_generator(match)
                            symbol = val['symbol']
                            # check
                            if match not in eq_dict['ARGS']:
                                # set
                                eq_dict['ARGS'][key] = val
                                # set body
                                body_ = body_.replace(
                                    f"'{match}'", f"'{symbol}'")

                    # NOTE: parse to extract parameters
                    # regex
                    regex = r"parms\['([^']+)'\]"
                    # find all matches
                    matches = re.findall(regex, body_)
                    # check
                    if matches:
                        # loop through matches
                        for match in matches:
                            # ! val generator
                            key, val = val_generator(match)
                            symbol = val['symbol']
                            # check
                            if match not in eq_dict['PARMS']:
                                # set
                                eq_dict['PARMS'][key] = val
                                # set body
                                body_ = body_.replace(
                                    f"'{match}'", f"'{symbol}'")

                    # NOTE: parse to extract returns
                    # regex
                    regex = r"res\['([^']+)'\]"
                    # find all matches
                    matches = re.findall(regex, body_)
                    # check
                    if matches:
                        # loop through matches
                        for match in matches:
                            # ! val generator
                            key, val = val_generator(match)
                            symbol = val['symbol']
                            # check
                            if match not in eq_dict['RETURNS']:
                                # set
                                eq_dict['RETURNS'][key] = val
                                # set body
                                body_ = body_.replace(f"res['{match}']", "res")

                # updated body
                # set body
                eq_dict['BODY'].append(body_)
            # return
            return eq_dict
        except Exception as e:
            raise Exception(f"parse_equation error! {e}")

    def __eq_formatter(self, eqs: List):
        '''
        Format equations
        '''
        try:
            # NOTE: eqs
            eqs_formatted = []

            # NOTE: check eqs
            for eq in eqs:
                # check keys
                if "ARGS" not in eq or "PARMS" not in eq or "RETURNS" not in eq:
                    # parse eq to generate equation structure
                    eq_ = self.equation_formatter(eq)
                    eqs_formatted.append(eq_)
                else:
                    eqs_formatted.append(eq)

            # res
            return eqs_formatted
        except Exception as e:
            raise Exception(f"equation formatting error! {e}")

    def equation_formatter(self, equation_src: Dict | str) -> Dict[str, Any]:
        '''
        Check equation format

        Parameters
        ----------
        equation_src : str | dict
            equation source (file path string or dict)
        '''
        try:
            # SECTION: path check
            if isinstance(equation_src, str):
                # check file
                if not os.path.isfile(equation_src):
                    raise FileNotFoundError(f"File not found: {equation_src}")

                # NOTE: load equation file (yml format)
                with open(equation_src, 'r') as f:
                    equations = yaml.load(f, Loader=yaml.FullLoader)
            elif isinstance(equation_src, dict):
                # NOTE: check if dict
                equations = equation_src

            # SECTION: check equation format
            # NOTE: check
            if 'BODY' not in equations.keys():
                raise ValueError("equation key `BODY` not found!")

            # NOTE: get equation body
            body_ = equations['BODY']

            # NOTE: parse
            parse_res = self.__parse_equation(body_)

            # NOTE: check other equations
            body_integral = equations.get('BODY-INTEGRAL', None)
            body_first_derivative = equations.get(
                'BODY-FIRST-DERIVATIVE', None)
            body_second_derivative = equations.get(
                'BODY-SECOND-DERIVATIVE', None)

            # check
            if body_integral is not None:
                # check
                if body_integral != 'None' and body_integral != 'NONE':
                    # parse
                    parse_ = self.__parse_equation(body_integral)
                    # add to res
                    parse_res['BODY-INTEGRAL'] = parse_['BODY']
            else:
                parse_res['BODY-INTEGRAL'] = None

            if body_first_derivative is not None:
                # check
                if body_first_derivative != 'None' and body_first_derivative != 'NONE':
                    # parse
                    parse_ = self.__parse_equation(body_first_derivative)
                    # add to res
                    parse_res['BODY-FIRST-DERIVATIVE'] = parse_['BODY']
            else:
                parse_res['BODY-FIRST-DERIVATIVE'] = None

            if body_second_derivative is not None:
                # check
                if body_second_derivative != 'None' and body_second_derivative != 'NONE':
                    # parse
                    parse_ = self.__parse_equation(body_second_derivative)
                    # add to res
                    parse_res['BODY-SECOND-DERIVATIVE'] = parse_['BODY']
            else:
                parse_res['BODY-SECOND-DERIVATIVE'] = None

            # res
            return parse_res
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {equation_src}")
        except Exception as e:
            raise Exception(f"equation format checker error! {e}")
