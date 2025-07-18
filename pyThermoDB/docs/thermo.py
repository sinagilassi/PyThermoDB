# import packages/modules
import logging
import os
import pandas as pd
from typing import (
    List,
    Dict,
    Optional,
    Literal,
    Union,
    Hashable
)
import json
import webbrowser
import tempfile
# from jinja2 import Environment, FileSystemLoader
# internal
from ..config import API_URL, __version__
from ..api import Manage
from ..utils import isNumber, uppercaseStringList
from .tableref import TableReference
from .transdata import TransData
from .transmatrixdata import TransMatrixData
from .managedata import ManageData
from .tableequation import TableEquation
from .tablematrixequation import TableMatrixEquation
from .tabledata import TableData
from .tablematrixdata import TableMatrixData
from ..data import TableTypes
from ..models import DataBookTableTypes
# web app
from ..ui import Launcher

# SECTION: types
ComponentSearch = Union[
    list[dict[str, str]],
    pd.DataFrame,
    str,
    dict[str, str | dict[str, str]]
]

ListComponents = Union[
    list[str],
    dict[str, list[str]],
    str
]

ListComponentsInfo = Union[
    list[dict[str, str | int]],
    dict[str, dict[str, str | int]],
    str
]

ListDatabookDescriptions = Union[
    dict[str, str | dict[str, str]],
    list[str],
    str,
    pd.DataFrame
]

ThermoProperty = Union[
    TableEquation,
    TableData,
    TableMatrixEquation,
    TableMatrixData
]


class ThermoDB(ManageData):
    '''
    Setting class
    '''
    # selected databook
    __selected_databook = ''
    # selected table
    __selected_tb = ''

    def __init__(self, custom_ref=None, data_source='local'):
        self.data_source = data_source
        self.custom_ref = custom_ref
        # ManageData init
        ManageData.__init__(self, custom_ref=custom_ref)

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

    def list_symbols(
            self,
            res_format: Literal[
                'dict', 'list', 'dataframe', 'json'
            ] = 'dataframe'):
        '''
        List all symbols

        Parameters
        ----------
        res_format : Literal['dict', 'list', 'dataframe', 'json']
            Format of the returned data. Defaults to 'dataframe'.
        '''
        try:
            # load symbols
            res = self.get_symbols()

            # check format
            if res_format == 'dict':
                return res[0]
            elif res_format == 'list':
                return res[1]
            elif res_format == 'json':
                return res[2]
            elif res_format == 'dataframe':
                return res[3]
            else:
                raise ValueError('Invalid res_format')

        except Exception as e:
            raise Exception(f"Symbols loading error! {e}")

    def list_descriptions(
            self,
            res_format: Literal[
                'dict', 'list', 'dataframe', 'json'
            ] = 'dataframe'
    ) -> ListDatabookDescriptions:
        '''
        List all descriptions of databooks and tables

        Parameters
        ----------
        res_format : Literal['dict', 'list', 'dataframe', 'json']
            Format of the returned data. Defaults to 'dataframe'.

        Returns
        -------
        res : ListDatabookDescriptions
            List of descriptions in the specified format.
        '''
        try:
            # load descriptions
            res = self.get_descriptions()

            # check
            if res_format == 'dict':
                return res[0]
            elif res_format == 'list':
                return res[1]
            elif res_format == 'json':
                return res[2]
            elif res_format == 'dataframe':
                return res[3]
            else:
                raise ValueError('Invalid python res_format')

        except Exception as e:
            raise Exception(f"Descriptions loading error! {e}")

    def databook_info(
        self,
        databook: int | str,
        res_format: Literal[
            'dict', 'str', 'json'
        ] = 'json'
    ) -> Dict[str, str | Dict[str, str]] | str:
        '''
        Get information about a databook.

        Parameters
        ----------
        databook : int | str
            databook id or name
        res_format : Literal['dict', 'json']
            Format of the returned data. Defaults to 'dict'.

        Returns
        -------
        res : Dict[str, str | Dict[str, str]] | str
            Dictionary containing databook information or a string representation.
            - 'DATABOOK-ID': ID of the databook.
            - 'DATABOOK-NAME': Name of the databook.
            - 'DESCRIPTION': Description of the databook.
        '''
        try:
            # find databook
            db, db_name, db_id = self.find_databook(databook)

            # get databook info
            res = self.get_descriptions_by_databook(db_name)

            # check
            if res_format == 'dict':
                return res
            elif res_format == 'str':
                # convert to json
                return str(res)
            elif res_format == 'json':
                # convert to json
                return json.dumps(res, indent=4)
            else:
                logging.error('Invalid res_format')

            return res
        except Exception as e:
            raise Exception(f"Databook info loading error! {e}")

    def list_databooks(
            self,
            res_format: Literal[
                'list', 'dataframe', 'json'
            ] = 'dataframe'):
        '''
        List all databooks

        Parameters
        -----------
        res_format : Literal['list', 'dataframe', 'json']
            Format of the returned data. Defaults to 'dataframe'.

        Returns
        -------
        res : list | pandas.DataFrame | str
            Databook list in the specified format.
            - 'list': List of dictionaries containing databook information.
            - 'dataframe': Pandas DataFrame containing databook information.
            - 'json': JSON string representing the databook list.
        '''
        try:
            # databook list
            res = self.get_databooks()
            # check
            if res_format == 'list':
                return res[0]
            elif res_format == 'dataframe':
                return res[1]
            elif res_format == 'json':
                return res[2]
            else:
                raise ValueError('Invalid res_format')
        except Exception as e:
            raise Exception(f"databooks loading error! {e}")

    def list_tables(self,
                    databook: int | str,
                    res_format: Literal[
                        'list', 'dataframe', 'json', 'dict'
                    ] = 'dataframe'
                    ) -> list[list[str]] | pd.DataFrame | str | dict[str, str]:
        '''
        List all tables in the selected databook

        Parameters
        ----------
        databook : int | str
            databook id or name
        res_format : Literal['list', 'dataframe', 'json']
            Format of the returned data. Defaults to 'dataframe'.

        Returns
        -------
        table list : list | pandas.DataFrame | str | dict[str, str]
            list of tables
        '''
        try:
            # manual databook setting
            db, db_name, db_id = self.find_databook(databook)
            # table list
            res = self.get_tables(db_name)
            # check
            if res_format == 'list':
                return res[0]
            elif res_format == 'dataframe':
                return res[1]
            elif res_format == 'json':
                return res[2]
            elif res_format == 'dict':
                return res[3]
            else:
                raise ValueError('Invalid res_format')
        except Exception as e:
            raise Exception("Table loading error!,", e)

    def select_table(
        self,
        databook: int | str,
        table: int | str
    ) -> DataBookTableTypes:
        '''
        Select a table structure

        Parameters
        ----------
        databook : int | str
            databook id or name
        table : int | str
            table id or name (non-zero-based id)
        dataframe: book
            if True, return a dataframe

        Returns
        -------
        tb : DataBookTableTypes
            table object
        '''
        try:
            # set
            tb_id = -1
            tb_name = ''

            # find databook
            db, db_name, db_id = self.find_databook(databook)

            # find table
            if isinstance(table, int):
                # tb
                tb = self.get_table(db_name, table-1)
            elif isinstance(table, str):
                # get tables
                tables = self.list_tables(databook=db_name, res_format='list')
                # check
                if isinstance(tables, list):
                    # looping
                    for i, item in enumerate(tables):
                        # check
                        if isinstance(item, list):
                            # table name
                            tb_name = item[0]
                            if tb_name == table.strip():
                                # zero-based id
                                tb_id = i
                                break
                        else:
                            raise ValueError(f"list {item} not found.")
                    # tb
                    # FIXME
                    tb = self.get_table(db, tb_id)
                else:
                    raise ValueError(f"table {table} not found.")
            else:
                raise ValueError("table must be int or str.")

            # res
            return tb
        except Exception as e:
            # Log or print the error for debugging purposes
            raise Exception(
                f"An error occurred while selecting the table: {e}")

    def table_description(
        self,
        databook: int | str,
        table: int | str,
        res_format: Literal[
            'str', 'json', 'dict'
        ] = 'str'
    ) -> str | dict:
        '''
        Get information about a databook.

        Parameters
        ----------
        databook : int | str
            databook id or name
        table : int | str
            table id or name
        res_format : Literal['str', 'json', 'dict']
            Format of the returned data. Defaults to 'str'.

        Returns
        -------
        str | dict
            Description of the table in the specified format.
            - 'str': Returns the description as a string.
            - 'dict': Returns a dictionary with the description.
            - 'json': Returns a JSON string with the description.
        '''
        try:
            # get the tb
            tb = self.select_table(databook, table)

            # check
            if tb:
                # descriptions
                descriptions = tb['description']

                # to dict
                des_dict = {
                    "table-description": descriptions
                }

                # check
                if descriptions:
                    # check
                    if res_format == 'str':
                        return descriptions
                    elif res_format == 'dict':
                        return des_dict
                    elif res_format == 'json':
                        return json.dumps(des_dict)
                    else:
                        raise ValueError('Invalid res_format')
                else:
                    return "No description found!"
            else:
                raise ValueError("No such table found!")

        except Exception as e:
            # Log or print the error for debugging purposes
            raise Exception(
                f"An error occurred while getting the databook info: {e}")

    def table_info(
        self,
        databook: int | str,
        table: int | str,
        res_format: Literal[
            'dict', 'dataframe', 'json'
        ] = 'dataframe'
    ) -> dict[str, int | str] | pd.DataFrame | str:
        '''
        Gives table contents as:

            * Table type
            * Data and equations numbers

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
        tb_summary : dict | pandas.DataFrame | str
            table summary

        Notes
        -----
        1. The default value of dataframe is True, the return value (tb_summary) is Pandas Dataframe
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
            matrix_equation_no = 0
            # data no
            data_no = 0
            matrix_data_no = 0
            # get the tb
            tb = self.select_table(databook, table)

            # check
            if tb:
                # table name
                table_name: str = tb['table']
                # check
                if table_name is None:
                    raise Exception(f"table name {table_name} not found!")

                # check data/equations and matrix-data/matrix-equation
                # tb_type = 'Equation' if tb['equations'] is not None else 'Data'

                if tb['data'] is not None:
                    tb_type = 'Data'
                if tb['equations'] is not None:
                    tb_type = 'Equation'
                if tb['matrix_equations'] is not None:
                    tb_type = 'Matrix-Equation'
                if tb['matrix_data'] is not None:
                    tb_type = 'Matrix-Data'

                # ! check equations
                if tb_type == 'Equation' and tb['equations'] is not None:
                    for item in tb['equations']:
                        table_equations.append(item)

                    # equation no
                    equation_no = len(table_equations)

                # ! check data
                if tb_type == 'Data' and tb['data'] is not None:
                    table_data = [*tb['data']]

                    # data no
                    data_no = 1

                # ! check matrix-equation
                if tb_type == 'Matrix-Equation' and tb['matrix_equations'] is not None:
                    for item in tb['matrix_equations']:
                        table_equations.append(item)

                    # equation no
                    matrix_equation_no = len(table_equations)

                # ! check matrix-data
                if tb_type == 'Matrix-Data' and tb['matrix_data'] is not None:
                    # set
                    table_data = [*tb['matrix_data']]

                    # data no
                    matrix_data_no = 1

                # data
                tb_summary: Dict[str, str | int] = {
                    "Table Name": table_name,
                    "Type": tb_type,
                    "Equations": equation_no,
                    "Data": data_no,
                    "Matrix-Equations": matrix_equation_no,
                    "Matrix-Data": matrix_data_no
                }

                # json
                tb_summary_json = json.dumps(tb_summary)

            else:
                raise ValueError("No such table")

            if res_format == 'dataframe':
                # column names
                column_names = ['Table Name', 'Type', 'Equations',
                                'Data', 'Matrix-Equations', 'Matrix-Data']
                # dataframe
                df = pd.DataFrame([tb_summary], columns=column_names)
                return df
            elif res_format == 'json':
                return tb_summary_json
            elif res_format == 'dict':
                return tb_summary
            else:
                raise ValueError("Invalid res_format")
        except Exception as e:
            raise Exception(f"Table loading error {e}")

    def table_view(self, databook: str | int, table: str | int):
        '''
        Display a table header columns and other info

        Parameters
        ----------
        databook : str | int
            databook name or id
        table : str | int
            table name or id

        Returns
        -------
        str
            HTML content of the table view page.
        '''
        try:
            # SECTION: check if jinja2 is installed
            try:
                from jinja2 import Environment, FileSystemLoader
            except ImportError:
                raise ImportError(
                    "Jinja2 is not installed. Please install it using 'pip install jinja2'.")

            # SECTION: detect table type
            tb_info_res_ = self.table_info(databook, table, res_format='dict')

            # NOTE: databook name
            db, db_name, db_rid = self.find_databook(databook)

            # NOTE: table name
            tb_id, tb_name = self.find_table(databook, table)

            # res
            tb_res = None

            # if
            if isinstance(tb_info_res_, dict):
                # check
                if tb_info_res_['Type'] == 'Equation':  # ! equation
                    # load table equation
                    tb_res = self.table_data(databook, table)
                elif tb_info_res_['Type'] == 'Data':  # ! data
                    # load table data
                    tb_res = self.table_data(databook, table)
                elif tb_info_res_['Type'] == 'Matrix-Equation':  # ! matrix-equation
                    # load table equation
                    tb_res = self.table_data(databook, table)
                elif tb_info_res_['Type'] == 'Matrix-Data':  # ! matrix-data
                    # load table equation
                    tb_res = self.table_data(databook, table)
                else:
                    raise Exception('No data/equation found!')

                # SECTION: convert dataframe to dict
                # check
                if isinstance(tb_res, pd.DataFrame):
                    # NOTE: convert to list of dict
                    tb_res = tb_res.to_dict(orient='records')

                # SECTION: web application
                # check jinja2 installed
                # from jinja2 import Environment, FileSystemLoader
                # res
                # return tb_res
                # NOTE: tojson function
                def tojson(obj):
                    return json.dumps(obj)

                # NOTE: url_for function
                def url_for(endpoint, filename=None):
                    """
                    Generate absolute paths for static files when opening the HTML file directly.
                    """
                    if endpoint == 'static':
                        # Get the directory of the current script
                        # current path
                        current_path = os.path.dirname(__file__)

                        # Go back to the parent directory (pyThermoDB)
                        parent_path = os.path.abspath(
                            os.path.join(current_path, '..'))

                        # static path
                        static_path = os.path.join(parent_path, 'static')

                        # base_dir = os.path.dirname(os.path.abspath(__file__))
                        # parent_dir = os.path.dirname(os.path.dirname(__file__))
                        # static directory
                        static_dir = f'file://{os.path.join(static_path, filename).replace(os.sep, "/")}'
                        return static_dir
                    return '#'

                def render_page(databook_name: str,
                                table_name: str,
                                sample_data: List[Dict],
                                page: int = 1,
                                rows_per_page: int = 50,
                                theme: Literal['light', 'dark'] = "light"):
                    """
                    Render the HTML page using Jinja2 templates

                    Parameters
                    ----------
                    databook_name : str
                        Name of the databook
                    table_name : str
                        Name of the table
                    sample_data : list
                        List of dictionaries containing table data
                    page : int, optional
                        Current page number (default is 1)
                    rows_per_page : int, optional
                        Number of rows per page (default is 50)
                    theme : str, optional
                        Theme for the table ('light' or 'dark', default is 'light')
                    """
                    # Define text colors for each theme to ensure visibility
                    text_colors = {
                        'light': {
                            'primary': '#212529',  # Dark text for light backgrounds
                            'secondary': '#495057',
                            'muted': '#6c757d'
                        },
                        'dark': {
                            'primary': '#f8f9fa',  # Light text for dark backgrounds
                            'secondary': '#e9ecef',
                            'muted': '#adb5bd'
                        }
                    }

                    # extract data
                    sample_data = sample_data[2:]
                    # Calculate pagination values
                    total_items = len(sample_data)
                    total_pages = (
                        total_items + rows_per_page - 1) // rows_per_page

                    # SECTION: Setup Jinja2 environment
                    # current path
                    current_path = os.path.dirname(__file__)

                    # Go back to the parent directory (pyThermoDB)
                    parent_path = os.path.abspath(
                        os.path.join(current_path, '..'))

                    # template path
                    template_path = os.path.join(parent_path, 'templates')

                    template_loader = FileSystemLoader(
                        searchpath=template_path)
                    template_env = Environment(loader=template_loader)

                    # Add the function to Jinja2 environment globals
                    template = template_env.get_template('table_view.html')

                    # SECTION: Get the template and render it with the data
                    rendered_html = template.render(
                        title='PyThermoDB Table Viewer',
                        app_name='PyThermoDB Viewer',
                        databook_name=databook_name,
                        table_name=table_name,
                        table_title='Chemical Compounds Data',
                        table_data=sample_data,
                        total_data=total_items,
                        tojson=tojson,
                        url_for=url_for,
                        current_page=page,
                        rows_per_page=rows_per_page,
                        total_pages=total_pages,
                        default_theme=theme,
                        text_colors=text_colors,
                        footer_text=(
                            'PyThermoDB Table Viewer - A web application to display and '
                            'interact with thermodynamic data tables.'
                        ),
                        company='PyThermoDB Project',
                        app_version=__version__,
                    )

                    return rendered_html

                # generate HTML content for the requested page
                html_content = render_page(
                    db_name,
                    tb_name,
                    tb_res,
                    page=1,
                    rows_per_page=50,
                    theme='light'
                )

                # temporary file to store the HTML content
                with tempfile.NamedTemporaryFile(
                    'w', delete=False, suffix='.html'
                ) as temp_file:
                    temp_file.write(html_content)
                    # NOTE: the file is not deleted after closing, so we can open it in the
                    # browser
                    webbrowser.open(temp_file.name)

                # Return the path to the temporary file in case needed elsewhere
                return temp_file.name

            else:
                raise Exception('Table loading error!')
        except Exception as e:
            raise Exception(f"Table loading error {e}")

    def tables_view(self):
        """
        Display all tables in the browser.
        """
        try:
            # SECTION: check if jinja2 is installed
            try:
                from jinja2 import Environment, FileSystemLoader
            except ImportError:
                raise ImportError(
                    "Jinja2 is not installed. Please install it using 'pip install jinja2'.")

            # SECTION: load data
            data_ = self.list_descriptions(res_format='dict')

            # check
            if not isinstance(data_, dict):
                raise ValueError("data_ is not a dictionary!")

            # card data
            card_data = []

            # looping through databooks
            for k, v in data_.items():
                db_name = k
                db_id = v['DATABOOK-ID']

                # looping through tables
                for k_, v_ in v.items():
                    if k_ == 'DATABOOK-ID':
                        continue

                    _table_id = v_['TABLE-ID']
                    _table_description = v_['DESCRIPTION']
                    _table_name = k_

                    # data load
                    _table_data = self.table_data(
                        db_id, _table_id, res_format='list')

                    # collect data
                    card_data.append({
                        'db_name': db_name,
                        'db_id': db_id,
                        'table_name': _table_name,
                        'table_id': _table_id,
                        'table_description': _table_description,
                        'table_data': _table_data,
                        'table_data_length': len(_table_data),
                    })

            # SECTION: render HTML page
            # init launcher
            app = Launcher()
            # pass data
            return app.launch(card_data)

        except Exception as e:
            raise Exception(f"Error displaying tables: {e}")

    def table_data(
        self,
        databook: str | int,
        table: str | int,
        res_format: Literal[
            'dataframe', 'list', 'json'
        ] = 'dataframe'
    ) -> pd.DataFrame | List[
        Dict[Hashable, Optional[float | int | str]]
    ] | str | Dict[str, pd.DataFrame]:
        '''
        Get all table elements (display a table)

        Parameters
        ----------
        databook : str | int
            databook name or id
        table : str | int
            table name or id
        res_format : Literal['dataframe', 'dict','json']
            Format of the returned data. Defaults to 'dataframe'.

        Returns
        -------
        tb_data : Pandas.DataFrame | list | str
            table data in the specified format.
        '''
        try:
            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id
            databook_id = db_rid + 1

            # find table zero-based id
            tb_id, tb_name = self.find_table(databook, table)
            # table id
            table_id = tb_id + 1

            # SECTION: set api
            TableReferenceC = TableReference(custom_ref=self.custom_ref)
            # REVIEW: load table
            tb_data = TableReferenceC.load_table(databook_id, table_id)

            # NOTE: check tb_data
            if isinstance(tb_data, pd.DataFrame):
                # ! dataframe
                # convert to list of dicts
                tb_list_dict = tb_data.to_dict(orient='records')
                # to json
                tb_json = tb_data.to_json(orient='records')

                # NOTE: check res_format
                if res_format == 'dataframe':
                    return tb_data
                elif res_format == 'list':
                    return tb_list_dict
                elif res_format == 'json':
                    return tb_json
                else:
                    raise ValueError('Invalid res_format')
            else:
                raise ValueError('Invalid table data format')
        except Exception as e:
            raise Exception(f"Loading matrix data failed {e}")

    def equation_load(
        self,
        databook: int | str,
        table: int | str
    ) -> TableEquation:
        '''
        Display table header columns and other info

        Parameters
        ----------
        databook : int | str
            databook id or name
        table : str
            table name

        Returns
        -------
        object: TableEquation

        Notes
        -----
        1. table should be a string
        '''
        try:
            # table type
            # tb_type = ''
            # table name
            table_name = ''
            # table equations
            table_equations = []
            # databook id | name
            db, db_name, db_id = self.find_databook(databook)
            # get the tb
            tb = self.select_table(databook, table)

            # check
            if tb:
                # NOTE: table name
                table_name = tb['table']

                # NOTE: table type
                if tb['table_type'] is not None and tb['table_type'] != 'None':
                    tb_type = TableTypes.EQUATIONS.value

                # NOTE: table values
                if tb['table_values'] is not None and tb['table_values'] != 'None':
                    table_values = tb['table_values']
                else:
                    table_values = None

                # NOTE: table structure
                if tb['table_structure'] is not None and tb['table_structure'] != 'None':
                    table_structure = tb['table_structure']
                else:
                    table_structure = None

                # check data/equations
                if tb['equations'] is not None and tb['equations'] != 'None':
                    # set table type
                    # tb_type = 'equation'

                    # looping through equations
                    for item in tb['equations']:
                        table_equations.append(item)

                    # create table equation
                    return TableEquation(
                        db_name,
                        table_name,
                        table_equations,
                        table_values=table_values,
                        table_structure=table_structure
                    )
                else:
                    raise Exception('Table loading error!')
            else:
                raise Exception('Table loading error!')

        except Exception as e:
            raise Exception(f"Table loading error {e}")

    def data_load(
        self,
        databook: int | str,
        table: int | str
    ) -> TableData:
        '''
        Display table header columns and other info

        Parameters
        ----------
        databook : int | str
            databook id or name
        table : str
            table name

        Returns
        -------
        object : TableData
            table object with data loaded
        '''
        try:
            # table type
            tb_type = ''
            # table name
            table_name = ''
            # table data
            table_data = []
            # databook id | name
            db, db_name, db_id = self.find_databook(databook)
            # get the tb
            tb = self.select_table(databook, table)

            # check
            if tb:
                # NOTE: table name
                table_name = tb['table']

                # NOTE: check data/equations
                if tb['data'] is None or tb['data'] == 'None':
                    raise Exception(
                        'This method not compatible with the selected table!')

                tb_type = TableTypes.DATA.value

                # NOTE: check table values
                if tb['table_values'] is not None and tb['table_values'] != 'None':
                    table_values = tb['table_values']
                else:
                    table_values = None

                # NOTE: check table structure
                if tb['table_structure'] is not None and tb['table_structure'] != 'None':
                    table_structure = tb['table_structure']
                else:
                    table_structure = None

                # check data
                if tb_type == 'data':
                    table_data = tb['data']

                    # check
                    if not isinstance(table_data, dict):
                        raise ValueError("Table data is not a dictionary!")

                    # extract table data
                    COLUMNS = table_data.get('COLUMNS')
                    SYMBOL = table_data.get('SYMBOL')
                    UNIT = table_data.get('UNIT')
                    CONVERSION = table_data.get('CONVERSION')

                    # NOTE: check if the table data is empty
                    if not COLUMNS or not SYMBOL or not UNIT or not CONVERSION:
                        raise ValueError("Table data is empty!")

                    # data no
                    return TableData(
                        db_name,
                        table_name,
                        table_data,
                        table_values=table_values,
                        table_structure=table_structure
                    )
                else:
                    raise Exception('Table loading error!')
            else:
                raise Exception('Table loading error!')
        except Exception as e:
            raise Exception(f"Table loading error {e}")

    def matrix_equation_load(
        self,
        databook: int | str,
        table: int | str
    ) -> TableMatrixEquation:
        '''
        Display table header columns and other info

        Parameters
        ----------
        databook : int | str
            databook id or name
        table : str
            table name

        Returns
        -------
        object: TableMatrixEquation

        Notes
        -----
        1. table should be a string
        '''
        try:
            # table type
            # tb_type = ''
            # table name
            table_name = ''
            # table equations
            table_equations = []
            # databook id | name
            db, db_name, db_id = self.find_databook(databook)
            # get the tb
            tb = self.select_table(databook, table)

            # check
            if tb:
                # table name
                table_name = tb['table']

                # matrix-data/matrix-equation
                if tb['matrix_equations'] is not None:
                    # tb_type = TableTypes.MATRIX_EQUATIONS.value

                    for item in tb['matrix_equations']:
                        table_equations.append(item)

                    # create table equation
                    return TableMatrixEquation(
                        db_name,
                        table_name,
                        table_equations
                    )
                else:
                    raise Exception('Table loading error!')
            else:
                raise Exception('Table loading error!')

        except Exception as e:
            raise Exception(f"Table loading error {e}")

    def matrix_data_load(
        self,
        databook: int | str,
        table: int | str
    ) -> TableMatrixData:
        '''
        Gives table contents as:

            * Table type
            * Data and equations numbers

        Parameters
        ----------
        databook : int | str
            databook id or name
        table : str
            table name

        Returns
        -------
        object : TableMatrixData
            table object with data loaded
        '''
        try:
            # table type
            # tb_type = ''
            # table name
            table_name = ''
            # table data
            table_data = []
            # databook id | name
            db, db_name, db_id = self.find_databook(databook)
            # get the tb
            tb = self.select_table(databook, table)

            # check
            if tb:
                # table name
                table_name = tb['table']

                # matrix-data/matrix-equation
                if tb['matrix_data'] is not None:
                    # tb_type = TableTypes.MATRIX_DATA.value

                    # table data
                    table_data = tb['matrix_data']

                    # data no
                    return TableMatrixData(db_name, table_name, table_data)
                else:
                    raise Exception('Table loading error!')
            else:
                raise Exception('Table not found!')
        except Exception as e:
            raise Exception(f"Table loading error {e}")

    def check_component(
            self,
            component_name: str | list[str],
            databook: int | str,
            table: int | str,
            column_name: Optional[str | list[str]] = None,
            query: bool = False,
            res_format: Literal[
                'dict', 'json', 'str'
            ] = 'json'
    ) -> Union[str, dict[str, str]]:
        '''
        Check a component availability in the selected databook and table

        Parameters
        ----------
        component_name : str | list
            string of component name (e.g. 'Carbon dioxide') | list as ['Carbon dioxide','g']
        databook : int | str
            databook id or name
        table : int | str
            table id or name
        column_name : str | list
            column name (e.g. 'Name') | list as ['Name','state']
        query : str
            query to search a dataframe

        Returns
        -------
        str | dict[str, str]
            summary of the component availability
        '''
        try:
            # check search option
            if column_name is None:
                column_name = 'Name'

            # check
            if query:
                column_name = column_name

            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id (non-zero-based id)
            databook_id = db_rid + 1

            # find table zero-based id
            tb_id, tb_name = self.find_table(databook, table)
            # table id (non-zero-based id)
            table_id = tb_id + 1

            # res
            res = False

            # check databook_id and table_id are number or not
            if isNumber(databook_id) and isNumber(table_id):
                # check
                if self.data_source == 'api':
                    # res = self.check_component_api(
                    #     component_name, databook_id, table_id)
                    pass
                elif self.data_source == 'local':
                    res = self.check_component_local(
                        component_name, databook_id, table_id,
                        column_name, query=query)
                else:
                    raise Exception('Data source error!')
            else:
                raise Exception("databook and table id required!")

            # res
            res_dict = {
                'databook_id': databook_id,
                'table_id': table_id,
                'component_name': component_name,
                'availability': res
            }

            # json
            res_json = json.dumps(res_dict, indent=4)

            # check
            if res_format == 'json':
                return res_json
            elif res_format == 'dict':
                return res_dict
            elif res_format == 'str':
                return res_json
            else:
                raise ValueError('Invalid res_format')
        except Exception as e:
            raise Exception(f"Component check error! {e}")

    def check_component_api(
            self,
            component_name: str | list,
            databook_id: int,
            table_id: int):
        '''
        Check component availability in the selected databook and table

        Parameters
        ----------
        component_name : str | list
            string of component name (e.g. 'Carbon dioxide') | list as ['Carbon dioxide','g']
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str | list
            column name (e.g. 'Name') | list as ['Name','state']

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
                    databook_name = self.list_databooks(res_format='list')[
                        databook_id-1]
                    # get table
                    # table_name = self.list_tables(databook=databook_id, res_format='list')[
                    #     table_id-1][0]

                    list_tables_ = self.list_tables(
                        databook=databook_id,
                        res_format='list'
                    )

                    # set
                    table_id_ = table_id - 1

                    # check
                    if len(list_tables_) > 0:
                        # get table name

                        table_name = "Obsolete Table"

                    # check
                    # if component_name.upper() in compListUpper:
                    #     print(
                    #         f"[{component_name}] available in [{table_name}] | [{databook_name}]")
                    # else:
                    #     print(f"{component_name} is not available.")
                else:
                    print("API error. Please try again later.")

                return None
            else:
                raise Exception(
                    "Invalid input. Please check the input type (databook_id and table_id).")
        except Exception as e:
            raise Exception(f'Checking data error {e}')

    def check_component_local(
        self,
        component_name: str | list,
        databook_id: int,
        table_id: int,
        column_name: str | list[str],
        query: bool = False,
        verbose: bool = False
    ) -> bool:
        '''
        Check component availability in the selected databook and table

        Parameters
        ----------
        component_name : str | list
            string of component name (e.g. 'Carbon dioxide') | list as ['Carbon dioxide','g']
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str
            column name (e.g. 'Name') | list
        query : str
            query string (e.g. 'Name == "Carbon dioxide"')

        Returns
        -------
        object : bool
            component information
        '''
        try:
            # check databook_id and table_id are number or not
            if (
                isNumber(databook_id) and
                isNumber(table_id)
            ):
                # set api
                TableReferenceC = TableReference(custom_ref=self.custom_ref)

                # NOTE: search
                df = TableReferenceC.search_tables(
                    databook_id,
                    table_id,
                    column_name,
                    component_name,
                    query=query
                )

                # NOTE: check availability
                if len(df) > 0:
                    # get databook
                    databook_name = self.list_databooks(
                        res_format='list'
                    )[
                        databook_id-1
                    ]
                    # get table
                    # table_name = self.list_tables(databook=databook_id, res_format='list')[
                    #     table_id-1][0]

                    table_name_ = self.list_tables(
                        databook=databook_id,
                        res_format='list'
                    )

                    # heck
                    if isinstance(table_name_, list):
                        table_name = table_name_[table_id-1][0]

                    # log
                    if verbose:
                        print(
                            f"[{component_name}] available in [{table_name}] | [{databook_name}]")

                    # res
                    return True
                else:
                    # log
                    if verbose:
                        print(f"{component_name} is not available.")
                    # res
                    return False
            else:
                raise Exception("databook and table id required!")
        except Exception as e:
            raise Exception(f'Reading data error {e}')

    def get_component_data(
        self,
        component_name: str,
        databook_id: int,
        table_id: int,
        column_name: Optional[str | list[str]] = None,
        dataframe: bool = False,
        query: bool = False,
        matrix_tb: bool = False
    ):
        '''
        Get component data from database (api|local csvs)

        Parameters
        ----------
        component_name : str
            string of component name (e.g. 'Carbon dioxide')
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str
            column name
        dataframe : bool
            return dataframe or not
        query : bool
            query or not

        Returns
        -------
        component_data : object | pandas dataframe
            component data
        '''
        try:
            # check search option
            if column_name is None:
                column_name = 'Name'

            # set
            component_name = str(component_name).strip()
            # check datasource
            if self.data_source == 'api':
                # component_data = self.get_component_data_api(
                #     component_name, databook_id, table_id, column_name,
                #     dataframe=dataframe)
                return None
            elif self.data_source == 'local':
                component_data = self.get_component_data_local(
                    component_name,
                    databook_id,
                    table_id,
                    column_name,
                    dataframe=dataframe,
                    query=query,
                    matrix_tb=matrix_tb
                )
            else:
                raise Exception('Data source error!')
            # res
            return component_data
        except Exception as e:
            raise Exception(f"Loading data failed {e}")

    def get_component_data_api(
            self,
            component_name: str,
            databook_id: int,
            table_id: int,
            dataframe: bool = False
    ):
        '''
        Get component data from database (api)

        It consists of:
            step1: get thermo data for a component,
            step2: get equation for the data (parameters).

        Parameters
        ----------
        component_name : str
            string of component name (e.g. 'Carbon dioxide')
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str
            column name
        dataframe : bool
            return dataframe or not

        Returns
        -------
        component_data : object | pandas dataframe
            component data
        '''
        # set api
        ManageC = Manage(API_URL, databook_id, table_id)
        # search
        component_data = ManageC.component_info(component_name)
        # check availability
        if len(component_data) > 0:
            # check
            if dataframe:
                df = pd.DataFrame(component_data, columns=[
                    'header', 'symbol', 'records', 'unit'])
                return df
            else:
                return component_data
        else:
            print(f"Data for {component_name} not available!")
            return {}

    def get_component_data_local(
        self,
        component_name: str,
        databook_id: int,
        table_id: int,
        column_name: str | list[str],
        dataframe: bool = False,
        query: bool = False,
        matrix_tb: bool = False
    ):
        '''
        Get component data from database (local csv files)

        Parameters
        ----------
        component_name : str
            string of component name (e.g. 'Carbon dioxide')
        databook_id : int
            databook id
        table_id : int
            table id
        column_name : str
            column name | query to find a record from a dataframe
        dataframe : bool
            return dataframe or not
        query : bool
            query or not
        matrix_tb : bool
            matrix table or not

        Returns
        -------
        payload : dict | pandas dataframe
            component information
        '''
        try:
            # check databook_id and table_id are number or not
            if isNumber(databook_id) and isNumber(table_id):
                # set api
                TableReferenceC = TableReference(custom_ref=self.custom_ref)

                # NOTE: search
                payload = TableReferenceC.make_payload(
                    databook_id,
                    table_id,
                    column_name,
                    component_name,
                    query=query,
                    matrix_tb=matrix_tb
                )

                # NOTE: check availability
                if payload:
                    # check
                    if len(payload) > 0:
                        if dataframe:
                            df = pd.DataFrame(
                                payload,
                                columns=[
                                    'header', 'symbol', 'records', 'unit'
                                ]
                            )
                            return df
                        else:
                            return payload
                    else:
                        raise Exception(
                            "Data for {} not available!".format(component_name))
                else:
                    raise Exception(
                        "Data for {} not available!".format(component_name))
            else:
                print("databook and table id required!")
        except Exception as e:
            raise Exception(f'Reading data error {e}')

    def build_thermo_property(
        self,
        component_names: list[str],
        databook: int | str,
        table: int | str
    ) -> ThermoProperty:
        """
        Build a thermodynamic property including data, equation, matrix-data and matrix-equation.

        Parameters
        ----------
        component_names :  list[str]
            list of component name (e.g. 'Carbon dioxide')
        databook : int | str
            databook id or name
        table : int | str
            table id or name

        Returns
        -------
        ThermoProperty
            table object with data loaded
            - TableEquation
            - TableData
            - TableMatrixEquation
            - TableMatrixData
        """
        try:
            # detect table type
            tb_info_res_ = self.table_info(databook, table, res_format='dict')

            # if
            if isinstance(tb_info_res_, dict):
                # check
                if tb_info_res_['Type'] == 'Equation':  # ! equation
                    # check
                    if len(component_names) > 1:
                        raise Exception('Only one component name required!')
                    # build equation
                    return self.build_equation(
                        component_names[0],
                        databook,
                        table
                    )
                elif tb_info_res_['Type'] == 'Data':  # ! data
                    # check
                    if len(component_names) > 1:
                        raise Exception('Only one component name required!')
                    # build data
                    return self.build_data(
                        component_names[0],
                        databook,
                        table
                    )
                elif tb_info_res_['Type'] == 'Matrix-Equation':  # ! matrix-equation
                    # check
                    if len(component_names) < 2:
                        raise Exception(
                            'At least two component names required!')
                    # build matrix-equation
                    return self.build_matrix_equation(
                        component_names,
                        databook,
                        table
                    )
                elif tb_info_res_['Type'] == 'Matrix-Data':  # ! matrix-data
                    # check
                    if len(component_names) < 2:
                        raise Exception(
                            'At least two component names required!')
                    # build matrix-data
                    return self.build_matrix_data(
                        component_names,
                        databook,
                        table
                    )
                else:
                    raise Exception('No data/equation found!')
            else:
                raise Exception('Table loading error!')
        except Exception as e:
            raise Exception(f'Building thermo property error {e}')

    def build_equation(
        self,
        component_name: str,
        databook: int | str,
        table: int | str,
        column_name: Optional[str | list[str]] = None,
        query: bool = False
    ) -> TableEquation:
        '''
        Build equation for as:
            step1: get thermo data for a component
            step2: get equation for the data (parameters)

        Parameters
        ----------
        component_name : str
            string of component name (e.g. 'Carbon dioxide')
        databook : int | str
            databook id or name
        table : int | str
            table id or name
        column_name : str | list
            column name (e.g. 'Name') | list as ['Name','state']
        query : bool
            query to search a dataframe

        Returns
        -------
        eqs: TableEquation
            equation object
        '''
        try:
            # check search option
            if column_name is None:
                column_name = 'Name'

            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id
            databook_id = db_rid + 1

            # find table zero-based id
            tb_id, tb_name = self.find_table(databook, table)
            # table id
            table_id = tb_id + 1

            # get data from api
            # ! dataframe and PayLoadType
            component_data = self.get_component_data(
                component_name, databook_id, table_id, column_name=column_name,
                query=query)

            # check loading state
            if component_data is not None:
                # check availability
                if len(component_data) > 0:
                    # ! reset data
                    # ! trans data
                    TransDataC = TransData(component_data)
                    # transform api data
                    TransDataC.trans()
                    # transformed api data
                    transform_api_data = TransDataC.data_trans
                    # check data type
                    _data_type = TransDataC.data_type

                    # ! check datatype compatibility
                    if _data_type != 'equation':
                        print("The selected table contains no data for building\
                            equation! check table id and try again.")

                        raise Exception('Building equation failed!')

                    # ! build equation
                    # check eq exists
                    eqs = self.equation_load(
                        databook_id, table_id)

                    # update trans_data
                    eqs.trans_data = transform_api_data

                    # equation init
                    eqs.eqSet()
                    # res
                    return eqs
                else:
                    raise Exception(
                        "Data for {} not available!".format(component_name))
            else:
                raise Exception("Building equation failed!")
        except Exception as e:
            raise Exception(f'Building equation error {e}')

    def build_data(
        self,
        component_name: str,
        databook: int | str,
        table: int | str,
        column_name: Optional[str | list[str]] = None,
        query: bool = False
    ) -> TableData:
        '''
        Build data as:
            step1: get thermo data for a component

        Parameters
        ----------
        component_name : str
            string of component name (e.g. 'Carbon dioxide')
        databook : int | str
            databook id or name
        table : int | str
            table id or name
        column_name : str | list
            column name (e.g. 'Name') | list as ['Name','state']
        query : bool
            query to search a dataframe

        Returns
        -------
        TableData
            table data object
        '''
        try:
            # check search option
            if column_name is None:
                column_name = 'Name'

            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id
            databook_id = db_rid + 1

            # find table zero-based id
            tb_id, tb_name = self.find_table(databook, table)
            # table id
            table_id = tb_id + 1

            # SECTION: get data from api
            # ! dataframe and PayLoadType
            component_data = self.get_component_data(
                component_name, databook_id, table_id, column_name=column_name,
                query=query)

            # check loading state
            if component_data is not None:
                # check availability
                if len(component_data) > 0:
                    # ! trans data
                    TransDataC = TransData(component_data)
                    # transform api data
                    TransDataC.trans()
                    # transformed api data
                    transform_api_data = TransDataC.data_trans

                    # ! check data type
                    _data_type = TransDataC.data_type
                    if _data_type != 'data':
                        print(
                            "The selected table contains no data for building data!\
                            check table id and try again.")

                        raise Exception('Building data failed!')

                    # ! build data
                    # * construct template
                    # check eq exists
                    dts = self.data_load(
                        databook_id, table_id)

                    # ! check
                    if dts is not None:
                        # update trans_data
                        dts.trans_data = transform_api_data
                        # prop data
                        dts.prop_data = transform_api_data
                    else:
                        raise Exception('Building data failed!')

                    # res
                    return dts
                else:
                    raise Exception(
                        "Data for {} not available!".format(component_name))
            else:
                raise Exception("Building data failed!")
        except Exception as e:
            raise Exception(f'Building data error {e}')

    def build_matrix_equation(
        self,
        component_names: list[str],
        databook: int | str,
        table: int | str,
        column_name: Optional[str | list[str]] = None,
        query: bool = False
    ) -> TableMatrixEquation:
        '''
        Build matrix-equation for as:
            step1: get thermo data for a component
            step2: get equation for the data (parameters)

        Parameters
        ----------
        component_names : list[str]
            component name list (e.g. ['Methanol','Ethanol'])
        databook : int | str
            databook id or name
        table : int | str
            table id or name
        column_name : str | list
            column name (e.g. 'Name') | list as ['Name','state']

        Returns
        -------
        eqs: TableMatrixEquation
            matrix-equation object
        '''
        try:
            # check search option
            if column_name is None:
                column_name = 'Name'

            # component no
            component_no = len(component_names)
            # check
            if component_no <= 1:
                raise Exception('At least two components are required')

            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id
            databook_id = db_rid + 1

            # find table zero-based id
            tb_id, tb_name = self.find_table(databook, table)
            # table id
            table_id = tb_id + 1

            # SECTION: create matrix-data
            # ! retrieve all data from matrix-table (csv file)
            # matrix table
            matrix_table = self.table_data(databook, table)

            # NOTE
            # get data from api
            component_data_pack = []

            # looping through components
            for component_name in component_names:
                # component name
                component_name = str(component_name).strip()

                # get data from api
                component_data = self.get_component_data(
                    component_name,
                    databook_id,
                    table_id,
                    column_name=column_name,
                    query=query,
                    matrix_tb=True
                )
                # save
                component_data_pack.append({
                    'component_name': component_name,
                    'data': component_data
                })

            # SECTION
            # check loading state
            if component_data_pack:
                # check availability
                if len(component_data_pack) > 0:
                    # ! trans data
                    TransDataC = TransMatrixData(component_data_pack)
                    # transform api data
                    TransDataC.trans()
                    # transformed api data
                    transform_api_data = TransDataC.data_trans_pack
                    # check data type
                    _data_type = TransDataC.data_type

                    # ! check datatype compatibility
                    if _data_type != 'matrix-equations':
                        print("The selected table contains no data for building\
                            equation! check table id and try again.")

                        raise Exception('Building matrix-equation failed!')

                    # ! build equation
                    # ! reading yml reference
                    # check eq exists
                    eqs = self.matrix_equation_load(
                        databook_id, table_id)

                    # NOTE: update trans_data
                    eqs.trans_data_pack = transform_api_data
                    # NOTE: matrix table (data template)
                    eqs.matrix_table = matrix_table

                    # equation init
                    eqs.eqSet()
                    # res
                    return eqs
                else:
                    raise Exception("Data for {} not available!".format(
                        ",".join(component_names)))
            else:
                raise Exception("Building matrix-equation failed!")
        except Exception as e:
            raise Exception(f'Building matrix-equation error {e}')

    def build_matrix_data(
        self,
        component_names: list[str],
        databook: int | str,
        table: int | str,
        column_name: Optional[str | list[str]] = None,
        query: bool = False
    ) -> TableMatrixData:
        '''
        Build matrix data as:
            step1: get thermo matrix data

        Parameters
        ----------
        component_names : list[str]
            component name list (e.g. ['Methanol','Ethanol'])
        databook : int | str
            databook id or name
        table : int | str
            table id or name
        column_name : str | list
            column name (e.g. 'Name') | list as ['Name','state']

        Returns
        -------
        TableMatrixData
            matrix-data object
        '''
        try:
            # check component list
            if not isinstance(component_names, list):
                raise Exception('Component names must be a list')

            # check component name
            if not all(isinstance(name, str) for name in component_names):
                raise Exception('Component names must be strings')

            # check search option
            if column_name is None:
                column_name = 'Name'

            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id
            databook_id = db_rid + 1

            # find table zero-based id
            tb_id, tb_name = self.find_table(databook, table)
            # table id
            table_id = tb_id + 1

            # NOTE: matrix table
            # ! retrieve all data from matrix-table
            # ? usually matrix-table data are limited
            matrix_table = self.table_data(databook, table)

            # SECTION: get data from api
            component_data_pack = []

            # looping through components
            for component_name in component_names:
                # get data
                component_data = self.get_component_data(
                    component_name.strip(),
                    databook_id,
                    table_id,
                    column_name=column_name,
                    query=query,
                    matrix_tb=True
                )
                # save
                component_data_pack.append({
                    'component_name': str(component_name).strip(),
                    'data': component_data
                })

            # check loading state
            if component_data_pack:
                # check availability
                if len(component_data_pack) > 0:
                    # ! trans data
                    TransMatrixDataC = TransMatrixData(component_data_pack)
                    # transform api data
                    TransMatrixDataC.trans()
                    # transformed api data
                    transform_api_data = TransMatrixDataC.data_trans_pack

                    # ! check data type
                    _data_type = TransMatrixDataC.data_type
                    if _data_type != 'matrix-data':
                        print(
                            "The selected table contains no data for building matrix-data! check table id and try again.")

                        raise Exception('Building data failed!')

                    # ! build data
                    # check eq exists
                    dts = self.matrix_data_load(
                        databook_id, table_id)

                    # ! check
                    if dts is not None:
                        # check type
                        if isinstance(dts, TableMatrixData):
                            if hasattr(dts, 'trans_data_pack') and hasattr(dts, 'prop_data_pack'):
                                # NOTE: update trans_data
                                dts.trans_data_pack = transform_api_data
                                # NOTE: prop data
                                dts.prop_data_pack = transform_api_data
                                # NOTE: matrix table
                                dts.matrix_table = matrix_table
                                # NOTE: matrix element
                                dts.matrix_elements = component_names

                                # res
                                return dts
                            else:
                                raise Exception('Building data failed!')
                        else:
                            raise Exception('Building data failed!')
                    else:
                        raise Exception('Building data failed!')
                else:
                    raise Exception("Data for {} not available!".format(
                        ', '.join(component_names)))
            else:
                raise Exception("Building data failed!")
        except Exception as e:
            raise Exception(f'Building matrix data error {e}')

    def __search_databook(
        self,
        search_terms: list[str],
        search_mode: str,
        column_names: list[str] = ['Name', 'Formula']
    ) -> list[dict[str, str]]:
        """
        Search a term through all databook for instance a component name

        Parameters
        ----------
        search_terms : list[str]
            search terms as list, e.g. ['Carbon dioxide','CO2']
        search_mode : Literal['exact', 'similar']
            search mode, 'exact' or 'similar'
        column_names : list[str]
            column names to search, e.g. ['Name', 'Formula']

        Returns
        -------
        list[dict[str, str]]
            search results as list of dictionaries, each dictionary contains
        """
        try:
            # set table reference
            # to load both internal and external data (csv files)
            TableReferenceC = TableReference(custom_ref=self.custom_ref)

            # search
            res = TableReferenceC.search_component(
                search_terms, search_mode, column_names=column_names)

            return res

        except Exception as e:
            raise Exception(f'Search databook error {e}')

    def search_databook(
            self,
            search_terms: list[str],
            column_names: list[str] = ['Name', 'Formula'],
            res_format: Literal[
                'list', 'dataframe', 'json', 'dict'
            ] = 'dict',
            search_mode: Literal[
                'exact', 'similar'
            ] = 'exact'
    ) -> ComponentSearch:
        """
        Search a term through all databook for instance a component name

        Parameters
        ----------
        search_terms : list[str]
            search terms as list, e.g. ['Carbon dioxide','CO2']
        column_names : list[str]
            column names to search, e.g. ['Name', 'Formula']
        res_format : Literal['list', 'dataframe', 'json', 'dict']
            result format, 'list', 'dataframe', 'json' or 'dict'
        search_mode : Literal['exact', 'similar']
            search mode, 'exact' or 'similar'

        Returns
        -------
        ComponentSearchResult
            search results
        """
        try:
            # call async function
            res = self.__search_databook(
                search_terms,
                search_mode,
                column_names
            )

            # check
            if len(res) == 0:
                logging.warning(
                    f'No results found for the search terms: {search_terms}, search mode: {search_mode}'
                )
                return []

            # dict
            res_dict = {f'record-{i+1}': item for i, item in enumerate(res)}

            res_dict = dict(
                {
                    'message': f'results found for the search terms : {search_terms}, search mode : {search_mode}'
                }, **res_dict
            )

            # NOTE: result settings
            # check res_format
            if res_format == 'list':
                return res
            elif res_format == 'dataframe':
                # dataframe
                return pd.DataFrame(res)
            elif res_format == 'json':
                # json
                return json.dumps(res_dict, indent=4)
            elif res_format == 'dict':
                return res_dict
            else:
                raise ValueError("Invalid res_format")
        except Exception as e:
            raise Exception(f'Search databook error {e}')

    def __list_components(self):
        """
        List all components in the databook
        """
        try:
            # set table reference
            # to load both internal and external data (csv files)
            TableReferenceC = TableReference(custom_ref=self.custom_ref)

            # search
            res = TableReferenceC.list_all_components()

            return res

        except Exception as e:
            raise Exception(f'Search databook error {e}')

    def list_components(
        self,
        res_format: Literal[
            'list', 'dict', 'json'
        ] = 'dict'
    ) -> ListComponents:
        """
        List all components in the databook

        Parameters
        ----------
        res_format : Literal['list', 'dict', 'json']
            result format, 'list', 'dict' or 'json'

        Returns
        -------
        ListComponents
            list of components in the databook
        """
        try:
            # exec
            res, _ = self.__list_components()

            # res dict
            res_dict = {
                'components': res
            }

            # json
            res_json = json.dumps(res_dict, indent=4)

            # check res_format
            if res_format == 'list':
                return res
            elif res_format == 'dict':
                return res_dict
            elif res_format == 'json':
                return res_json
            else:
                raise ValueError("Invalid res_format")

        except Exception as e:
            raise Exception(f'Listing component error {e}')

    def list_components_info(
            self,
            res_format: Literal[
                'list', 'dict', 'json'
            ] = 'dict'
    ) -> ListComponentsInfo:
        """
        List components information in the databook

        Parameters
        ----------
        res_format : Literal['list', 'dict', 'json']
            result format, 'list', 'dict' or 'json'

        Returns
        -------
        ListComponentsInfo
            list of components information in the databook
        """
        try:
            # from async
            _, res = self.__list_components()

            # dict
            res_dict = {f'record-{i+1}': item for i, item in enumerate(res)}
            # json
            res_json = json.dumps(res_dict, indent=4)

            # check res_format
            if res_format == 'list':
                return res
            elif res_format == 'dict':
                return res_dict
            elif res_format == 'json':
                return res_json
            else:
                raise ValueError("Invalid res_format")

        except Exception as e:
            raise Exception(f'Listing component info error {e}')
