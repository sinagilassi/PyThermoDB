# import libs
import logging
from typing import Dict, List
from pyThermoDB import check_and_build_component_thermodb
from pyThermoDB.references import component_reference_mapper
from pyThermoDB.core import TableEquation, TableData
from pythermodb_settings.models import Component, ComponentReferenceThermoDB
from rich import print
from pythermodb_settings.models import ComponentConfig
import os
# local
from ref_content import REFERENCE_CONTENT

# NOTE: logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ? ==============================================
# SECTION: current file path and database path
# ? ==============================================
# NOTE: current file path
parent_path = os.path.dirname(os.path.abspath(__file__))
print(f"parent_path: {parent_path}")

# database
db_path = os.path.join(parent_path, 'thermodb')
print(f"db_path: {db_path}")

# ? ==============================================
# SECTION: check component availability
# ? ==============================================
component_name = 'carbon dioxide'
component_formula = 'CO2'
component_state = 'g'

component = Component(
    name=component_name,
    formula=component_formula,
    state=component_state
)

# component id
component_id = f"{component_name}-{component_state}"
print(f"component_id: {component_id}")

# ? ==============================================
# SECTION: Map Component Reference ThermoDB
# ? ==============================================

# ! ignore_state_props to ignore state check for specific properties
ignore_state_props = ['Cp_IG', 'MW', 'VaPr']
component_ref_thermodb2: ComponentReferenceThermoDB = component_reference_mapper(
    component=component,
    reference_content=REFERENCE_CONTENT,
    component_key='Formula-State',
    ignore_state_props=ignore_state_props
)

print("[bold green]Ignored State Properties:[/bold green]")
print(ignore_state_props)


print("component ref thermodb 2:")
print(component_ref_thermodb2)


# ! custom reference
custom_reference: Dict[str, List[str]] = {'reference': [REFERENCE_CONTENT]}
# ! reference config
reference_config: Dict[
    str,
    ComponentConfig
] = component_ref_thermodb2.reference_thermodb.configs
# ! ignore labels
ignore_labels = component_ref_thermodb2.reference_thermodb.ignore_labels

# ? ==============================================
# SECTION: Build Component ThermoDB
# ? ==============================================
# build component thermodb
component_thermodb = check_and_build_component_thermodb(
    component=component,
    reference_config=reference_config,
    custom_reference=custom_reference,
    component_key='Formula-State',
    ignore_state_props=ignore_labels,
    thermodb_name=component_id,
    thermodb_save=True,
    thermodb_save_path=db_path,
    include_data=False,
)

print(
    f"[bold green]Component ThermoDB (from custom reference):[/bold green]")
print(ignore_state_props)

print("Component ThermoDB:")
print({component_thermodb})
print(type(component_thermodb))

# ? ==============================================
# SECTION: Check Component ThermoDB
# ? ==============================================

# check result
if component_thermodb is None:
    print("[bold red]Failed to build Component ThermoDB.[/bold red]")
    raise ValueError("Component ThermoDB build failed.")

# NOTE: ideal-gas-heat-capacity calculation
Cp_eq = component_thermodb.select_function(
    function_name='CUSTOM-REF-1::ideal-gas-heat-capacity'
)
print(type(Cp_eq))

# TableEquation instance
if not isinstance(Cp_eq, TableEquation):
    raise TypeError("Cp_eq is not an instance of TableEquation.")

# equation summary
print(Cp_eq.summary)

# ! normalized equation
print(Cp_eq.normalized_fn_body(1))

# ! normalized all equations
print(Cp_eq.normalized_fns())

# NOTE: calculate Cp at T=300 K
T = 300  # temperature in K
Cp_value = Cp_eq.cal(T=T)
print(
    f"[bold white]Calculated ideal-gas-heat-capacity at T={T} K:[/bold white]")
print(Cp_value)


# NOTE: check general data
general_data = component_thermodb.select('CUSTOM-REF-1::general-data')
print(type(general_data))

# TableData instance
if not isinstance(general_data, TableData):
    raise TypeError("general_data is not an instance of TableData.")

# symbols
print("General Data Symbols:")
print(general_data.table_symbols)
