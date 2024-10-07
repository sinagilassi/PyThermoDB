# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp
import os

# dir
# print(dir(pt))
# get versions
# print(pt.get_version())
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
# ====================================
# files
yml_file = 'test-general\\general data.yml'
yml_path = os.path.join(os.getcwd(), yml_file)
# csv files (data/equation tables)
csv_file_1 = 'test-general\\The Molar Heat Capacities of Gases in the Ideal Gas (Zero-Pressure) State.csv'
csv_file_2 = 'test-general\\General Data.csv'
csv_file_3 = 'test-general\\Vapor Pressure.csv'
csv_path_1 = os.path.join(os.getcwd(), csv_file_1)
csv_path_2 = os.path.join(os.getcwd(), csv_file_2)
csv_path_3 = os.path.join(os.getcwd(), csv_file_3)

# custom ref
ref = {'yml': [yml_path], 'csv': [csv_path_1, csv_path_2, csv_path_3]}

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
tb_list = thermo_db.list_tables(4)
print(tb_list)

# ====================================
# DISPLAY TABLE INFO
# ====================================
# display a table
tb_info = thermo_db.table_info(4, 1)
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
comp1 = "carbon dioxide"
# COMP1_check_availability = thermo_db.check_component(comp1, 4, 1)
# COMP1_check_availability = thermo_db.check_component(comp1, 4, 2)
COMP1_check_availability = thermo_db.check_component(comp1, 4, 3)

# query
# query = f"Name.str.lower() == '{comp1.lower()}' & State == 'g'"
# COMP1_check_availability = thermo_db.check_component(
#     comp1, 3, 2, query, query=True)


# ====================================
# BUILD DATA
# ====================================
# build data
comp1_data = thermo_db.build_data(comp1, 4, 2)
pp(comp1_data.data_structure())

pp(comp1_data.get_property(6))
# by symbol
pp(float(comp1_data.get_property('dHf_IG')['value']))


# ====================================
# BUILD EQUATION
# ====================================
# ! equation 1
# build equation
comp1_eq = thermo_db.build_equation(comp1, 4, 1)

# search a component using query
# comp1_eq = thermo_db.build_equation(
#     comp1, 3, 1)

# load parms
pp(comp1_eq.parms)
pp(comp1_eq.parms_values)
# equation details
pp(comp1_eq.equation_parms())
pp(comp1_eq.equation_args())
pp(comp1_eq.equation_body())
pp(comp1_eq.equation_return())

# check custom integral
pp(comp1_eq.custom_integral)
# check body
pp(comp1_eq.check_custom_integral_equation_body('Cp/RT'))
pp(comp1_eq.check_custom_integral_equation_body('Cp/R'))

# cal
Cp_cal = comp1_eq.cal(T=298.15)
pp(Cp_cal)

# first derivative
Cp_cal_first = comp1_eq.cal_first_derivative(T=273.15)
pp(Cp_cal_first)

# second derivative
Cp_cal_second = comp1_eq.cal_second_derivative(T=273.15)
pp(Cp_cal_second)

# integral
Cp_cal_integral = comp1_eq.cal_integral(T1=298.15, T2=320)
pp(Cp_cal_integral)

# custom integral
# Cp/RT
Cp_cal_custom_integral_Cp__RT = comp1_eq.cal_custom_integral(
    'Cp/RT', T1=298.15, T2=373.15)
pp(Cp_cal_custom_integral_Cp__RT)
# Cp/R
Cp_cal_custom_integral_Cp__R = comp1_eq.cal_custom_integral(
    'Cp/R', T1=298.15, T2=373.15)
pp(Cp_cal_custom_integral_Cp__R)

# ! equation 2
# build equation
vapor_pressure_eq = thermo_db.build_equation(comp1, 4, 3)

pp(vapor_pressure_eq.equation_args())
pp(vapor_pressure_eq.equation_return())
VaPr = vapor_pressure_eq.cal(T=304.21)
pp(VaPr)
# integral
VaPr_cal_integral = vapor_pressure_eq.cal_integral(T1=298.15, T2=320)
pp(VaPr_cal_integral)

# custom
pp(vapor_pressure_eq.custom_integral)
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