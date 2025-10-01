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
from pythermodb_settings.models import Component
# internal
from ..config import API_URL, __version__
from ..api import Manage
from ..utils import isNumber, uppercaseStringList, create_binary_mixture_id, create_binary_mixtures
from .tableref import TableReference
# transformer
from ..transformer import TransData
from ..transformer import TransMatrixData
from ..manager import ManageData
# core
from ..core import (
    TableEquation,
    TableMatrixEquation,
    TableData,
    TableMatrixData
)
from ..data import TableTypes
from ..models import DataBookTableTypes
# web app
from ..ui import Launcher

# NOTE: logger
logger = logging.getLogger(__name__)

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

    def __init__(
            self,
            custom_ref=None,
            data_source='local'
    ):
        # NOTE: set
        self.data_source = data_source
        self.custom_ref = custom_ref

        # LINK: ManageData init
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
                            # ! table name (case insensitive)
                            tb_name = item[0].lower().strip()
                            if tb_name == table.strip().lower():
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
            table summary which includes table name, type, equations no, data no, matrix-equations no, matrix-data no in the specified format as:

        Notes
        -----
        1. The default value of dataframe is True, the return value (tb_summary) is Pandas Dataframe
        2. The table type can be one of the following:
            - 'Equation': if the table contains equations
            - 'Data': if the table contains data
            - 'Matrix-Equation': if the table contains matrix equations
            - 'Matrix-Data': if the table contains matrix data
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
                    return TableMatrixData(
                        databook_name=db_name,
                        table_name=table_name,
                        table_data=table_data
                    )
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
            summary of the component availability as a string or dictionary in the specified format.

            - 'databook_id': databook id,
            - 'databook_name': 'Thermodynamic Properties of Pure Compounds',
            - 'table_id': table id,
            - 'table_name': 'Physical Properties of Pure Compounds',
            - 'component_name': name of the component,
            - 'availability': True or False

        Notes
        -----
        1. component_name can be a string or a list of strings.
            If a list is provided, it should contain the component name and state (e.g., ['Carbon dioxide', 'g']).
        2. column_name can be a string or a list of strings.
            If a list is provided, it should contain the column names to search in (e.g., ['Name', 'State']).
        3. If query is provided, it will be used to search the dataframe directly.
        4. If column_name is not provided, it defaults to 'Name'.
        5. If query is not provided, the method will construct a query based on component_name and column_name.
        6. The method returns the result in the specified format: 'dict', 'json', or 'str'.
        7. The `query phrase` is set to `column_name` if query is True.
        '''
        try:
            # NOTE: check search option
            if column_name is None:
                column_name = 'Name'

            # NOTE: check
            if query:
                column_name = column_name

            # SECTION: find ids
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
                        component_name=component_name,
                        databook_id=databook_id,
                        table_id=table_id,
                        column_name=column_name,
                        query=query
                    )
                else:
                    raise Exception('Data source error!')
            else:
                raise Exception("databook and table id required!")

            # res
            res_dict = {
                'databook_id': databook_id,
                'databook_name': db_name,
                'table_id': table_id,
                'table_name': tb_name,
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

    def check_components(
            self,
            component_names: List[str],
            databook: int | str,
            table: int | str,
            column_name: Optional[str | list[str]] = None,
            query: bool = False,
            res_format: Literal[
                'dict', 'json', 'str'
            ] = 'dict'):
        '''
        Check multiple components availability in the selected databook and table

        Parameters
        ----------
        component_names : List[str]
            List of component names (e.g. ['Carbon dioxide', 'Water'])
        databook : int | str
            databook id or name
        table : int | str
            table id or name
        column_name : str | list, optional
            column name (e.g. 'Name') | list as ['Name','state'], by default None
        query : bool, optional
            query to search a dataframe, by default False
        res_format : Literal['dict', 'json', 'str'], optional
            Format of the returned data, by default 'json'

        Returns
        -------
        str | dict[str, str]
            summary of the components availability as a string or dictionary in the specified format.
            - 'databook_id': databook id,
            - 'databook_name': 'Thermodynamic Properties of Pure Compounds',
            - 'table_id': table id,
            - 'table_name': 'Physical Properties of Pure Compounds',
            - 'component_name': name of the component,
            - 'availability': True or False

        Notes
        -----
        1. component_names should be a list of strings.
        2. If column_name is not provided, it defaults to 'Name'.
        3. If query is provided, it will be used to search the dataframe directly.
        4. The method returns the result in the specified format: 'dict', 'json', or 'str'.
        '''
        try:
            # NOTE: check
            if not isinstance(component_names, list) or not component_names:
                raise ValueError(
                    "component_names must be a non-empty list of strings.")

            # results
            results = []

            # NOTE: looping through components
            for component_name in component_names:
                res = self.check_component(
                    component_name=component_name,
                    databook=databook,
                    table=table,
                    column_name=column_name,
                    query=query,
                    res_format='dict'
                )
                results.append(res)

            # NOTE: check overall availability
            # init
            overall_availability = None

            # looping through results
            for item in results:
                if not item['availability']:
                    overall_availability = False
                    break
                overall_availability = True

            # ! create results dict
            results = {
                'databook_id': results[0]['databook_id'],
                'databook_name': results[0]['databook_name'],
                'table_id': results[0]['table_id'],
                'table_name': results[0]['table_name'],
                'components': results,
                'availability': overall_availability,
            }

            # json
            res_json = json.dumps(results, indent=4)

            # check
            if res_format == 'json':
                return res_json
            elif res_format == 'dict':
                return results
            elif res_format == 'str':
                return res_json
            else:
                raise ValueError('Invalid res_format')

        except Exception as e:
            raise Exception(f"Components check error! {e}")

    def is_component_available(
        self,
        component: Component,
        databook: int | str,
        table: int | str,
        column_names: List[str] = ['Name', 'Formula'],
        component_key: Literal[
            'Name-State', 'Formula-State'
        ] = 'Name-State',
        res_format: Literal[
            'dict', 'json', 'str'
        ] = 'dict'
    ) -> Union[str, dict[str, str]]:
        '''
        Check if a component is available in the specified databook and table. A component is defined as:
        - name-state: carbon dioxide-g
        - formula-state: CO2-g

        Parameters
        ----------
        component : Component
            The component to check.
        databook : int | str
            The databook id or name.
        table : int | str
            The table id or name.
        column_names : List[str], optional
            List of column names to search in, by default ['Name', 'Formula'].
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for identifying the component, by default 'Name-State'.
        res_format : Literal['dict', 'json', 'str'], optional
            The format of the returned result, by default 'json'.

        Returns
        -------
        str | dict[str, str]
            Summary of the component availability as a string or dictionary in the specified format.

            - 'databook_id': databook id,
            - 'databook_name': 'Thermodynamic Properties of Pure Compounds',
            - 'table_id': table id,
            - 'table_name': 'Physical Properties of Pure Compounds',
            - 'component_name': name of the component,
            - 'availability': True or False

        Notes
        -----
        - Table should contain columns for 'Name', 'Formula', and 'State'. Otherwise an error will be raised.
        '''
        try:
            # SECTION: Validate input
            if not isinstance(component, Component):
                raise ValueError(
                    "Invalid component. Must be an instance of Component class.")
            if (
                not component.name and
                not component.formula and
                not component.state
            ):
                raise ValueError(
                    "Component must have at least a name or a formula.")
            if not column_names or not isinstance(column_names, list):
                raise ValueError(
                    "column_names must be a non-empty list of strings.")
            if len(column_names) != 2:
                raise ValueError(
                    "column_names must contain exactly two elements: ['Name', 'Formula'].")

            # SECTION: Check component_key validity
            if component_key not in ['Name-State', 'Formula-State']:
                raise ValueError(
                    "Invalid component_key. Must be 'Name-State' or 'Formula-State'.")

            # NOTE: create component id band query
            component_id = None
            query = None

            # check
            if component_key == 'Name-State':
                # set
                component_id = f"{component.name}-{component.state}"
                # query
                query = f'Name.str.lower() == "{component.name.lower()}" and State.str.lower() == "{component.state.lower()}"'
            elif component_key == 'Formula-State':
                # set
                component_id = f"{component.formula}-{component.state}"
                # query
                query = f'Formula.str.lower() == "{component.formula.lower()}" and State.str.lower() == "{component.state.lower()}"'

            if component_id is None:
                raise ValueError("Component ID could not be determined.")

            if query is None:
                raise ValueError("Query could not be determined.")

            # SECTION: find ids
            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id (non-zero-based id)
            databook_id = db_rid + 1

            # find table zero-based id
            tb_id, tb_name = self.find_table(databook, table)
            # table id (non-zero-based id)
            table_id = tb_id + 1

            # SECTION: Check if the component exists in the specified databook and table
            availability = self.check_component_local(
                component_name=component_id,
                databook_id=databook_id,
                table_id=table_id,
                column_name=query,
                query=True,
            )

            # res
            res_dict = {
                'databook_id': databook_id,
                'databook_name': db_name,
                'table_id': table_id,
                'table_name': tb_name,
                'component_name': component_id,
                'availability': availability
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
            raise Exception(f"Error checking component availability: {e}")

    def is_binary_mixture_available(
        self,
        components: List[Component],
        databook: int | str,
        table: int | str,
        column_name: str = 'Mixture',
        component_key: Literal[
            'Name-State', 'Formula-State',
        ] = 'Name-State',
        mixture_key: Literal[
            'Name', 'Formula',
        ] = 'Name',
        delimiter: str = '|',
        ignore_component_state: bool = False,
        res_format: Literal[
            'dict', 'json', 'str'
        ] = 'dict'
    ) -> str | Dict[str, str | float | bool]:
        '''
        Check if all components in a binary mixture are available in the specified databook and table. A component is defined as:
        - name-state: carbon dioxide-g
        - formula-state: CO2-g

        Parameters
        ----------
        components : List[Component]
            The list of components in the mixture to check.
        databook : int | str
            The databook id or name.
        table : int | str
            The table id or name.
        column_name : str, optional
            The name of the column containing mixture identifiers, by default 'Mixture'.
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for identifying the component, by default 'Name-State'.
        mixture_key : Literal['Name', 'Formula'], optional
            The key to use for identifying the mixture, by default 'Name'.
        delimiter : str, optional
            The delimiter used in the mixture identifiers, by default '|'.
        ignore_component_state : bool, optional
            Whether to ignore the state of the components when checking availability, by default False.
        res_format : Literal['dict', 'json', 'str'], optional
            The format of the returned result, by default 'dict'.

        Returns
        -------
        str | dict[str, str | float | bool]
            Summary of the mixture availability as a string or dictionary in the specified format.

            - 'databook_id': databook id,
            - 'databook_name': 'Thermodynamic Properties of Pure Compounds',
            - 'table_id': table id,
            - 'table_name': 'Physical Properties of Pure Compounds',
            - 'components': list of component identifiers,
            - 'all_available': True if all components are available, False otherwise

        Notes
        -----
        - Table should contain columns for 'Mixture', 'Name', 'Formula', and 'State'. Otherwise an error will be raised.
        - All components must be available for the mixture to be considered available.
        '''
        try:
            # NOTE: check required columns
            required_columns = ['Name', 'Formula', 'State', 'Mixture']

            # SECTION: Validate input
            if not isinstance(components, list) or not all(isinstance(c, Component) for c in components):
                raise ValueError(
                    "Invalid components. Must be a list of Component instances.")
            if not components:
                raise ValueError("Components list cannot be empty.")
            if not column_name or not isinstance(column_name, str):
                raise ValueError(
                    "column_names must be a non-empty list of strings.")

            # SECTION: components config
            # NOTE: at least two components are required
            if len(components) != 2:
                raise ValueError(
                    "The two components are required to check mixture availability.")

            # NOTE: component identifiers for mixture id creation
            component_1 = components[0]
            component_2 = components[1]

            # SECTION: find ids
            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id (non-zero-based id)
            databook_id = db_rid + 1
            # find table zero-based id
            tb_id, tb_name = self.find_table(databook, table)
            # table id (non-zero-based id)
            table_id = tb_id + 1

            # SECTION: binary mixture configuration
            # NOTE: create a unique mixture id based on component names/formulas
            binary_mixture_id: str = create_binary_mixture_id(
                component_1=component_1,
                component_2=component_2,
                mixture_key=mixture_key
            )
            # >> normalized mixture id
            binary_mixture_id = binary_mixture_id.lower().strip()

            # SECTION: load matrix data
            def normalize_mixture_id(
                    mixture: str,
                    delimiter: str
            ) -> str:
                parts = mixture.lower().strip().split(delimiter)
                return delimiter.join(sorted(parts))

            # NOTE: check table type
            table_data = self.table_data(
                databook=databook_id,
                table=table_id,
                res_format='dataframe'
            )

            # check dataframe
            if not isinstance(table_data, pd.DataFrame):
                raise ValueError("Table data is not a valid DataFrame.")

            # NOTE: look up mixture column 'Mixture' for availability of the binary mixture
            if column_name not in table_data.columns:
                raise ValueError(
                    f"Table must contain a {column_name} column to check binary mixture availability.")

            # >> check required columns
            for col in required_columns:
                if col not in table_data.columns:
                    # log
                    logger.error(
                        f"Table must contain a '{col}' column to check binary mixture availability.")
                    return {
                        'databook_id': databook_id,
                        'databook_name': db_name,
                        'table_id': table_id,
                        'table_name': tb_name,
                        'mixture_name': binary_mixture_id,
                        'availability': False,
                        'available_count': 0,
                        'error': f"Table must contain a '{col}' column to check binary mixture availability."
                    }

            # NOTE: normalized dataframe
            # normalized column
            normalized_column_name = f'Normalized_{column_name}'

            # create normalized column
            table_data[normalized_column_name] = table_data[column_name].apply(
                lambda x: normalize_mixture_id(str(x).strip(), delimiter)
            )
            # print(table_data)

            # SECTION: filter dataframe for the mixture
            # ! normalized binary mixture id
            normalized_binary_mixture_id = normalize_mixture_id(
                mixture=binary_mixture_id,
                delimiter=delimiter
            )

            # ! mask
            mask_ = table_data[normalized_column_name].str.strip(
            ) == normalized_binary_mixture_id

            mixture_df = table_data[mask_]
            # print(mixture_df)

            # count row
            available_count = 0
            # check availability
            if mixture_df.empty:
                all_available = False
            else:
                # SECTION: check component name/formula and state in each row
                mask_component_1 = None
                mask_component_2 = None

                if component_key == 'Name-State' and ignore_component_state is False:
                    mask_component_1 = (
                        (
                            mixture_df['Name'].str.lower().str.strip(
                            ) == component_1.name.lower().strip()
                        ) &
                        (
                            mixture_df['State'].str.lower().str.strip(
                            ) == component_1.state.lower().strip()
                        )
                    )
                    mask_component_2 = (
                        (
                            mixture_df['Name'].str.lower().str.strip(
                            ) == component_2.name.lower().strip()
                        ) &
                        (
                            mixture_df['State'].str.lower().str.strip()
                            == component_2.state.lower().strip()
                        )
                    )
                elif component_key == 'Formula-State' and ignore_component_state is False:
                    mask_component_1 = (
                        (
                            mixture_df['Formula'].str.lower().str.strip(
                            ) == component_1.formula.lower().strip()
                        ) &
                        (
                            mixture_df['State'].str.lower().str.strip()
                            == component_1.state.lower().strip()
                        )
                    )
                    mask_component_2 = (
                        (
                            mixture_df['Formula'].str.lower().str.strip(
                            ) == component_2.formula.lower().strip()
                        ) &
                        (
                            mixture_df['State'].str.lower().str.strip()
                            == component_2.state.lower().strip()
                        )
                    )
                elif ignore_component_state:
                    # NOTE: set Name for chosen Name-State
                    component_key_ = 'Name' if component_key == 'Name-State' else 'Formula'

                    # NOTE: compare
                    mask_component_1 = (
                        mixture_df[component_key_].str.lower().str.strip()
                        == component_1.name.lower().strip()
                    )
                    mask_component_2 = (
                        mixture_df[component_key_].str.lower().str.strip()
                        == component_2.name.lower().strip()
                    )
                else:
                    raise ValueError(
                        "Invalid component_key or ignore_component_state configuration.")

                # check
                if mask_component_1 is None or mask_component_2 is None:
                    raise ValueError(
                        "Component masks could not be determined.")
                # check if both components are found
                if not mixture_df[mask_component_1].empty and not mixture_df[mask_component_2].empty:
                    all_available = True
                    # count available rows containing the mixture
                    available_count = len(mixture_df)
                else:
                    all_available = False

            # SECTION: Format results
            res_dict = {
                'databook_id': databook_id,
                'databook_name': db_name,
                'table_id': table_id,
                'table_name': tb_name,
                'mixture_name': binary_mixture_id,
                'availability': all_available,
                'available_count': available_count
            }
            res_json = json.dumps(res_dict, indent=4)

            # >> check
            if res_format == 'json':
                return res_json
            elif res_format == 'dict':
                return res_dict
            elif res_format == 'str':
                return res_json
            else:
                raise ValueError('Invalid res_format')
        except Exception as e:
            raise Exception(f"Error checking mixture availability: {e}")

    def check_mixtures_availability(
        self,
        components: List[Component],
        databook: int | str,
        table: int | str,
        column_name: str = 'Mixture',
        component_key: Literal[
            'Name-State', 'Formula-State',
        ] = 'Name-State',
        mixture_key: Literal[
            'Name', 'Formula',
        ] = 'Name',
        delimiter: str = '|',
        ignore_component_state: bool = False,
        res_format: Literal[
            'dict', 'json', 'str'
        ] = 'dict'
    ) -> Dict[str, str | Dict[str, str | float | bool]]:
        '''
        Check if all components in multiple binary mixtures are available in the specified databook and table. A component is defined as:
        - name-state: carbon dioxide-g
        - formula-state: CO2-g

        Parameters
        ----------
        components : List[Component]
            The list of components in the mixtures to check.
        databook : int | str
            The databook id or name.
        table : int | str
            The table id or name.
        column_name : str, optional
            The name of the column containing mixture identifiers, by default 'Mixture'.
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for identifying the component, by default 'Name-State'.
        mixture_key : Literal['Name', 'Formula'], optional
            The key to use for identifying the mixture, by default 'Name'.
        delimiter : str, optional
            The delimiter used in the mixture identifiers, by default '|'.
        ignore_component_state : bool, optional
            Whether to ignore the state of the components when checking availability, by default False.
        res_format : Literal['dict', 'json', 'str'], optional
            The format of the returned result, by default 'dict'.

        Returns
        -------
        str | dict[str, Union[str, str | float | bool, list]]
            Summary of the mixtures availability as a string or dictionary in the specified format.

            - 'databook_id': databook id,
            - 'databook_name': 'Thermodynamic Properties of Pure Compounds',
            - 'table_id': table id,
            - 'table_name': 'Physical Properties of Pure Compounds',
            - 'mixtures': list of mixture availability results,
            - 'all_available': True if all mixtures are available, False otherwise

        Notes
        -----
        - Table should contain columns for 'Mixture', 'Name', 'Formula', and 'State'. Otherwise an error will be raised.
        - All components in each mixture must be available for that mixture to be considered available.
        - All mixtures must be available for the overall availability to be True.
        '''
        try:
            # SECTION: create mixtures
            binary_mixtures = create_binary_mixtures(
                components=components,
                mixture_key=mixture_key,
                delimiter=delimiter
            )

            # SECTION: check each mixture availability
            results = {}

            # NOTE: looping through mixtures
            try:
                for mixture_id, mixture_components in binary_mixtures.items():
                    # check
                    res = self.is_binary_mixture_available(
                        components=mixture_components,
                        databook=databook,
                        table=table,
                        column_name=column_name,
                        component_key=component_key,
                        mixture_key=mixture_key,
                        delimiter=delimiter,
                        ignore_component_state=ignore_component_state,
                        res_format=res_format
                    )

                    # append check result
                    results[mixture_id] = res
            except Exception as e:
                logger.warning(
                    f"Error checking mixture [{mixture_id}] availability: {e}")

            # SECTION: check overall availability

            # res
            return results
        except Exception as e:
            raise Exception(f"Error checking mixtures availability: {e}")

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
        verbose: bool = False,
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

        Notes
        -----
        - Return True if df is not empty
        - Return False if df is empty
        '''
        try:
            # check databook_id and table_id are number or not
            if (
                isNumber(databook_id) and
                isNumber(table_id)
            ):
                # NOTE: set api
                TableReferenceC = TableReference(custom_ref=self.custom_ref)

                # NOTE: search
                df = TableReferenceC.search_tables(
                    databook_id=databook_id,
                    table_id=table_id,
                    column_name=column_name,
                    lookup=component_name,  # ! exact match
                    query=query
                )

                # NOTE: check availability
                if len(df) > 0:
                    if verbose:
                        print(
                            f"[{component_name}] available in [{table_id}] | [{databook_id}]"
                        )

                    # res
                    return True
                else:
                    # log
                    if verbose:
                        print(f"{component_name} is not available.")

                    # res
                    return False
            else:
                logger.error(
                    "Invalid input. Please check the input type (databook_id and table_id).")
                return False
        except Exception as e:
            logger.error(f'Checking data error {e}')
            return False

    def get_component_data(
        self,
        component_name: str,
        databook_id: int,
        table_id: int,
        column_name: Optional[str | list[str]] = None,
        dataframe: bool = False,
        query: bool = False,
        matrix_tb: bool = False,
        component_state: Optional[str] = None
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
        column_name : str | list, optional
            column name
        dataframe : bool
            return dataframe or not
        query : bool
            query or not
        matrix_tb : bool
            matrix table or not
        component_state : str, optional
            component state (e.g. 'g', 'l', 's')

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
                    component_name=component_name,
                    databook_id=databook_id,
                    table_id=table_id,
                    column_name=column_name,
                    component_state=component_state,
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
        component_state: Optional[str] = None,
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
        component_state : str, optional
            component state (e.g. 'g', 'l', 's')
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

                # NOTE: set query
                if component_state is not None:
                    # ! set column_name
                    if isinstance(column_name, str):
                        column_name = [column_name, 'State']
                    elif isinstance(column_name, list):
                        if 'State' not in column_name:
                            column_name.append('State')

                    # ! set query
                    if isinstance(component_name, str):
                        lookup = [component_name, component_state]
                else:
                    lookup = component_name

                # NOTE: search
                try:
                    payload = TableReferenceC.make_payload(
                        databook_id=databook_id,
                        table_id=table_id,
                        column_name=column_name,
                        lookup=lookup,
                        query=query,
                        matrix_tb=matrix_tb
                    )
                except Exception as e:
                    logging.error(f"Table search error {e}")
                    payload = None

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

    def get_binary_mixture_data(
        self,
        components: List[Component],
        databook: int | str,
        table: int | str,
        column_name: str = 'Mixture',
        component_key: Literal[
            'Name-State', 'Formula-State',
        ] = 'Name-State',
        mixture_key: Literal[
            'Name', 'Formula',
        ] = 'Name',
        delimiter: str = '|',
        ignore_component_state: bool = False,
        res_format: Literal[
            'dict', 'json', 'str'
        ] = 'dict'
    ) -> Union[str, dict[str, Union[str, str | float | bool]]]:
        '''
        Get component data in a binary mixture are available in the specified databook and table. A component is defined as:
        - name-state: carbon dioxide-g
        - formula-state: CO2-g

        Parameters
        ----------
        components : List[Component]
            The list of components in the mixture to check.
        databook : int | str
            The databook id or name.
        table : int | str
            The table id or name.
        column_name : str, optional
            The name of the column containing mixture identifiers, by default 'Mixture'.
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for identifying the component, by default 'Name-State'.
        mixture_key : Literal['Name', 'Formula'], optional
            The key to use for identifying the mixture, by default 'Name'.
        delimiter : str, optional
            The delimiter used in the mixture identifiers, by default '|'.
        ignore_component_state : bool, optional
            Whether to ignore the state of the components when checking availability, by default False.
        res_format : Literal['dict', 'json', 'str'], optional
            The format of the returned result, by default 'dict'.

        Returns
        -------
        str | dict[str, Union[str, str | float | bool]]
            Summary of the mixture availability as a string or dictionary in the specified format.

            - 'databook_id': databook id,
            - 'databook_name': 'Thermodynamic Properties of Pure Compounds',
            - 'table_id': table id,
            - 'table_name': 'Physical Properties of Pure Compounds',
            - 'mixture_name': name of the mixture,
            - 'availability': True if all components are available, False otherwise
            - 'available_count': number of available records for the mixture,
            - 'component_data': detailed data for each component if available,

        Notes
        -----
        - Table should contain columns for 'Mixture', 'Name', 'Formula', and 'State'. Otherwise an error will be raised.
        - All components must be available for the mixture to be considered available.
        '''
        try:
            # NOTE: check required columns
            required_columns = ['Name', 'Formula', 'State', 'Mixture']

            # SECTION: Validate input
            if not isinstance(components, list) or not all(isinstance(c, Component) for c in components):
                raise ValueError(
                    "Invalid components. Must be a list of Component instances.")
            if not components:
                raise ValueError("Components list cannot be empty.")
            if not column_name or not isinstance(column_name, str):
                raise ValueError(
                    "column_names must be a non-empty list of strings.")

            # SECTION: components config
            # NOTE: at least two components are required
            if len(components) != 2:
                raise ValueError(
                    "The two components are required to check mixture availability.")

            # NOTE: component identifiers for mixture id creation
            component_1 = components[0]
            component_2 = components[1]

            # SECTION: find ids
            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id (non-zero-based id)
            databook_id = db_rid + 1
            # find table zero-based id
            tb_id, tb_name = self.find_table(databook, table)
            # table id (non-zero-based id)
            table_id = tb_id + 1

            # SECTION: binary mixture configuration
            # NOTE: create a unique mixture id based on component names/formulas
            binary_mixture_id: str = create_binary_mixture_id(
                component_1=component_1,
                component_2=component_2,
                mixture_key=mixture_key
            )
            # >> normalized mixture id
            binary_mixture_id = binary_mixture_id.lower().strip()

            # SECTION: load matrix data
            def normalize_mixture_id(
                    mixture: str,
                    delimiter: str
            ) -> str:
                parts = mixture.lower().strip().split(delimiter)
                return delimiter.join(sorted(parts))

            # NOTE: check table type
            table_data = self.table_data(
                databook=databook_id,
                table=table_id,
                res_format='dataframe'
            )

            # check dataframe
            if not isinstance(table_data, pd.DataFrame):
                raise ValueError("Table data is not a valid DataFrame.")

            # NOTE: look up mixture column 'Mixture' for availability of the binary mixture
            if column_name not in table_data.columns:
                raise ValueError(
                    f"Table must contain a {column_name} column to check binary mixture availability.")

            # >> check required columns
            for col in required_columns:
                if col not in table_data.columns:
                    # log
                    logger.error(
                        f"Table must contain a '{col}' column to check binary mixture availability.")
                    return {
                        'databook_id': databook_id,
                        'databook_name': db_name,
                        'table_id': table_id,
                        'table_name': tb_name,
                        'mixture_name': binary_mixture_id,
                        'availability': False,
                        'available_count': 0,
                        'error': f"Table must contain a '{col}' column to check binary mixture availability."
                    }

            # SECTION: get dataframe details
            # ! header
            header = table_data.columns.tolist()
            # ! symbol (first row)
            symbol = table_data.iloc[0].tolist(
            ) if not table_data.empty else []
            # ! unit (second row)
            unit = table_data.iloc[1].tolist() if len(table_data) > 1 else []

            # NOTE: normalized dataframe
            # normalized column
            normalized_column_name = f'Normalized_{column_name}'

            # create normalized column
            table_data[normalized_column_name] = table_data[column_name].apply(
                lambda x: normalize_mixture_id(str(x).strip(), delimiter)
            )

            # SECTION: filter dataframe for the mixture
            # ! normalized binary mixture id
            normalized_binary_mixture_id = normalize_mixture_id(
                mixture=binary_mixture_id,
                delimiter=delimiter
            )

            # ! mask
            mask_ = table_data[normalized_column_name].str.strip(
            ) == normalized_binary_mixture_id

            mixture_df = table_data[mask_]

            # NOTE: initialize
            # count row
            available_count = 0
            # combined dataframe
            combined_df = pd.DataFrame()
            # component data
            component_data = {
                component_1.name: {
                    'records': [],
                    'header': [],
                    'unit': [],
                    'symbol': []
                },
                component_2.name: {
                    'records': [],
                    'header': [],
                    'unit': [],
                    'symbol': []
                }
            }

            # NOTE: check availability
            if mixture_df.empty:
                all_available = False
            else:
                # SECTION: check component name/formula and state in each row
                mask_component_1 = None
                mask_component_2 = None

                if component_key == 'Name-State' and ignore_component_state is False:
                    mask_component_1 = (
                        (
                            mixture_df['Name'].str.lower().str.strip(
                            ) == component_1.name.lower().strip()
                        ) &
                        (
                            mixture_df['State'].str.lower().str.strip(
                            ) == component_1.state.lower().strip()
                        )
                    )
                    mask_component_2 = (
                        (
                            mixture_df['Name'].str.lower().str.strip(
                            ) == component_2.name.lower().strip()
                        ) &
                        (
                            mixture_df['State'].str.lower().str.strip()
                            == component_2.state.lower().strip()
                        )
                    )
                elif component_key == 'Formula-State' and ignore_component_state is False:
                    mask_component_1 = (
                        (
                            mixture_df['Formula'].str.lower().str.strip(
                            ) == component_1.formula.lower().strip()
                        ) &
                        (
                            mixture_df['State'].str.lower().str.strip()
                            == component_1.state.lower().strip()
                        )
                    )
                    mask_component_2 = (
                        (
                            mixture_df['Formula'].str.lower().str.strip(
                            ) == component_2.formula.lower().strip()
                        ) &
                        (
                            mixture_df['State'].str.lower().str.strip()
                            == component_2.state.lower().strip()
                        )
                    )
                elif ignore_component_state:
                    # NOTE: set Name for chosen Name-State
                    component_key_ = 'Name' if component_key == 'Name-State' else 'Formula'

                    # NOTE: compare
                    mask_component_1 = (
                        mixture_df[component_key_].str.lower().str.strip()
                        == component_1.name.lower().strip()
                    )
                    mask_component_2 = (
                        mixture_df[component_key_].str.lower().str.strip()
                        == component_2.name.lower().strip()
                    )
                else:
                    raise ValueError(
                        "Invalid component_key or ignore_component_state configuration.")

                # NOTE: check
                if mask_component_1 is None or mask_component_2 is None:
                    raise ValueError(
                        "Component masks could not be determined.")
                # check if both components are found
                if not mixture_df[mask_component_1].empty and not mixture_df[mask_component_2].empty:
                    all_available = True
                    # count available rows containing the mixture
                    available_count = len(mixture_df)

                    # ! combine rows (series) to dataframe
                    combined_df = pd.concat(
                        [mixture_df[mask_component_1],
                            mixture_df[mask_component_2]]
                    ).drop_duplicates().reset_index(drop=True)
                else:
                    all_available = False
                    combined_df = pd.DataFrame()

            # NOTE: data
            if not combined_df.empty:
                # data as list of dict
                # data = combined_df.to_dict(orient='records')
                # component data first row data
                component_data_1_df = mixture_df[mask_component_1]
                # >> values
                component_data_1 = component_data_1_df.values.tolist()[
                    0]
                # >> set
                component_data[component_1.name]['records'] = component_data_1
                component_data[component_1.name]['header'] = header
                component_data[component_1.name]['symbol'] = symbol
                component_data[component_1.name]['unit'] = unit

                # component data second row data
                component_data_2_df = mixture_df[mask_component_2]
                # >> values
                component_data_2 = component_data_2_df.values.tolist()[
                    0]
                # >> set
                component_data[component_2.name]['records'] = component_data_2
                component_data[component_2.name]['header'] = header
                component_data[component_2.name]['symbol'] = symbol
                component_data[component_2.name]['unit'] = unit

            # SECTION: Format results
            res_dict = {
                'databook_id': databook_id,
                'databook_name': db_name,
                'table_id': table_id,
                'table_name': tb_name,
                'mixture_name': binary_mixture_id,
                'availability': all_available,
                'available_count': available_count,
                'component_data': component_data,
            }

            # >> check
            if res_format == 'json' or res_format == 'str':
                # set json format
                res_json = json.dumps(res_dict, indent=4)
                # >> return
                return res_json
            elif res_format == 'dict':
                # >> return
                return res_dict
            else:
                raise ValueError('Invalid res_format')
        except Exception as e:
            raise Exception(f"Error checking mixture availability: {e}")

    def build_thermo_property(
        self,
        component_names: list[str],
        databook: int | str,
        table: int | str,
        **kwargs
    ) -> ThermoProperty:
        """
        Build a thermodynamic property including data, equation, matrix-data and matrix-equation.

        Parameters
        ----------
        component_names : list[str]
            list of component name (e.g. 'Carbon dioxide')
        databook : int | str
            databook id or name
        table : int | str
            table id or name
        **kwargs
            Additional keyword arguments to pass to the specific build methods.
            - column_name: str, optional
                The name of the column to use for component identification. Default is None.
            - query: bool, optional
                Whether to use a query for component identification. Default is False.

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
            # SECTION: extract kwargs
            # LINK: column name
            column_name = kwargs.get('column_name', None)
            # LINK: query
            query = kwargs.get('query', False)

            # SECTION: detect table type
            tb_info_res_ = self.table_info(databook, table, res_format='dict')

            # SECTION: build thermo property
            if isinstance(tb_info_res_, dict):
                # check
                if tb_info_res_['Type'] == 'Equation':  # ! equation
                    # check
                    if len(component_names) > 1:
                        raise Exception('Only one component name required!')

                    # component name set
                    component_name_ = component_names[0]

                    # build equation
                    return self.build_equation(
                        component_name=component_name_,
                        databook=databook,
                        table=table,
                        column_name=column_name,
                        query=query
                    )
                elif tb_info_res_['Type'] == 'Data':  # ! data
                    # check
                    if len(component_names) > 1:
                        raise Exception('Only one component name required!')

                    # component name set
                    component_name_ = component_names[0]

                    # build data
                    return self.build_data(
                        component_name=component_name_,
                        databook=databook,
                        table=table,
                        column_name=column_name,
                        query=query
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
                        component_names=component_names,
                        databook=databook,
                        table=table,
                        column_name=column_name,
                        query=query
                    )
                else:
                    raise Exception('No data/equation found!')
            else:
                raise Exception('Table loading error!')
        except Exception as e:
            raise Exception(f'Building thermo property error {e}')

    def build_components_thermo_property(
        self,
        components: List[Component],
        databook: int | str,
        table: int | str,
        component_key: Literal[
            'Name-State', 'Formula-State'
        ] = 'Name-State',
        mixture_key: Literal[
            'Name', 'Formula'
        ] = 'Name',
        delimiter: str = '|',
        ignore_component_state: bool = False,
        column_name: Optional[str] = None,
    ) -> ThermoProperty:
        '''
        Build thermo property for a component including data, equation, matrix-data and matrix-equation.

        Parameters
        ----------
        components : str
            string of component name (e.g. 'Carbon dioxide')
        component_state : str, optional
            component state (e.g. 'g', 'l', 's')
        databook : int | str
            databook id or name
        table : int | str
            table id or name
        component_key : Literal['Name-State', 'Formula-State'], optional
            The key to use for identifying the component, by default 'Name-State'.
        mixture_key : Literal['Name', 'Formula'], optional
            The key to use for identifying the mixture, by default 'Name'.
        delimiter : str, optional
            The delimiter used in the mixture identifiers, by default '|'.
        ignore_component_state : bool, optional
            Whether to ignore the state of the components when checking availability, by default False.
        column_name : str, optional
            The name of the column to use for component identification. Default is None.

        Returns
        -------
        ThermoProperty
            table object with data loaded
            - TableEquation
            - TableData
            - TableMatrixEquation
            - TableMatrixData

        Notes
        -----
        - Table should contain columns for 'Name', 'Formula', and 'State'. Otherwise an error will be raised.
        - For 'Equation' and 'Data' types, only one component should be provided.
        - For 'Matrix-Equation' and 'Matrix-Data' types, at least two components should be provided.
        - The `component_key` parameter determines whether to use the component's name or formula along
        '''
        try:
            # NOTE: detect table type
            tb_info_res_ = self.table_info(
                databook=databook,
                table=table,
                res_format='dict'
            )

            # SECTION: build thermo property
            if isinstance(tb_info_res_, dict):
                # check
                if tb_info_res_['Type'] == 'Equation':  # ! equation

                    # NOTE: check components
                    if len(components) != 1:
                        raise Exception('Only one component required!')

                    if not isinstance(components[0], Component):
                        raise Exception('Invalid component!')

                    # set component id
                    component_id_ = None
                    component_state_ = components[0].state
                    column_id_ = None

                    # NOTE: set component id and column id
                    if component_key == 'Name-State':
                        component_id_ = components[0].name
                        column_id_ = 'Name'
                    elif component_key == 'Formula-State':
                        component_id_ = components[0].formula
                        column_id_ = 'Formula'
                    else:
                        raise Exception('Invalid component_key!')

                    # NOTE: build equation
                    return self.build_equation(
                        component_name=component_id_,
                        databook=databook,
                        table=table,
                        column_name=column_id_,
                        component_state=component_state_,
                    )
                elif tb_info_res_['Type'] == 'Data':  # ! data
                    # check
                    if len(components) > 1:
                        raise Exception('Only one component name required!')

                    if not isinstance(components[0], Component):
                        raise Exception('Invalid component!')

                    # NOTE: set component id
                    component_id_ = None
                    component_state_ = components[0].state
                    column_id_ = None

                    # NOTE: set component id and column id
                    if component_key == 'Name-State':
                        component_id_ = components[0].name
                        column_id_ = 'Name'
                    elif component_key == 'Formula-State':
                        component_id_ = components[0].formula
                        column_id_ = 'Formula'
                    else:
                        raise Exception('Invalid component_key!')

                    # NOTE: build data
                    return self.build_data(
                        component_name=component_id_,
                        databook=databook,
                        table=table,
                        column_name=column_id_,
                        component_state=component_state_,
                    )
                elif tb_info_res_['Type'] == 'Matrix-Data':  # ! matrix-data
                    # NOTE: check components
                    if len(components) != 2:
                        raise Exception(
                            'Two components required for matrix-data!')

                    if not all(isinstance(comp, Component) for comp in components):
                        raise Exception('Invalid components!')

                    # NOTE: mixture key
                    mixture_id = create_binary_mixture_id(
                        component_1=components[0],
                        component_2=components[1],
                        mixture_key=mixture_key
                    )

                    # set component names
                    component_names_ = [comp.name for comp in components]
                    # set component formulas
                    component_formulas_ = [comp.formula for comp in components]
                    # set component states
                    component_states_ = [comp.state for comp in components]

                    # NOTE: set column name
                    if column_name is None:
                        column_name = 'Mixture'

                    # NOTE: mixture data
                    # component data
                    component_data = None

                    try:
                        mixture_data = self.get_binary_mixture_data(
                            components=components,
                            databook=databook,
                            table=table,
                            column_name=column_name,
                            component_key=component_key,
                            mixture_key=mixture_key,
                            delimiter=delimiter,
                            ignore_component_state=ignore_component_state,
                            res_format='dict'
                        )

                        # >> set
                        if (
                            isinstance(mixture_data, dict) and
                            mixture_data.get('availability', False)
                        ):
                            # component data
                            component_data = mixture_data.get(
                                'component_data',
                                None
                            )
                        else:
                            logger.error(
                                'Mixture data not available! Checking component state ignore option may help.')
                            raise
                    except Exception as e:
                        raise Exception(f'Loading mixture data error {e}')

                    # NOTE: build matrix-data
                    return self.build_matrix_data(
                        component_names=component_names_,
                        databook=databook,
                        table=table,
                        mixture_id=mixture_id,
                        components_state=component_states_,
                        mixture_data=component_data,
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
        query: bool = False,
        component_state: Optional[str] = None,
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
            databook id or name, id is non-zero-based
        table : int | str
            table id or name, id is non-zero-based
        column_name : str | list
            column name (e.g. 'Name') | list as ['Name','state']
        query : bool
            query to search a dataframe
        component_state : str, optional
            component state (e.g. 'g', 'l', 's')

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
                component_name=component_name,
                databook_id=databook_id,
                table_id=table_id,
                column_name=column_name,
                query=query,
                component_state=component_state
            )

            # check loading state
            if component_data is not None:
                # check availability
                if len(component_data) > 0:
                    # ! reset data
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
        query: bool = False,
        component_state: Optional[str] = None,
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
        component_state : str, optional
            component state (e.g. 'g', 'l', 's')

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

            # check tb_name
            if tb_name.strip() == '' or tb_name is None:
                logger.error('Table name not found!')

            # SECTION: get data from api
            # ! dataframe and PayLoadType
            component_data = self.get_component_data(
                component_name=component_name,
                databook_id=databook_id,
                table_id=table_id,
                column_name=column_name,
                query=query,
                component_state=component_state
            )

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
                        logger.error("The selected table contains no data for building\
                            data! check table id and try again.")

                        raise Exception('Building data failed!')

                    # ! build data
                    # * construct template
                    # check eq exists
                    dts = self.data_load(
                        databook_id,
                        table_id
                    )

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
        query: bool = False,
        mixture_id: Optional[str] = None,
        component_key: Literal['Name-State', 'Formula-State'] = 'Name-State',
        **kwargs
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
        query : bool
            query to search a dataframe
        mixture_id : str, optional
            mixture id (e.g. 'Methanol-Ethanol')
        component_key : Literal['Name-State', 'Formula-State'], optional
                The key to use for identifying the component, by default 'Name-State'.
        **kwargs
            Additional keyword arguments.
            - mixture_data: dict, optional
                Pre-fetched mixture data to use instead of querying the database again.

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
                # column_name = 'Name'
                # set based on component_key
                column_name = 'Name' if component_key == 'Name-State' else 'Formula'

            # find databook zero-based id (real)
            db, db_name, db_rid = self.find_databook(databook)
            # databook id
            databook_id = db_rid + 1

            # find table zero-based id
            tb_id, tb_name = self.find_table(
                databook=databook,
                table=table
            )
            # table id
            table_id = tb_id + 1

            # NOTE: matrix table
            # ! retrieve all data from matrix-table
            # ? usually matrix-table data are limited
            matrix_table = self.table_data(
                databook=databook,
                table=table
            )

            # SECTION: get binary mixture if provided
            # init mixture data
            mixture_data = None

            # check mixture id
            if mixture_id:
                # binary mixture data
                mixture_data = kwargs.get('mixture_data', None)
                # >> check
                if mixture_data is None:
                    # log
                    logging.info(
                        f'Loading mixture data for {mixture_id} from databook {databook_id} table {table_id}...')
                    raise NotImplementedError(
                        'Loading mixture data from databook is not implemented yet. Please provide mixture_data as an argument.')

            # SECTION: get data from api
            component_data_pack = []

            # NOTE: looping through components
            for component_name in component_names:
                # component name
                component_name = str(component_name).strip()

                # NOTE: get data
                # ! (check only by Name/Formula)
                # component data consists of:
                # header, symbol, units, records
                if mixture_data:
                    # get data from mixture_data
                    component_data = mixture_data.get(
                        component_name, None
                    )
                else:
                    # get data from api/local
                    component_data = self.get_component_data(
                        component_name=component_name,
                        databook_id=databook_id,
                        table_id=table_id,
                        column_name=column_name,
                        query=query,
                        matrix_tb=True
                    )

                # NOTE: get component formula
                # check type to consider only PayLoadType
                if (
                    component_data is not None and
                    (
                        not isinstance(component_data, pd.DataFrame) or
                        not component_data.empty
                    )
                ):
                    # header
                    header_ = component_data['header']
                    # records
                    records_ = component_data['records']

                    # component formula
                    # component_name = None
                    # component formula
                    component_formula = None
                    # component state
                    component_state = None

                    # >> find formula if header contains Formula
                    for i, h in enumerate(header_):
                        if h.lower() == 'formula':
                            # set name
                            component_formula = records_[i]
                            break

                    # >> find name if header contains Name
                    for i, h in enumerate(header_):
                        if h.lower() == 'name':
                            # set name
                            component_name = records_[i]
                            break

                    # >> find state if header contains State
                    for i, h in enumerate(header_):
                        if h.lower() == 'state':
                            # set name
                            component_state = records_[i]
                            break
                else:
                    # log
                    logging.warning(
                        f"Data for {component_name} not available!")
                    component_formula = None
                    component_state = None

                # save
                component_data_pack.append({
                    'component_name': component_name,
                    'component_formula': component_formula,
                    'component_state': component_state,
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
                        databook=databook_id,
                        table=table_id
                    )

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
                                # NOTE: mixture id
                                dts.mixture_id = mixture_id

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
