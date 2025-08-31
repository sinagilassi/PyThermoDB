# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp
import os
from rich import print
from typing import Dict, Any, List

# version
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
# ====================================
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Parent directory: {parent_dir}")

# files
yml_file = 'nrtl-3.yml'
yml_path = os.path.join(parent_dir, yml_file)
# csv files (data/equation tables)
# ! new format
csv_file_1 = 'Non-randomness parameters of the NRTL equation-2-1.csv'
csv_file_2 = 'Interaction parameters of the NRTL equation-2.csv'
csv_path_1 = os.path.join(parent_dir, csv_file_1)
csv_path_2 = os.path.join(parent_dir, csv_file_2)

# custom ref
ref: Dict[str, Any] = {
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
db_list = thermo_db.list_databooks()
print(db_list)

# ====================================
# SELECT A DATABOOK
# ====================================
# table list
tb_list = thermo_db.list_tables('NRTL')
print(tb_list)

# # select a table
tb = thermo_db.select_table(
    'NRTL',
    'Non-randomness parameters of the NRTL equation-2-1'
)
print(tb)

# ====================================
# DISPLAY TABLE INFO
# ====================================
# display a table
tb_info = thermo_db.table_info(
    'NRTL',
    "Non-randomness parameters of the NRTL equation-2-1"
)
print(tb_info)

# ====================================
# LOAD TABLE
# ====================================
# load equation
# tb_eq = thermo_db.equation_load(3, 1)
# equation structure
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

components = [comp1, comp2, comp3]

# ====================================
# LOAD MATRIX DATA
# ====================================
tb_data_df = thermo_db.table_data(
    'NRTL', 1)
print(type(tb_data_df))
pp(tb_data_df)


# ====================================
# BUILD MATRIX DATA
# ====================================
# NOTE: build a matrix data
nrtl_alpha = thermo_db.build_thermo_property(
    [comp1, comp2], 'NRTL', "Non-randomness parameters of the NRTL equation-2-1")

# matrix table
print(nrtl_alpha.matrix_table)
# matrix table
print(nrtl_alpha.get_matrix_table(mode='selected'))
# symbol
print(nrtl_alpha.matrix_symbol)

print(nrtl_alpha.matrix_data_structure())

print(nrtl_alpha.get_property('Alpha_i_1', comp1))
# print(nrtl_alpha.get_property(4, comp1))
# by symbol
# pp(float(Alpha_i_j['value']))

print(nrtl_alpha.get_matrix_property("Alpha_i_j",
                                     [comp1, comp2], symbol_format='alphabetic', message="NRTL Alpha value"))

print(nrtl_alpha.get_matrix_property("Beta_i_j",
                                     [comp1, comp2], symbol_format='alphabetic', message="NRTL Alpha value"))

# property name using ij method
prop_name = f"Alpha_{comp1}_{comp3}"
print(prop_name)
print(nrtl_alpha.ij(prop_name))
print(nrtl_alpha.ij(prop_name).get('value'))


# matrix data
res_1 = nrtl_alpha.mat("Alpha", [comp2, comp1, comp3])
print(res_1)

# metric
print(nrtl_alpha.ijs(f"Alpha | {comp1} | {comp2}"))

# components
# looping through the matrix data
for comp1 in components:
    for comp2 in components:
        prop_name = f"Delta_{comp1}_{comp2}"
        # get property value
        prop_value = nrtl_alpha.ij(prop_name).get('value')
        # log
        print(f"Property: {prop_name} = {prop_value}")


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
tau_cal = nrtl_tau_eq.cal(message="NRTL Tau value",
                          output_format='numeric', T=298.15)
print(tau_cal)
tau_cal = nrtl_tau_eq.cal(message="NRTL Tau value",
                          output_format='alphabetic', T=298.15)
print(tau_cal)

tau_cal = nrtl_tau_eq.cal(message="NRTL Tau value", filter_elements=[
                          'methanol', 'ethanol'], output_format='numeric', T=298.15)
print(tau_cal)
tau_cal = nrtl_tau_eq.cal(message="NRTL Tau value", filter_elements=[
                          'methanol', 'ethanol'], output_format='alphabetic', T=298.15)
print(tau_cal)
tau_cal = nrtl_tau_eq.cal(message="NRTL Tau value", filter_elements=[
                          'ethanol', 'methanol'], output_format='numeric', T=298.15)
print(tau_cal)
tau_cal = nrtl_tau_eq.cal(message="NRTL Tau value", filter_elements=[
                          'ethanol', 'methanol'], output_format='alphabetic', T=298.15)
print(tau_cal)

# ====================================
# BUILD THERMODB
# ====================================
# thermodb name
thermodb_name = "thermodb_nrtl_2"

# build a thermodb
thermo_db = ptdb.build_thermodb()
pp(type(thermo_db))

# NOTE: add TableMatrixData
thermo_db.add_data('nrtl_alpha', nrtl_alpha)
# NOTE: add TableMatrixEquation
thermo_db.add_data('nrtl_tau', nrtl_tau_eq)

# save
thermo_db.save(
    f'{thermodb_name}', file_path=parent_dir)

# ====================================
# CHECK THERMODB
# ====================================
# check all properties and functions registered
pp(thermo_db.check_properties())
pp(thermo_db.check_functions())
