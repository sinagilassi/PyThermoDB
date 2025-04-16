# Removed unused imports
import os
import json
import webbrowser
import tempfile
from jinja2 import Environment, FileSystemLoader


def tojson(obj):
    return json.dumps(obj)


def url_for(endpoint, filename=None):
    """
    Generate absolute paths for static files when opening the HTML file directly.
    """
    if endpoint == 'static':
        # Get the directory of the current script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return f'file://{os.path.join(base_dir, "static", filename).replace(os.sep, "/")}'
    return '#'


def render_page(sample_data, page=1, rows_per_page=50, theme="light"):
    """
    Render the HTML page using Jinja2 templates

    Args:
        page: Current page number to display (default=1)
        rows_per_page: Number of rows per page (default=50)
        theme: UI theme, either 'light' or 'dark' (default='light')
        show_all: If True, displays all data without pagination (default=False)
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

    # Calculate pagination values
    total_items = len(sample_data)
    total_pages = (total_items + rows_per_page - 1) // rows_per_page

    # SECTION: Setup Jinja2 environment
    template_loader = FileSystemLoader(
        searchpath=os.path.join(os.path.dirname(__file__), 'templates'))
    template_env = Environment(loader=template_loader)

    # Add the function to Jinja2 environment globals
    template = template_env.get_template('table_view.html')

    # SECTION: Get the template and render it with the data
    rendered_html = template.render(
        title='PyThermoDB Table Viewer',
        app_name='PyThermoDB Viewer',
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
        app_version='1.9.1',
    )

    return rendered_html


def init_app(sample_data, page=1, rows_per_page=50, theme="light"):
    """
    Initialize the application and open the rendered page in a browser

    Args:
        page: Current page number to display (default=1)
        rows_per_page: Number of rows per page (default=50)
        theme: UI theme, either 'light' or 'dark' (default='light')
        show_all: If True, displays all data without pagination (default=False)
    """
    # generate HTML content for the requested page
    html_content = render_page(sample_data,
                               page=page, rows_per_page=rows_per_page, theme=theme)

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
