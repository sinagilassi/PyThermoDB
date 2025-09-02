# import packages/modules
import os
from typing import Any, Dict
from rich import print
import pyThermoDB as ptdb
from pyThermoDB.core import TableData, TableEquation

# version
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
# ====================================
# parent path
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Parent directory: {parent_dir}")

# databook name
DATABOOK_NAME = 'CO2-Hydrogenation Reaction'
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

# custom ref
ref: Dict[str, Any] = {
    'reference': [yml_path],
    'tables': [csv_path_1, csv_path_2, csv_path_3]
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
# SELECT A DATABOOK
# ====================================
# table list
tb_list = thermo_db.list_tables(DATABOOK_NAME)
print(tb_list)

# ====================================
# DISPLAY TABLE INFO
# ====================================
# display a table
# tb_info = thermo_db.table_info(DATABOOK_NAME, 2)
# print(tb_info)

tb_info = thermo_db.table_info(DATABOOK_NAME, 'General Data')
print(tb_info)

# ====================================
# LOAD TABLE
# ====================================
# load equation
# tb_eq = thermo_db.equation_load(DATABOOK_NAME, 'Vapor Pressure')
# load equation
tb_eq = thermo_db.equation_load(
    DATABOOK_NAME,
    'The Molar Heat Capacities of Gases in the Ideal Gas (Zero-Pressure) State'
)
# equation structure
tb_eq_structure = tb_eq.eq_structure(1)
print(tb_eq_structure)

# ====================================
# CHECK COMPONENT AVAILABILITY IN A TABLE
# ====================================
# check component availability in the databook and table
comp1 = "Carbon Dioxide"
COMP1_check_availability = thermo_db.check_component(
    comp1,
    DATABOOK_NAME,
    'General Data'
)

# query
# query = f"Name.str.lower() == '{comp1.lower()}' & State == 'g'"
# COMP1_check_availability = thermo_db.check_component(
#     comp1, 3, 2, query, query=True)


# ====================================
# BUILD DATA
# ====================================
# build data
comp1_data = thermo_db.build_data(
    comp1,
    DATABOOK_NAME,
    'General Data'
)
print(comp1_data.data_structure())

print(comp1_data.get_property(6))
# by symbol
print(float(comp1_data.get_property('EnFo')['value']))


# ====================================
# BUILD EQUATION
# ====================================
# ! equation 1
# build equation
comp1_eq = thermo_db.build_equation(
    comp1,
    DATABOOK_NAME,
    'The Molar Heat Capacities of Gases in the Ideal Gas (Zero-Pressure) State'
)

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
vapor_pressure_eq = thermo_db.build_equation(
    comp1,
    DATABOOK_NAME,
    'Vapor Pressure'
)

print(vapor_pressure_eq.equation_args())
print(vapor_pressure_eq.equation_return())
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
# print(comp1_eq.equation_parms())
# print(comp1_eq.equation_args())
# print(comp1_eq.equation_body())
# print(comp1_eq.equation_return())

# cal (using sympy)
# Cp_cal = comp1_eq.cal(sympy_format=True, T=290)
# print(Cp_cal)


# ====================================
# BUILD THERMODB
# ====================================
# build a thermodb
thermo_db = ptdb.build_thermodb()
print(type(thermo_db))

# * add TableData
thermo_db.add_data('GENERAL', comp1_data)
# second data
thermo_db.add_data('GENERAL-2', comp1_data)
# * add TableEquation
thermo_db.add_data('heat-capacity', comp1_eq)
thermo_db.add_data('vapor-pressure', vapor_pressure_eq)
# add string
# thermo_db.add_data('dHf', {'dHf_IG': 152})
# file name
# thermodb_file_path = os.path.join(os.getcwd(), f'{comp1}')

# ====================================
# LIST THERMO DATA (DATA,EQUATIONS)
# ====================================
print(thermo_db.list_data())

# ====================================
# REMOVE A RECORD
# ====================================
# remove a record
# print(thermo_db.delete_data('GENERAL-2'))
# check data after change (remove data)
# print(thermo_db.list_data())

# ====================================
# CLEAN
# ====================================
# print(thermo_db.clean())


# ====================================
# SAVE
# ====================================
# save
thermo_db.save(
    f'{comp1}-multiple-3',
    file_path=parent_dir,
)

# ====================================
# CHECK THERMODB
# ====================================
# check all properties and functions registered
print(thermo_db.check_properties())
print(thermo_db.check_functions())
