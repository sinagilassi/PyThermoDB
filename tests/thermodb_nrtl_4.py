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
yml_file = 'tests\\NRTL Non-randomness parameters-1.yml'
yml_path = os.path.join(os.getcwd(), yml_file)
# csv files (data/equation tables)
csv_file_1 = 'tests\\NRTL Non-randomness parameters-1.csv'
csv_path_1 = os.path.join(os.getcwd(), csv_file_1)

# custom ref
ref = {
    'reference': [yml_path],
    'tables': [csv_path_1]
}

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
tb_list = thermo_db.list_tables('NRTL-EtOH-MTBE')
print(tb_list)

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
comp1 = "ethanol"
# COMP1_check_availability = thermo_db.check_component(
#     comp1, 'NRTL', "Non-randomness parameters of the NRTL equation")

comp2 = "butyl-methyl-ether"
# COMP1_check_availability = thermo_db.check_component(
#     comp2, 'NRTL', "Non-randomness parameters of the NRTL equation")

# query
# query = f"Name.str.lower() == '{comp1.lower()}' & State == 'g'"
# COMP1_check_availability = thermo_db.check_component(
#     comp1, 3, 2, query, query=True)

components = [comp1, comp2]

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
# NOTE: build a matrix data
nrtl_alpha = thermo_db.build_thermo_property(
    [comp1, comp2], 'NRTL-EtOH-MTBE', "NRTL Non-randomness parameters-1")

# matrix table
print(nrtl_alpha.matrix_table)
# matrix table
res_ = nrtl_alpha.get_matrix_table(mode='selected')
print(res_, type(res_))

# symbol
print(nrtl_alpha.matrix_symbol)

print(nrtl_alpha.matrix_data_structure())

print(nrtl_alpha.get_property('alpha_i_1', comp1))


print(nrtl_alpha.get_matrix_property("alpha_i_j",
                                     [comp1, comp2], symbol_format='alphabetic', message="NRTL Alpha value"))

print(nrtl_alpha.get_matrix_property("dg_i_j",
                                     [comp1, comp2], symbol_format='alphabetic', message="NRTL Alpha value"))

# property name using ij method
prop_name = f"alpha_{comp1}_{comp2}"
print(prop_name)
res_1 = nrtl_alpha.ij(prop_name)
print(res_1)
print(res_1.get('value'))

# components
# looping through the matrix data
# for comp1 in components:
#     for comp2 in components:
#         prop_name = f"dg_{comp1}_{comp2}"
#         # get property value
#         prop_value = nrtl_alpha.ij(prop_name).get('value')
#         # log
#         print(f"Property: {prop_name} = {prop_value}")
        
# get property value using the matrix data
# format 1
# prop_name = f"dg_{comp1}_{comp2}"
# format 2
prop_name = f"dg | {comp1} | {comp2}"
# get values
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='array')
print(prop_matrix, type(prop_matrix))

prop_name = f"alpha | {comp1} | {comp2}"
# get values
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='array')
print(prop_matrix, type(prop_matrix))
# ====================================
# BUILD MATRIX EQUATION
# ====================================
# NOTE: build equation
nrtl_tau_eq = thermo_db.build_thermo_property(
    components, 'NRTL', 'Interaction parameters of the NRTL equation-2')

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
# elements
print(nrtl_tau_eq.matrix_elements)

# cal
tau_cal = nrtl_tau_eq.cal(T=298.15)
tau_cal = nrtl_tau_eq.cal(message="NRTL Tau value", output_format='numeric', T=298.15)
print(tau_cal)
tau_cal = nrtl_tau_eq.cal(message="NRTL Tau value", output_format='alphabetic', T=298.15)
print(tau_cal)

tau_cal = nrtl_tau_eq.cal(message="NRTL Tau value", filter_elements=['methanol', 'ethanol'], output_format='numeric', T=298.15)
print(tau_cal)
tau_cal = nrtl_tau_eq.cal(message="NRTL Tau value", filter_elements=['methanol', 'ethanol'], output_format='alphabetic', T=298.15)
print(tau_cal)
tau_cal = nrtl_tau_eq.cal(message="NRTL Tau value", filter_elements=['ethanol', 'methanol'], output_format='numeric', T=298.15)
print(tau_cal)
tau_cal = nrtl_tau_eq.cal(message="NRTL Tau value", filter_elements=['ethanol', 'methanol'], output_format='alphabetic', T=298.15)
print(tau_cal)

# ====================================
# BUILD THERMODB
# ====================================
# thermodb name
thermodb_name = "thermodb_nrtl_3"

# build a thermodb
thermo_db = ptdb.build_thermodb()
pp(type(thermo_db))

# NOTE: add TableMatrixData
thermo_db.add_data('nrtl_alpha', nrtl_alpha)
# NOTE: add TableMatrixEquation
thermo_db.add_data('nrtl_tau', nrtl_tau_eq)

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
