# import libs
import os
from typing import List, Dict, Optional, Literal, Union, Tuple
import json
import webbrowser
import tempfile
# local
from ..config import __version__, __author__, __email__


class Launcher:
    def __init__(self):
        pass

    def tojson(self, obj):
        return json.dumps(obj)

    def url_for(self, endpoint, filename=None):
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

    def render_page(self, app_data: List[Dict],
                    page: int = 1, rows_per_page: int = 50, theme: Literal['light', 'dark'] = "light"):
        """
        Render the HTML page using Jinja2 templates

        Parameters
        ----------
        app_data : list of dict
            Data to be displayed in the table. Each dictionary represents a row.
        page : int, optional
            Current page number (default is 1)
        rows_per_page : int, optional
            Number of rows per page (default is 50)
        theme : str, optional
            Theme for the table ('light' or 'dark', default is 'light')
        """
        try:
            # SECTION: check if jinja2 is installed
            try:
                from jinja2 import Environment, FileSystemLoader
            except ImportError:
                raise ImportError(
                    "Jinja2 is not installed. Please install it using 'pip install jinja2'.")

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

            # Calculate pagination values
            total_items = len(app_data)
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
            template = template_env.get_template('index.html')

            # SECTION: Get the template and render it with the data
            rendered_html = template.render(
                title='PyThermoDB Table Viewer',
                app_name='PyThermoDB',
                table_title='Python Thermodynamic Databook',
                card_data=app_data,
                total_data=total_items,
                tojson=self.tojson,
                url_for=self.url_for,
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
                author=__author__,
                email=__email__,
            )

            return rendered_html
        except Exception as e:
            raise Exception(
                f"Error rendering HTML page: {e}")

    def launch(self, app_data: List[Dict]):
        """
        Launch the HTML viewer for the given data.

        Parameters
        ----------
        app_data : list of dict
            Data to be displayed in the table. Each dictionary represents a row.
        """
        try:
            # generate HTML content for the requested page
            html_content = self.render_page(
                app_data, page=1, rows_per_page=50, theme='light')

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
        except Exception as e:
            raise Exception(f"Error launching HTML viewer: {e}")
