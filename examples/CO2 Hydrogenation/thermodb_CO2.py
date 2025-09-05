# import packages/modules
from typing import Any, Dict
import os
from rich import print
import pyThermoDB as ptdb
from pyThermoDB.core import TableData, TableEquation

# get versions
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
# ====================================
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Parent directory: {parent_dir}")

# files
yml_file = 'CO2 Hydrogenation.yml'
yml_path = os.path.join(parent_dir, yml_file)
# csv files (data/equation tables)
csv_file_1 = 'The Molar Heat Capacities of Gases in the Ideal Gas (Zero-Pressure) State.csv'
csv_file_2 = 'General Data.csv'
csv_file_3 = 'Vapor Pressure.csv'
csv_path_1 = os.path.join(parent_dir, csv_file_1)
csv_path_2 = os.path.join(parent_dir, csv_file_2)
csv_path_3 = os.path.join(parent_dir, csv_file_3)

# symbols
symbol_file = 'custom_symbol_list.yml'
symbol_path = os.path.join(parent_dir, symbol_file)

# custom ref
ref: Dict[str, Any] = {
    'yml': [yml_path],
    'csv': [
        csv_path_1,
        csv_path_2,
        csv_path_3
    ],
    'symbols': [symbol_path]
}

# ====================================
# INITIALIZATION OWN THERMO DB
# ====================================
thermo_db = ptdb.init(ref)

# ====================================
# GET DATABOOK LIST
# ====================================
db_list = thermo_db.list_databooks()
print(db_list)

# ====================================
# GET SYMBOL LIST
# ====================================
symbol_list = thermo_db.list_symbols(res_format='json')
print(symbol_list)

# ====================================
# SELECT A DATABOOK
# ====================================
# NOTE:
databook = 'CO2-Hydrogenation Reaction'
# table list
tb_list = thermo_db.list_tables(databook)
print(tb_list)

# ====================================
# DISPLAY TABLE INFO
# ====================================
# display a table
tb_info = thermo_db.table_info(databook, 1)
print(tb_info)

tb_info = thermo_db.table_info(databook, 2)
print(tb_info)

tb_info = thermo_db.table_info(databook, 3)
print(tb_info)

# ====================================
# LOAD TABLE
# ====================================
# # load equation
# tb_eq = thermo_db.equation_load(3, 1)
# # equation structure
# tb_eq_structure = tb_eq.eq_structure(1)
# pp(tb_eq_structure)

# ====================================
# CHECK COMPONENT AVAILABILITY IN A TABLE
# ====================================
# check component availability in the databook and table
comp1 = "Carbon Dioxide"
COMP1_check_availability = thermo_db.check_component(comp1, 3, 2)

# query
# query = f"Name.str.lower() == '{comp1.lower()}' & State == 'g'"
# COMP1_check_availability = thermo_db.check_component(
#     comp1, 3, 2, query, query=True)


# ====================================
# BUILD DATA
# ====================================
# build data
comp1_data = thermo_db.build_data(comp1, databook, 2)
print(comp1_data.data_structure())

# ! check property availability
print(comp1_data.is_property_available('GiEnFo'))
print(comp1_data.is_property_available('GiEnFo', search_mode='SYMBOL'))
print(comp1_data.is_property_available('GiEnFo', search_mode='COLUMN'))
print(comp1_data.is_property_available('MW'))
print(comp1_data.is_property_available('molecular-weight'))
print(comp1_data.is_property_available('critical-temperature'))
print(comp1_data.is_property_available('Critical-Temperature'))
print(comp1_data.is_property_available('Critical-Temperature0'))

# get property by column index
print(comp1_data.get_property(6, message=f"{comp1} Enthalpy of formation"))
# by symbol
print(comp1_data.get_property('gibbs-energy-of-formation')['value'])


# ====================================
# BUILD EQUATION
# ====================================
# ! equation 1
# build equation
comp1_eq = thermo_db.build_equation(comp1, databook, 1)

# search a component using query
# comp1_eq = thermo_db.build_equation(
#     comp1, 3, 1)

# load parms
print(comp1_eq.parms)
print(comp1_eq.parms_values)
# equation details
print(comp1_eq.equation_parms())
print(comp1_eq.equation_args())
print(comp1_eq.equation_body())
print(comp1_eq.equation_return())

# cal
Cp_cal = comp1_eq.cal(T=298.15)
print(Cp_cal)

# first derivative
Cp_cal_first = comp1_eq.cal_first_derivative(T=273.15)
print(Cp_cal_first)

# second derivative
Cp_cal_second = comp1_eq.cal_second_derivative(T=273.15)
print(Cp_cal_second)

# integral
Cp_cal_integral = comp1_eq.cal_integral(T1=298.15, T2=320)
print(Cp_cal_integral)

# ! equation 2
# build equation
vapor_pressure_eq = thermo_db.build_equation(comp1, databook, 3)

print(vapor_pressure_eq.equation_args())
print(vapor_pressure_eq.equation_return())
VaPr = vapor_pressure_eq.cal(message=f'{comp1} Vapor Pressure', T=304.21)
VaPr = vapor_pressure_eq.cal(T=304.21)
print(VaPr)

# ====================================
# BUILD EQUATION
# ====================================
# build equation
# comp1_eq = thermo_db.build_equation(comp1, 3, 1)

# search a component using query
# comp1_eq = thermo_db.build_equation(
#     comp1, 3, 1)

# equation details
# pp(comp1_eq.equation_parms())
# pp(comp1_eq.equation_args())
# pp(comp1_eq.equation_body())
# pp(comp1_eq.equation_return())

# cal (using sympy)
# Cp_cal = comp1_eq.cal(sympy_format=True, T=290)
# pp(Cp_cal)

# ====================================
# SECTION: BUILD THERMODB
# ====================================
# name
thermodb_name = comp1.upper()

# build a thermodb
thermo_db = ptdb.build_thermodb()
print(type(thermo_db))

# * add TableData
thermo_db.add_data('general', comp1_data)
# * add TableEquation
thermo_db.add_data('heat-capacity', comp1_eq)
thermo_db.add_data('vapor-pressure', vapor_pressure_eq)
# add string
# thermo_db.add_data('dHf', {'dHf_IG': 152})

# save
thermo_db.save(
    f'{thermodb_name}', file_path=parent_dir)

# ====================================
# CHECK THERMODB
# ====================================
# check all properties and functions registered
print(thermo_db.check_properties())
print(thermo_db.check_functions())
