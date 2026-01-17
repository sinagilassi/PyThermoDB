# import libs
import logging
import yaml
import os
from typing import List
from pythermodb_settings.models import Component
from pyThermoDB import build_component_thermodb_from_reference, ComponentThermoDB
from pyThermoDB.core import TableEquation, TableData
from rich import print
# local
from reference_content import REFERENCE_CONTENT

# NOTE: logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ? =====================================================
# SECTION: paths
# ? =====================================================
# NOTE: current file path
parent_path = os.path.dirname(os.path.abspath(__file__))
print(f"parent_path: {parent_path}")

# database
db_path = os.path.join(parent_path, 'thermodb')
print(f"db_path: {db_path}")


# ? =====================================================
# SECTION: load reference content
# ? =====================================================
# NOTE: reference path
reference_path = r"D:\Google Cloud\Python Source\pyThermoDB\data\upd\reference_content.yaml"

# load reference content from yaml file and convert to string
with open(reference_path, 'r') as file:
    reference_data = yaml.safe_load(file)

# convert back to yaml string
REFERENCE_CONTENT = yaml.dump(reference_data)
# print(f"REFERENCE_CONTENT: {REFERENCE_CONTENT}")

# ? =====================================================
# SECTION: check component availability
# ? =====================================================
component_name = 'acetaldehyde'
component_formula = 'C2H4O'
component_state = 'g'
# component id
component_id = f"{component_name}-{component_state}"
print(f"component_id: {component_id}")

# ? =====================================================
# SECTION: build component thermodb with ignore state
# ? =====================================================
# NOTE: ignore state for specific properties
ignore_state_props = ['MW', 'VaPr', 'Cp_LIQ', 'Cp_IG', 'rho_LIQ']
thermodb_component_ignore_state_: ComponentThermoDB | None = build_component_thermodb_from_reference(
    component_name=component_name,
    component_formula=component_formula,
    component_state=component_state,
    reference_content=REFERENCE_CONTENT,
    component_key='Formula-State',
    ignore_state_props=ignore_state_props,
    thermodb_name=component_id,
    thermodb_save=True,
    thermodb_save_path=db_path,
)
# check
if thermodb_component_ignore_state_ is None:
    raise ValueError(
        "Failed to build component ThermoDB with ignore state properties.")

# NOTE: thermodb
thermodb_ignore_state_ = thermodb_component_ignore_state_.thermodb
print(f"thermodb_ignore_state_: {thermodb_ignore_state_}")
# check
print(f"thermodb_ignore_state_ checks: {thermodb_ignore_state_.check()}")

# ? =====================================================
# SECTION: check fnctions and data details
# ? =====================================================
# function details
functions_list = thermodb_ignore_state_.all_function_details()
# >> check
if functions_list is None:
    raise ValueError("Failed to get functions list.")

print("Functions List:")
for func in functions_list:
    print(func)

# data details
data_list = thermodb_ignore_state_.all_data_details()
# >> check
if data_list is None:
    raise ValueError("Failed to get data list.")
print("Data List:")
for data in data_list:
    print(data)

# ? ==============================================
# SECTION: Check Component ThermoDB
# ? ==============================================
# create table for temperature
T = {
    "Tc": 305.32,
    "Cp_IG": {
        "T_min": 200,
        "T_max": 1500,
    },
    "Cp_LIQ": {
        "T_min": 150.15,
        "T_max": 294.00,
    },
    "VaPr": {
        "T_min": 150.15,
        "T_max": 466,
    },
    "rho_LIQ": {
        "T_min": 150.15,
        "T_max": 466,
    },
}


# check result
if thermodb_ignore_state_ is None:
    print("[bold red]Failed to build Component ThermoDB.[/bold red]")
    raise ValueError("Component ThermoDB build failed.")

# ! check ideal-gas-heat-capacity function
# NOTE: ideal-gas-heat-capacity calculation
Cp_eq = thermodb_ignore_state_.select_function(
    function_name='CUSTOM-REF-1::ideal_gas_heat_capacity_at_constant_pressure'
)
print(type(Cp_eq))

# TableEquation instance
if not isinstance(Cp_eq, TableEquation):
    raise TypeError("Cp_eq is not an instance of TableEquation.")

# equation summary
print(Cp_eq.summary)

# NOTE: calculate Cp
Tmin = T['Cp_IG']['T_min']
Tmax = T['Cp_IG']['T_max']
Cp_value = Cp_eq.cal(T=Tmin)
print(
    f"[bold white]Calculated ideal-gas-heat-capacity at T={Tmin} K:[/bold white]")
print(Cp_value)
# Tmax
Cp_value = Cp_eq.cal(T=Tmax)
print(
    f"[bold white]Calculated ideal-gas-heat-capacity at T={Tmax} K:[/bold white]")
print(Cp_value)

# ! check liquid heat capacity function
# NOTE: liquid-heat-capacity function
Cp_liq_eq = thermodb_ignore_state_.select_function(
    function_name='CUSTOM-REF-1::liquid_heat_capacity_at_constant_pressure'
)
print(type(Cp_liq_eq))
# TableEquation instance
if not isinstance(Cp_liq_eq, TableEquation):
    raise TypeError("Cp_liq_eq is not an instance of TableEquation.")

# equation summary
print(Cp_liq_eq.summary)

# NOTE: calculate Cp_liq
Tmin = T['Cp_LIQ']['T_min']
Tmax = T['Cp_LIQ']['T_max']
Tc = T['Tc']

Cp_liq_value = Cp_liq_eq.cal(T=Tmin, Tc=Tc)
print(
    f"[bold white]Calculated liquid-heat-capacity at T={Tmin} K:[/bold white]")
print(Cp_liq_value)

# Tmax
Cp_liq_value = Cp_liq_eq.cal(T=Tmax, Tc=Tc)
print(
    f"[bold white]Calculated liquid-heat-capacity at T={Tmax} K:[/bold white]")
print(Cp_liq_value)

# ! check vapor-pressure function
# NOTE: vapor pressure function
Pv_eq = thermodb_ignore_state_.select_function(
    function_name='CUSTOM-REF-1::vapor_pressure'
)

# Tmin/Tmax [K]
Tmin = T['VaPr']['T_min']
Tmax = T['VaPr']['T_max']
print(type(Pv_eq))
# TableEquation instance
if not isinstance(Pv_eq, TableEquation):
    raise TypeError("Pv_eq is not an instance of TableEquation.")

# equation summary
print(Pv_eq.summary)
# NOTE: calculate Pv
Pv_value = Pv_eq.cal(T=Tmin)
print(
    f"[bold white]Calculated vapor pressure at T={Tmin} K:[/bold white]")
print(Pv_value)
# Tmax
Pv_value = Pv_eq.cal(T=Tmax)
print(
    f"[bold white]Calculated vapor pressure at T={Tmax} K:[/bold white]")
print(Pv_value)

# ! check liquid-density function
# NOTE: liquid density function
rho_eq = thermodb_ignore_state_.select_function(
    function_name='CUSTOM-REF-1::liquid_density'
)
print(type(rho_eq))
# TableEquation instance
if not isinstance(rho_eq, TableEquation):
    raise TypeError("rho_eq is not an instance of TableEquation.")

# equation summary
print(rho_eq.summary)
# NOTE: calculate rho
Tmin = T['rho_LIQ']['T_min']
Tmax = T['rho_LIQ']['T_max']

rho_value = rho_eq.cal(T=Tmin)
print(
    f"[bold white]Calculated liquid density at T={Tmin} K:[/bold white]")
print(rho_value)
# Tmax
rho_value = rho_eq.cal(T=Tmax)
print(
    f"[bold white]Calculated liquid density at T={Tmax} K:[/bold white]")
print(rho_value)


# ! check general data
# NOTE: check general data
general_data = thermodb_ignore_state_.select('CUSTOM-REF-1::general_data')
print(type(general_data))

# TableData instance
if not isinstance(general_data, TableData):
    raise TypeError("general_data is not an instance of TableData.")

# symbols
print("General Data Symbols:")
print(general_data.table_symbols)

# content
print("General Data Content:")
print(general_data.property_names)
print(general_data.prop_data)
