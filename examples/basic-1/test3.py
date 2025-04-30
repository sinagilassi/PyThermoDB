# import packages/modules
import pyThermoDB as ptdb
import os
from rich import print

# get versions
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
# ====================================
# parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))

# files
yml_file = 'ref1.yml'
yml_path = os.path.join(parent_dir, yml_file)

csv_file_1 = 'Table A.II The Molar Heat Capacities of Gases in the Ideal Gas (Zero-Pressure) State.csv'
csv_file_2 = 'Table A.IV Enthalpies and Gibbs Energies of Formation.csv'
csv_path_1 = os.path.join(parent_dir, csv_file_1)
csv_path_2 = os.path.join(parent_dir, csv_file_2)

# custom ref
ref = {'reference': [yml_path], 'tables': [csv_path_1, csv_path_2]}

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
comp1_data = thermo_db.build_data(comp1, 'CO2 Hydrogenation', 2)
print(comp1_data.data_structure())

print(comp1_data.get_property(6))


# ====================================
# BUILD EQUATION
# ====================================
# build equation
comp1_eq = thermo_db.build_equation(comp1, 'CO2 Hydrogenation', 1)

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
# BUILD THERMODB
# ====================================
# build a thermodb
thermo_db = ptdb.build_thermodb()
print(type(thermo_db))

# add TableData
thermo_db.add_data('general', comp1_data)
# add TableEquation
thermo_db.add_data('heat-capacity', comp1_eq)
# add string
# thermo_db.add_data('dHf', {'dHf_IG': 152})
# export
# thermo_db.export_data_structure(comp1)
# save
thermo_db.save(f'{comp1}-1.pkl', file_path=parent_dir)
