# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp
import os
from rich import print

# version
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
# ====================================
# files
yml_file = 'tests\\nrtl.yml'
yml_path = os.path.join(os.getcwd(), yml_file)
# csv files (data/equation tables)
csv_file_1 = 'tests\\Non-randomness parameters of the NRTL equation.csv'
csv_file_2 = 'tests\\Interaction parameters of the NRTL equation-2.csv'
csv_path_1 = os.path.join(os.getcwd(), csv_file_1)
csv_path_2 = os.path.join(os.getcwd(), csv_file_2)

# custom ref
ref = {
    'reference': [yml_path],
    'tables': [csv_path_1, csv_path_2]
}

# ====================================
# INITIALIZATION OWN THERMO DB
# ====================================
thermo_db = ptdb.init(custom_reference=ref)

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

# # select a table
# tb = thermo_db.select_table(
#     'NRTL', 'Non-randomness parameters of the NRTL equation')
# print(tb)

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
# nrtl_alpha = thermo_db.build_matrix_data(
#     [comp1, comp2], 'NRTL', "Non-randomness parameters of the NRTL equation")

# NOTE
nrtl_alpha = thermo_db.build_thermo_property(
    [comp1, comp2], 'NRTL', "Non-randomness parameters of the NRTL equation")

# symbol
print(nrtl_alpha.matrix_symbol)

print(nrtl_alpha.matrix_data_structure())

print(nrtl_alpha.get_property('Alpha_i_1', comp1))
# print(nrtl_alpha.get_property(4, comp1))
# by symbol
# pp(float(Alpha_i_j['value']))

print(nrtl_alpha.get_matrix_property("Alpha_i_j",
                                     [comp1, comp2], symbol_format='alphabetic', message="NRTL Alpha value"))

# use ij method
print(nrtl_alpha.ij("Alpha_i_j", [comp1, comp2], symbol_format='alphabetic', message="NRTL Alpha value"))

# # property name
prop_name_lists = ["Alpha", comp1, comp3]
prop_name = "_".join(prop_name_lists)
print(prop_name)
print(nrtl_alpha.get_matrix_property_by_name(prop_name))
print(nrtl_alpha.get_matrix_property_by_name(prop_name).get('value'))

# ====================================
# BUILD MATRIX EQUATION
# ====================================
# ! equation 1
# build equation
# nrtl_tau_eq = thermo_db.build_matrix_equation(
#     [comp1, comp2, comp3], 'NRTL', 'Interaction parameters of the NRTL equation-2')

# NOTE
nrtl_tau_eq = thermo_db.build_thermo_property(
    [comp1, comp2, comp3], 'NRTL', 'Interaction parameters of the NRTL equation-2')

# load parms
print(nrtl_tau_eq.parms)
print(nrtl_tau_eq.parms_values)
print(nrtl_tau_eq.args)
print(nrtl_tau_eq.arg_symbols)
print(nrtl_tau_eq.returns)
print(nrtl_tau_eq.return_symbols)
print(nrtl_tau_eq.summary)
# equation details
print(nrtl_tau_eq.equation_parms())
print(nrtl_tau_eq.equation_args())
print(nrtl_tau_eq.equation_body())
print(nrtl_tau_eq.equation_return())

# cal
tau_cal = nrtl_tau_eq.cal(T=298.15)
tau_cal = nrtl_tau_eq.cal(message="NRTL Tau value", T=298.15)
print(tau_cal)


# ====================================
# CHECK COMPONENT AVAILABILITY IN A TABLE
# ====================================
# check component availability in the databook and table
comp4 = "Carbon Dioxide"
# CO2_check_availability = tdb.check_component(comp1, 1, 2)

# check component
CO2_check_availability = thermo_db.check_component(comp4,
                                                   "Perry's Chemical Engineers' Handbook",
                                                   "TABLE 2-153 Heat Capacities of Inorganic and Organic Liquids")
print(CO2_check_availability)

# ====================================
# BUILD DATA
# ====================================
# build data
CO2_data = thermo_db.build_data(comp4, 1, 2)
print(CO2_data.data_structure())
print(CO2_data.get_property(5))


# ====================================
# BUILD THERMODB
# ====================================
# thermodb name
thermodb_name = "thermodb_nrtl_1"

# build a thermodb
thermo_db = ptdb.build_thermodb()
pp(type(thermo_db))

# NOTE: add TableMatrixData
thermo_db.add_data('nrtl_alpha', nrtl_alpha)
# NOTE: add TableMatrixEquation
thermo_db.add_data('nrtl_tau', nrtl_tau_eq)
# NOTE: add TableData
thermo_db.add_data('CO2_general_data', CO2_data)

# file name
thermodb_file_path = os.path.join(os.getcwd(), 'tests')
# save
thermo_db.save(
    f'{thermodb_name}', file_path=thermodb_file_path)

# ====================================
# CHECK THERMODB
# ====================================
# check all properties and functions registered
pp(thermo_db.check_properties())
pp(thermo_db.check_functions())
