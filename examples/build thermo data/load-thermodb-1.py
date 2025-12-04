# import libs
import logging
from typing import Dict, List
from pyThermoDB.core import TableEquation
from pythermodb_settings.models import Component, ComponentReferenceThermoDB
from rich import print
import pyThermoDB as ptdb
import os

# NOTE: logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NOTE: current file path
parent_path = os.path.dirname(os.path.abspath(__file__))
print(f"parent_path: {parent_path}")

# database
db_path = os.path.join(parent_path, 'thermodb')
print(f"db_path: {db_path}")

# SECTION: check component availability
component_name = 'acetaldehyde'
component_formula = 'C2H4O'
component_state = 'g'

component = Component(
    name=component_name,
    formula=component_formula,
    state=component_state
)

# component id
component_id = f"{component_name}-{component_state}"
print(f"component_id: {component_id}")

# component thermodb file path
comp_thermodb = os.path.join(db_path, f"{component_id}.pkl")
print(f"comp_thermodb: {comp_thermodb}")

# SECTION: load thermodb
data_thermodb = ptdb.load_thermodb(thermodb_file=comp_thermodb)
print(type(data_thermodb))

# NOTE: metadata
# ! build version
print("ThermoDB Build Version:", data_thermodb.build_version)
# ! build date
print("ThermoDB Build Date:", data_thermodb.build_date)
# ! python version
print("ThermoDB Build Python Version:", data_thermodb.build_python)

# SECTION: check all properties and functions registered
print(data_thermodb.check())

# SECTION: get all function details
print("[bold green]Function Details:[/bold green]")
print(data_thermodb.all_function_details())

# SECTION: get all data details
print("[bold green]Data Details:[/bold green]")
print(data_thermodb.all_data_details())
