# import packages/modules
from typing import Any, Dict
import os
from rich import print
# pyThermoDB
import pyThermoDB as ptdb
from pyThermoDB.core import TableData, TableEquation, TableConstants

# get versions
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
# ====================================
# NOTE: parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))

# NOTE: files
yml_file = 'ref1.yml'
yml_path = os.path.join(parent_dir, yml_file)

# NOTE: csv files
# ! because of copyright issue, the csv files are not included in the repo. Please download the csv files from the original source and place them in the same directory as this test file.
# csv directory
csv_dir = os.path.join(parent_dir, '..', '..', 'private', 'csv_files')
# csv files
csv_file_1 = 'Table A.II The Molar Heat Capacities of Gases in the Ideal Gas (Zero-Pressure) State.csv'
csv_file_2 = 'Table A.IV Enthalpies and Gibbs Energies of Formation.csv'
# custom constants
csv_file_3 = 'custom-constants.csv'
csv_path_1 = os.path.join(csv_dir, csv_file_1)
csv_path_2 = os.path.join(csv_dir, csv_file_2)
csv_path_3 = os.path.join(csv_dir, csv_file_3)

# NOTE: custom ref
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
tb_list = thermo_db.list_tables('CO2 Hydrogenation')
print(tb_list)

# ====================================
# DISPLAY TABLE INFO
# ====================================
# display a table
tb_info = thermo_db.table_info('CO2 Hydrogenation', 1)
print(tb_info)

tb_info = thermo_db.table_info('CO2 Hydrogenation', 2)
print(tb_info)

tb_info = thermo_db.table_info('CO2 Hydrogenation', 'custom-constants')
print(tb_info)

# ====================================
# LOAD TABLE
# ====================================
# load equation
tb_eq = thermo_db.equation_load('CO2 Hydrogenation', 1)
# equation structure
tb_eq_structure = tb_eq.eq_structure(1)
print(tb_eq_structure)

# ====================================
# CHECK COMPONENT AVAILABILITY IN A TABLE
# ====================================
# check component availability in the databook and table
# comp1 = "Carbon Dioxide"
comp1 = "Methane"
# COMP1_check_availability = thermo_db.check_component(comp1, 3, 2)

# query
# query = f"Name.str.lower() == '{comp1.lower()}' & State == 'g'"
# COMP1_check_availability = thermo_db.check_component(
#     comp1, 3, 2, query, query=True)


# ====================================
# BUILD DATA
# ====================================
# build data
comp1_data: TableData = thermo_db.build_data(comp1, 'CO2 Hydrogenation', 2)
print(comp1_data.data_structure())

print(comp1_data.get_property(6))

# ! check property availability
print(comp1_data.is_property_available('Cp_IG'))
print(comp1_data.is_property_available('dHf_IG', search_mode='SYMBOL'))
print(comp1_data.is_property_available('dHf_IG', search_mode='COLUMN'))

# dHf_IG (case insensitive)
print(comp1_data.get_property('dHf_IG'))
print(comp1_data.get_property('dhf_IG'))
print(comp1_data.get_property('dhf_iG'))
# print(comp1_data.get_property('dhf_if')) # raise error

# ====================================
# BUILD EQUATION
# ====================================
# build equation
comp1_eq: TableEquation = thermo_db.build_equation(
    comp1,
    'CO2 Hydrogenation',
    1
)

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

# first derivative
# Cp_cal_first = comp1_eq.cal_first_derivative(T=273.15)
# print(Cp_cal_first)

# second derivative
# Cp_cal_second = comp1_eq.cal_second_derivative(T=273.15)
# print(Cp_cal_second)

# integral
# Cp_cal_integral = comp1_eq.cal_integral(T1=273.15, T2=373.15)
# print(Cp_cal_integral)

# ====================================
# BUILD CONSTANTS
# ====================================
# build constants
general_const: TableConstants = thermo_db.build_constants(
    databook='CO2 Hydrogenation',
    table='custom-constants'
)
print(general_const.data_structure())

# access constant
# ! R (scalar)
print(general_const.get_constant('R'))
# ! dG_rxn (dictionary)
print(general_const.get_constant('dG_rxn'))
# ! Xb (string)
print(general_const.get_constant('Xb'))
# ! X (list)
print(general_const.get_constant('X'))
# ! non-existing constant (can raise error)
print(general_const.get_constant('non_existing_constant', strict=False))
# print(general_const.get_constant('non_existing_constant'))

# ====================================
# BUILD THERMODB
# ====================================
# build a thermodb
thermo_db = ptdb.build_thermodb()
print(type(thermo_db))

# add TableData
thermo_db.add_data('general', comp1_data)
# add TableEquation
thermo_db.add_data('heat-capacity', comp1_eq)
# add constants
thermo_db.add_data('custom-constants', general_const)
# add string
# thermo_db.add_data('dHf', {'dHf_IG': 152})
# export
# thermo_db.export_data_structure(comp1)
# save
res_ = thermo_db.save(f'{comp1}-custom-constant-1.pkl', file_path=parent_dir)
print(res_)
