# import libs
import logging
from typing import Dict, List
from pyThermoDB.core import TableEquation, TableData
from pythermodb_settings.models import Component, ComponentReferenceThermoDB
from rich import print
import pyThermoDB as ptdb
import pickle
import os
# path

# NOTE: logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NOTE: current file path
parent_path = os.path.dirname(os.path.abspath(__file__))
print(f"parent_path: {parent_path}")

# database
db_path = r'D:\Google Cloud\Python Source\pyThermoDB\data\upd\thermodb'
print(f"db_path: {db_path}")

# SECTION: check component availability
component_name = 'ethane'
component_formula = 'C2H6'
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
        "T_min": 92,
        "T_max": 290,
    },
    "VaPr": {
        "T_min": 90.35,
        "T_max": 305.32,
    },
    "rho_LIQ": {
        "T_min": 90.35,
        "T_max": 305.32,
    },
}


# ! check ideal-gas-heat-capacity function
# NOTE: ideal-gas-heat-capacity calculation
Cp_eq = data_thermodb.select_function(
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
Cp_liq_eq = data_thermodb.select_function(
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
Pv_eq = data_thermodb.select_function(
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
rho_eq = data_thermodb.select_function(
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
general_data = data_thermodb.select('CUSTOM-REF-1::general_data')
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
