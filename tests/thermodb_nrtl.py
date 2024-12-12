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
yml_file = 'tests\\nrtl.yml'
yml_path = os.path.join(os.getcwd(), yml_file)
# csv files (data/equation tables)
csv_file_1 = 'tests\\Non-randomness parameters of the NRTL equation.csv'
csv_file_2 = 'tests\\Interaction parameters of the NRTL equation.csv'
csv_path_1 = os.path.join(os.getcwd(), csv_file_1)
csv_path_2 = os.path.join(os.getcwd(), csv_file_2)

# custom ref
ref = {'reference': [yml_path], 'tables': [csv_path_1, csv_path_2]}

# ====================================
# INITIALIZATION OWN THERMO DB
# ====================================
thermo_db = ptdb.init(ref)

# ====================================
# GET DATABOOK LIST
# ====================================
# db_list = thermo_db.list_databooks()
# print(db_list)

# ====================================
# SELECT A DATABOOK
# ====================================
# table list
# tb_list = thermo_db.list_tables('NRTL')
# print(tb_list)

# ====================================
# DISPLAY TABLE INFO
# ====================================
# display a table
# tb_info = thermo_db.table_info(
#     'NRTL', "Non-randomness parameters of the NRTL equation")
# print(tb_info)

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
comp1 = "methanol"
# COMP1_check_availability = thermo_db.check_component(
#     comp1, 'NRTL', "Non-randomness parameters of the NRTL equation")

comp2 = "ethanol"
# COMP1_check_availability = thermo_db.check_component(
#     comp2, 'NRTL', "Non-randomness parameters of the NRTL equation")

# comp3
comp3 = 'benzene'
# query
# query = f"Name.str.lower() == '{comp1.lower()}' & State == 'g'"
# COMP1_check_availability = thermo_db.check_component(
#     comp1, 3, 2, query, query=True)

# ====================================
# LOAD MATRIX DATA
# ====================================
# tb_data_df = thermo_db.table_data(
#     'NRTL', 2)
# print(type(tb_data_df))
# pp(tb_data_df)


# ====================================
# BUILD MATRIX DATA
# ====================================
# build data
nrtl_data = thermo_db.build_matrix_data(
    [comp1, comp2], 'NRTL', "Non-randomness parameters of the NRTL equation")
# pp(nrtl_data.matrix_data_structure())

# pp(nrtl_data.get_property(0, comp1))
# by symbol
# pp(float(comp1_data.get_property('dHf_IG')['value']))

pp(nrtl_data.get_matrix_property("Alpha_i_j",
   [comp1, comp2], symbol_format='alphabetic'))

# property name
prop_name_lists = ["Alpha", comp1, comp3]
prop_name = "_".join(prop_name_lists)
print(prop_name)
pp(nrtl_data.get_matrix_property_by_name(prop_name).get('value'))

# ====================================
# BUILD EQUATION
# ====================================
# ! equation 1
# build equation
comp1_eq = thermo_db.build_equation(comp1, 3, 1)

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

# ! equation 2
# build equation
vapor_pressure_eq = thermo_db.build_equation(comp1, 3, 3)

pp(vapor_pressure_eq.equation_args())
pp(vapor_pressure_eq.equation_return())
VaPr = vapor_pressure_eq.cal(T=304.21)
pp(VaPr)

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
# BUILD THERMODB
# ====================================
# build a thermodb
thermo_db = ptdb.build_thermodb()
pp(type(thermo_db))

# * add TableData
thermo_db.add_data('general', comp1_data)
# * add TableEquation
thermo_db.add_data('heat-capacity', comp1_eq)
thermo_db.add_data('vapor-pressure', vapor_pressure_eq)
# add string
# thermo_db.add_data('dHf', {'dHf_IG': 152})
# file name
# thermodb_file_path = os.path.join(os.getcwd(), f'{comp1}')
# save
thermo_db.save(
    f'{comp1}', file_path='E:\\Python Projects\\pyThermoDB\\tests')

# ====================================
# CHECK THERMODB
# ====================================
# check all properties and functions registered
pp(thermo_db.check_properties())
pp(thermo_db.check_functions())
