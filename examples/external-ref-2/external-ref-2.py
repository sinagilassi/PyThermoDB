# import packages/modules
from typing import Dict, Any, List
import pyThermoDB as ptdb
import os
from rich import print

# dir
# print(dir(pt))
# get versions
# print(pt.get_version())
print(ptdb.__version__)

# ====================================
# ! CUSTOM REFERENCES
# ====================================
# current directory
current_directory = os.getcwd()
print(f"Current directory: {current_directory}")
# parent directory
parent_directory = os.path.dirname(os.path.abspath(__file__))
print(f"Parent directory: {parent_directory}")
# target directory
test_dir = os.path.join(current_directory, 'examples', 'external-ref-2')
print(f"Test directory: {test_dir}")

# NOTE: files
# file 1
yml_file_1 = 'general data-1.yml'
yml_path_1 = os.path.join(test_dir, yml_file_1)
print(f"YAML file path: {yml_path_1}")
# file 2
yml_file_2 = 'general data-2.yml'
yml_path_2 = os.path.join(test_dir, yml_file_2)
print(f"YAML file path: {yml_path_2}")

# NOTE: csv files (data/equation tables)
# data
csv_file_1 = 'The Molar Heat Capacities of Gases in the Ideal Gas (Zero-Pressure) State.csv'
# equation
csv_file_2 = 'General Data.csv'
csv_file_3 = 'Vapor Pressure.csv'

# set csv files
csv_path_1 = os.path.join(test_dir, csv_file_1)
csv_path_2 = os.path.join(test_dir, csv_file_2)
csv_path_3 = os.path.join(test_dir, csv_file_3)

# NOTE: custom ref
ref: Dict[str, Any] = {
    'reference': [yml_path_1, yml_path_2],
    'tables': [csv_path_1, csv_path_2, csv_path_3],
}

print(ref)

# ====================================
# INITIALIZATION OWN THERMO DB
# ====================================
thermo_db = ptdb.init(custom_reference=ref)

# ====================================
# GET DATABOOK LIST
# ====================================
db_list = thermo_db.list_databooks()
print(db_list)

# ====================================
# SELECT A DATABOOK
# ====================================
# table list
tb_list = thermo_db.list_tables('GENERAL-1')
print(f"Table list in GENERAL-1: {tb_list}")

tb_list = thermo_db.list_tables('GENERAL-2')
print(f"Table list in GENERAL-2: {tb_list}")

# ====================================
# DISPLAY TABLE INFO
# ====================================
# display a table
tb_info = thermo_db.table_info('GENERAL-1', 2)
print(f"Table info for GENERAL-1, Table 2: {tb_info}")

# display a table
tb_info = thermo_db.table_info('GENERAL-2', 2)
print(f"Table info for GENERAL-2, Table 1: {tb_info}")

# ====================================
# LOAD TABLE
# ====================================
# load equation
tb_eq = thermo_db.equation_load('GENERAL-1', 3)
# equation structure
tb_eq_structure = tb_eq.eq_structure(1)
print(f"Equation structure for GENERAL-1, Table 3: {tb_eq_structure}")

tb_eq = thermo_db.equation_load('GENERAL-2', 3)
# equation structure
tb_eq_structure = tb_eq.eq_structure(1)
print(f"Equation structure for GENERAL-2, Table 3: {tb_eq_structure}")

# ====================================
# CHECK COMPONENT AVAILABILITY IN A TABLE
# ====================================
# check component availability in the databook and table
comp1 = "toluene"
# COMP1_check_availability = thermo_db.check_component(comp1, 3, 2)

# query
# query = f"Name.str.lower() == '{comp1.lower()}' & State == 'g'"
# COMP1_check_availability = thermo_db.check_component(
#     comp1, 3, 2, query, query=True)


# ====================================
# BUILD DATA
# ====================================
# build data
comp1_data_1 = thermo_db.build_data(comp1, 'GENERAL-1', 2)
print(comp1_data_1.data_structure())
print(comp1_data_1.get_property(6))

# databook 2
comp1_data = thermo_db.build_data(comp1, 'GENERAL-2', 2)
print(comp1_data.data_structure())
print(comp1_data.get_property(6))


# ====================================
# BUILD EQUATION
# ====================================
# build equation
comp1_eq = thermo_db.build_equation(comp1, 'GENERAL-1', 3)

# search a component using query
# comp1_eq = thermo_db.build_equation(
#     comp1, 3, 1)

# equation details
print(comp1_eq.equation_parms())
print(comp1_eq.equation_args())
print(comp1_eq.equation_body())
print(comp1_eq.equation_return())

# cal
Cp_cal = comp1_eq.cal(T=290)
print(Cp_cal)

# # first derivative
# Cp_cal_first = comp1_eq.cal_first_derivative(T=273.15)
# print(Cp_cal_first)

# # second derivative
# Cp_cal_second = comp1_eq.cal_second_derivative(T=273.15)
# print(Cp_cal_second)

# # integral
# Cp_cal_integral = comp1_eq.cal_integral(T1=273.15, T2=373.15)
# print(Cp_cal_integral)

# NOTE: databook 2
comp1_eq = thermo_db.build_equation(comp1, 'GENERAL-2', 3)

# search a component using query
# comp1_eq = thermo_db.build_equation(
#     comp1, 3, 1)

# equation details
print(comp1_eq.equation_parms())
print(comp1_eq.equation_args())
print(comp1_eq.equation_body())
print(comp1_eq.equation_return())

# cal
Cp_cal = comp1_eq.cal(T=290)
print(Cp_cal)

# # first derivative
# Cp_cal_first = comp1_eq.cal_first_derivative(T=273.15)
# print(Cp_cal_first)

# # second derivative
# Cp_cal_second = comp1_eq.cal_second_derivative(T=273.15)
# print(Cp_cal_second)

# # integral
# Cp_cal_integral = comp1_eq.cal_integral(T1=273.15, T2=373.15)
# print(Cp_cal_integral)

# ====================================
# BUILD THERMODB
# ====================================
# build a thermodb
thermo_db = ptdb.build_thermodb()
print(type(thermo_db))

# add TableData
thermo_db.add_data('general', comp1_data_1)
# add TableEquation
thermo_db.add_data('vapor-pressure', comp1_eq)
# save
thermo_db.save(f'{comp1}-1.pkl', file_path=parent_directory)

# check
