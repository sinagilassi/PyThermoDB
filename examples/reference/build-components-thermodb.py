# import packages/modules
from typing import Dict, List, Any
import os
from rich import print
import pyThermoDB as ptdb
from pyThermoDB.core import TableData, TableEquation, TableMatrixData
from pyThermoDB.references import ReferenceConfig
from pyThermoDB import check_and_build_component_thermodb
from pythermodb_settings.models import Component

# versions
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
# ====================================
# parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))

# files
# SECTION:
yml_file = 'str-ref-1.yml'
yml_path = os.path.join(parent_dir, yml_file)

# SECTION:
md_file = 'str-ref-1.md'
md_path = os.path.join(parent_dir, md_file)

# SECTION: file contents
file_contents = """

"""

# NOTE: custom ref
# ref: Dict[str, Any] = {'reference': [file_contents]}
# md ref
# ref = {'reference': [md_path]}
# yml ref
ref: Dict[str, Any] = {'reference': [yml_path]}

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
tb_list = thermo_db.list_tables('CUSTOM-REF-1')
print(tb_list)

# ====================================
# BUILD COMPONENTS THERMODB
# ====================================
# property
reference_config = {
    'nrtl': {
        'databook': 'CUSTOM-REF-1',
        'table': "NRTL Non-randomness parameters-2",
        'symbols': {
            'alpha': 'alpha',
            'a_i_j': 'a_i_j',
            'b_i_j': 'b_i_j',
            'c_i_j': 'c_i_j',
        }
    }
}

# NOTE: build components thermodb
thermodb_components_ = ptdb.build_components_thermodb(
    component_names=['ethanol', 'methanol'],
    reference_config=reference_config,
    custom_reference=ref)
# check
print(thermodb_components_.check())
print(thermodb_components_.message)

# ====================================
# BUILD MATRIX DATA
# ====================================
# components
comp1 = "methanol"
comp2 = "ethanol"

components = [comp1, comp2]

# NOTE: build a matrix data
nrtl_alpha = thermodb_components_.select('nrtl')
# check
if not isinstance(nrtl_alpha, TableMatrixData):
    raise TypeError("Not TableMatrixData")

# matrix table
print(nrtl_alpha.matrix_table)
# matrix table
res_ = nrtl_alpha.get_matrix_table(mode='selected')
print(res_, type(res_))

# symbol
print(nrtl_alpha.matrix_symbol)

print(nrtl_alpha.matrix_data_structure())

# matrix data
print(nrtl_alpha.get_matrix_property(
    "a_i_j",
    [comp1, comp2],
    symbol_format='alphabetic',
    message="NRTL Alpha value")
)

print(nrtl_alpha.get_matrix_property(
    "b_i_j",
    [comp1, comp2],
    symbol_format='alphabetic',
    message="NRTL Alpha value")
)

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

print("*" * 20)
prop_name = f"b | {comp1} | {comp2}"
# get values
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='alphabetic')
print(prop_matrix, type(prop_matrix))

print("*" * 20)
prop_name = f"c | {comp1} | {comp2}"
# get values
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='alphabetic')
print(prop_matrix, type(prop_matrix))
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='numeric')
print(prop_matrix, type(prop_matrix))
mat_ = nrtl_alpha.mat('c', [comp1, comp2])
print(mat_)
# get values
prop_name = f"c | {comp2} | {comp1}"
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='alphabetic')
print(prop_matrix, type(prop_matrix))
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='numeric')
print(prop_matrix, type(prop_matrix))
# ! ij matrix
mat_ = nrtl_alpha.mat('c', [comp2, comp1])
print(mat_)
print("*" * 20)

prop_name = f"alpha | {comp1} | {comp2}"
# get values
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='alphabetic')
print(prop_matrix, type(prop_matrix))

# ! ij matrix
mat_ = nrtl_alpha.mat('alpha', [comp2, comp1])
print(mat_)
print("*" * 20)

# ====================================
# SAVE THERMODB
# ====================================
# thermodb_file = thermodb_component_.thermodb_name or 'thermodb_component'

# # save (pkl format)
# res_ = thermodb_component_.save(thermodb_file, file_path=parent_dir)
# print(f"ThermoDB saved: {res_}")

# multi-component
thermodb_file = thermodb_components_.thermodb_name or 'thermodb_component'

# save (pkl format)
res_ = thermodb_components_.save(thermodb_file, file_path=parent_dir)
print(f"ThermoDB saved: {res_}")
