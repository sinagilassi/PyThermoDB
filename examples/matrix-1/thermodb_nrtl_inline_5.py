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
# parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Parent directory: {parent_dir}")

# files
yml_file = 'NRTL Non-randomness parameters-inline-2-1.yml'
yml_path = os.path.join(parent_dir, yml_file)

# custom ref
ref = {
    'reference': [yml_path],
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
tb_list = thermo_db.list_tables('NRTL-PARAMETERS')
print(tb_list)

# # select a table
tb = thermo_db.select_table(
    'NRTL-PARAMETERS', 'NRTL Non-randomness parameters-2')
print(tb)

# ====================================
# DISPLAY TABLE INFO
# ====================================
# display a table
tb_info = thermo_db.table_info(
    'NRTL-PARAMETERS', "NRTL Non-randomness parameters-2")
print(tb_info)

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

components = [comp1, comp2]

# ====================================
# BUILD MATRIX DATA
# ====================================
# NOTE: build a matrix data
nrtl_alpha = thermo_db.build_thermo_property(
    [comp1, comp2], 'NRTL-PARAMETERS', "NRTL Non-randomness parameters-2")

# matrix table
print(nrtl_alpha.matrix_table)
# matrix table
res_ = nrtl_alpha.get_matrix_table(mode='selected')
print(res_, type(res_))

# symbol
print(nrtl_alpha.matrix_symbol)

print(nrtl_alpha.matrix_data_structure())

# matrix data
print(nrtl_alpha.get_matrix_property("a_i_j",
                                     [comp1, comp2], symbol_format='alphabetic', message="NRTL Alpha value"))

print(nrtl_alpha.get_matrix_property("b_i_j",
                                     [comp1, comp2], symbol_format='alphabetic', message="NRTL Alpha value"))

# property name using ij method
prop_name = f"a_{comp1}_{comp2}"
print(prop_name)
res_1 = nrtl_alpha.ij(prop_name)
print(res_1)
print(res_1.get('value'))

# get property value using the matrix data
# format 1
# prop_name = f"dg_{comp1}_{comp2}"
# format 2
prop_name = f"a | {comp1} | {comp2}"
# get values
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='alphabetic')
print(prop_matrix, type(prop_matrix))

prop_name = f"b | {comp1} | {comp2}"
# get values
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='alphabetic')
print(prop_matrix, type(prop_matrix))

prop_name = f"c | {comp1} | {comp2}"
# get values
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='alphabetic')
print(prop_matrix, type(prop_matrix))

prop_name = f"alpha | {comp1} | {comp2}"
# get values
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='alphabetic')
print(prop_matrix, type(prop_matrix))

# ====================================
# BUILD THERMODB
# ====================================
# thermodb name
thermodb_name = f"thermodb_nrtl_{comp1}_{comp2}_2_inline"

# build a thermodb
thermo_db = ptdb.build_thermodb()
pp(type(thermo_db))

# NOTE: add TableMatrixData
thermo_db.add_data('non-randomness-parameters', nrtl_alpha)

# save
thermo_db.save(
    f'{thermodb_name}', file_path=parent_dir)

# ====================================
# CHECK THERMODB
# ====================================
# check all properties and functions registered
pp(thermo_db.check_properties())
pp(thermo_db.check_functions())
