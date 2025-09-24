# import packages/modules
import os
import pyThermoDB as ptdb
from pyThermoDB.core import TableData, TableMatrixData
from pythermodb_settings.models import Component

from rich import print

# version
print(ptdb.__version__)

# ====================================
# ☑️ CUSTOM REFERENCES
# ====================================
# parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Parent directory: {parent_dir}")

# files
# yml_file = 'NRTL Non-randomness parameters-inline-2-1.yml'
# ! new format (values)
yml_file = 'NRTL Non-randomness parameters-inline-2-2.yml'
# ! new format (values)
yml_file = 'NRTL Non-randomness parameters-inline-2-3.yml'
yml_path = os.path.join(parent_dir, yml_file)

# NOTE: md file
md_file = 'NRTL Non-randomness parameters-inline-2-1.md'
md_file = 'NRTL Non-randomness parameters-inline-2-2.md'
# md_file = 'NRTL Non-randomness parameters-inline-2-3.md'
md_path = os.path.join(parent_dir, md_file)

# custom ref
custom_reference = {
    'reference': [yml_path],
}

# ====================================
# ☑️ INITIALIZATION OWN THERMO DB
# ====================================
thermo_db = ptdb.init(custom_reference=custom_reference)

# ====================================
# ☑️ GET DATABOOK LIST
# ====================================
db_list = thermo_db.list_databooks()
print(db_list)

# ====================================
# ☑️ SELECT A DATABOOK
# ====================================
# table list
tb_list = thermo_db.list_tables('NRTL-PARAMETERS')
print(tb_list)

# # select a table
tb = thermo_db.select_table(
    'NRTL-PARAMETERS',
    'NRTL Non-randomness parameters-2'
)
print(tb)

# ====================================
# ☑️ DISPLAY TABLE INFO
# ====================================
# display a table
tb_info = thermo_db.table_info(
    'NRTL-PARAMETERS',
    "NRTL Non-randomness parameters-2"
)
print(tb_info)

# ====================================
# ☑️ CHECK COMPONENT AVAILABILITY IN A TABLE
# ====================================
# check component availability in the databook and table
comp1 = "methanol"
comp2 = "ethanol"

components = [comp1, comp2]

# component 1
methanol_Comp = Component(
    name='Methanol',
    formula='CH3OH',
    state='l'
)

# component 2
ethanol_Comp = Component(
    name='Ethanol',
    formula='C2H5OH',
    state='l'
)

# SECTION: check availability of the binary mixture
# NOTE: state is considered
availability = thermo_db.is_binary_mixture_available(
    components=[methanol_Comp, ethanol_Comp],
    databook='NRTL-PARAMETERS',
    table='NRTL Non-randomness parameters-2',
    component_key='Name-State',
    ignore_component_state=False,
)
print("Availability (with state):")
print(availability)

# NOTE: ignore state
availability = thermo_db.is_binary_mixture_available(
    components=[methanol_Comp, ethanol_Comp],
    databook='NRTL-PARAMETERS',
    table='NRTL Non-randomness parameters-2',
    component_key='Name-State',
    ignore_component_state=True,
)
print("Availability (ignore state):")
print(availability)

# ====================================
# ☑️ GET MIXTURE DATA
# ====================================
# NOTE: get mixture data
mixture_data = thermo_db.get_binary_mixture_data(
    components=[methanol_Comp, ethanol_Comp],
    databook='NRTL-PARAMETERS',
    table='NRTL Non-randomness parameters-2',
    component_key='Name-State',
    delimiter='|',
    ignore_component_state=True,
)
print(f"Mixture data: {mixture_data}")

# ====================================
# ☑️ BUILD MATRIX DATA
# ====================================
# NOTE: build a matrix data
nrtl_alpha = thermo_db.build_thermo_property(
    [comp1, comp2],
    'NRTL-PARAMETERS',
    "NRTL Non-randomness parameters-2"
)
# check
if not isinstance(nrtl_alpha, TableMatrixData):
    raise TypeError("Not a TableMatrixData object")

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
# ☑️ BUILD THERMODB
# ====================================
# thermodb name
thermodb_name = f"thermodb_nrtl_{comp1}_{comp2}_md_2_inline"

# build a thermodb
thermo_db = ptdb.build_thermodb()
print(type(thermo_db))

# NOTE: add TableMatrixData
thermo_db.add_data('non-randomness-parameters', nrtl_alpha)

# save
thermo_db.save(
    f'{thermodb_name}', file_path=parent_dir)

# ====================================
# ☑️ CHECK THERMODB
# ====================================
# check all properties and functions registered
print(thermo_db.check_properties())
print(thermo_db.check_functions())
