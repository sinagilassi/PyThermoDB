# import libs
import logging
from typing import Dict, List
from pyThermoDB.core import TableEquation, TableData
from pythermodb_settings.models import Component, ComponentReferenceThermoDB
from rich import print
import pyThermoDB as ptdb
import pickle
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
# ! build type
print("ThermoDB Build Type:", data_thermodb.build_type)
# ! component identifiers
print("Component Name:", data_thermodb.component_name)
print("Component Formula:", data_thermodb.component_formula)
print("Component State:", data_thermodb.component_state)

# SECTION: check all properties and functions registered
print(data_thermodb.check())

# SECTION: get all function details
print("[bold green]Function Details:[/bold green]")
print(data_thermodb.all_function_details())

# SECTION: get all data details
print("[bold green]Data Details:[/bold green]")
print(data_thermodb.all_data_details())

# SECTION: select property
# general data
prop1_ = data_thermodb.select('CUSTOM-REF-1::general_data')
# check
if not isinstance(prop1_, TableData):
    raise TypeError("Not TableEquation")

# type
print(type(prop1_))
print(prop1_.prop_data)
# get all data
all_tb_data = prop1_.table_values
# to array
size_bytes = len(pickle.dumps(all_tb_data))
print(size_bytes, "bytes")
# bytes to KB
print(size_bytes / 1024, "KB")
# bytes to MB
print(size_bytes / (1024 ** 2), "MB")

# load data
print(prop1_.get_property("MW"))


# ? ==============================================
# NOTE: ideal-gas-heat-capacity calculation
# ? ==============================================
Cp_eq = data_thermodb.select_function(
    function_name='CUSTOM-REF-1::ideal_gas_heat_capacity_at_constant_pressure'
)
print(type(Cp_eq))

# TableEquation instance
if not isinstance(Cp_eq, TableEquation):
    raise TypeError("Cp_eq is not an instance of TableEquation.")

# equation summary
print(Cp_eq.summary)

# NOTE: calculate Cp at T=300 K
T = 300  # temperature in K
Cp_value = Cp_eq.cal(T=T)
print(
    f"[bold white]Calculated ideal-gas-heat-capacity at T={T} K:[/bold white]")
print(Cp_value)


# NOTE: check general data
general_data = data_thermodb.select('CUSTOM-REF-1::general_data')
print(type(general_data))

# TableData instance
if not isinstance(general_data, TableData):
    raise TypeError("general_data is not an instance of TableData.")

# symbols
print("General Data Symbols:")
print(general_data.table_symbols)
