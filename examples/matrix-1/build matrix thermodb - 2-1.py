# import packages/modules
import pyThermoDB as ptdb
from pyThermoDB.core import TableMatrixData
from pyThermoDB.utils import create_binary_mixtures
from pythermodb_settings.models import Component
import os
from rich import print
from typing import Dict, Any

# version
print(ptdb.__version__)

# ====================================
# ☑️ CUSTOM REFERENCES
# ====================================
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Parent directory: {parent_dir}")

# NOTE: format 2
# ! Mixture column
# files
yml_file = 'matrix-format-2.yml'
yml_path = os.path.join(parent_dir, yml_file)

# custom ref
ref: Dict[str, Any] = {
    'reference': [yml_path]
}

# ====================================
# ☑️ INITIALIZATION OWN THERMO DB
# ====================================
thermo_db = ptdb.init(custom_reference=ref)

# ====================================
# ☑️ GET DATABOOK LIST
# ====================================
db_list = thermo_db.list_databooks()
print(db_list)

# ====================================
# ☑️ SELECT A DATABOOK
# ====================================
# table list
tb_list = thermo_db.list_tables('NRTL')
print(tb_list)

# ====================================
# ☑️ CHECK COMPONENT AVAILABILITY IN A TABLE
# ====================================
# check component availability in the databook and table
# ! component
methanol = Component(name="methanol", formula="CH3OH", state="l")
ethanol = Component(name="ethanol", formula="C2H5OH", state="l")
methane = Component(name="methane", formula="CH4", state="g")

# ! mixture
mixture_components = [methanol, ethanol, methane]
# >> methanol-ethanol
# >> methanol-methane
# >> ethanol-methane

# ====================================
# ☑️ CHECK MIXTURE AVAILABILITY IN A TABLE
# ====================================
# create mixtures
mixtures = create_binary_mixtures(
    components=mixture_components,
    mixture_key='Name',
    delimiter='|'
)
print(f"Mixtures:")
print(mixtures)

# ! check binary mixtures availability in the databook and table
check_binary_mixtures_availability = thermo_db.check_mixtures_availability(
    components=mixture_components,
    databook='NRTL',
    table='Non-randomness parameters of the NRTL equation-3',
    column_name='Mixture',
    component_key='Name-State',
    mixture_key='Name',
    delimiter='|',
    ignore_component_state=True
)
print("Binary mixtures availability:")
print(check_binary_mixtures_availability)

# ! check specific mixture availability
check_binary_mixtures_availability = thermo_db.check_mixtures_availability(
    components=mixture_components,
    databook='NRTL',
    table='Non-randomness parameters of the NRTL equation-3',
    mixture_names=['methanol | ethanol', 'methanol | methane'],
    column_name='Mixture',
    component_key='Name-State',
    mixture_key='Name',
    delimiter='|',
    ignore_component_state=True
)
print("Specific binary mixtures availability:")
print(check_binary_mixtures_availability)

# mixture
mixture_methanol_ethanol = methanol.name + ' | ' + ethanol.name
print(f"Mixture: {mixture_methanol_ethanol}")

# NOTE: components
# comp1
comp1 = methanol.name
comp2 = ethanol.name
comp3 = methane.name
# components list
components = [comp1, comp2]

# ====================================
# ☑️ GET MIXTURES DATA
# ====================================
# NOTE: get mixtures data
mixtures_data = thermo_db.get_mixtures_data(
    components=mixture_components,
    databook='NRTL',
    table='Non-randomness parameters of the NRTL equation-3',
    mixture_names=["methanol | ethanol", "methanol | methane"],
    column_name='Mixture',
    component_key='Name-State',
    mixture_key='Name',
    delimiter='|',
    ignore_component_state=True,
)
print("Mixtures data:")
print(mixtures_data)

# ====================================
# ☑️ BUILD MATRIX DATA
# ====================================
# NOTE: build a matrix data
nrtl_alpha = thermo_db.build_components_thermo_property(
    components=[methanol, ethanol, methane],
    databook='NRTL',
    table="Non-randomness parameters of the NRTL equation-3",
    ignore_component_state=True,
    mixture_names=["methanol | ethanol", "methanol | methane"],
)
# check type
if not isinstance(nrtl_alpha, TableMatrixData):
    raise TypeError("nrtl_alpha is not an instance of TableMatrixData")

# NOTE: matrix table
print(nrtl_alpha.matrix_table)
# NOTE: matrix table
print(nrtl_alpha.get_matrix_table(mode='selected'))
# NOTE: symbol
print(nrtl_alpha.matrix_symbol)
# NOTE: structure
print(nrtl_alpha.matrix_data_structure())

# SECTION: get property value
# # ! by name
# print(nrtl_alpha.get_property('a_i_1', methanol.name))
# # ! by formula
# print(nrtl_alpha.get_property('a_i_1', methanol.formula))
# #
# print(nrtl_alpha.get_property('a_i_2', methanol.name))
# print(nrtl_alpha.get_property('a_i_2', methanol.name))
# print(nrtl_alpha.get_property('a_i_3', methanol.formula))
# # ! unknown
# print(nrtl_alpha.get_property('b_i_1', comp1))
# print(nrtl_alpha.get_property(4, comp1))
# # by symbol
# # print(float(Alpha_i_j['value']))

# SECTION: get matrix property
# mixture name
mixture_name_methanol_ethanol = f"{comp1} | {comp2}"
print(f"Mixture name: {mixture_name_methanol_ethanol}")

mixture_name_methanol_methane = f"{comp1} | {comp3}"
print(f"Mixture name: {mixture_name_methanol_methane}")

# ! property [i,i]
# >> methanol-ethanol mixture
print(nrtl_alpha.get_matrix_property(
    "a_i_j",
    [comp1, comp1],
    symbol_format='alphabetic',
    message="NRTL Alpha value",
    mixture_name=mixture_name_methanol_ethanol
)
)

print(nrtl_alpha.get_matrix_property(
    "a_i_j",
    [comp1, comp2],
    symbol_format='alphabetic',
    message="NRTL Alpha value",
    mixture_name=mixture_name_methanol_ethanol
)
)

# >> methanol-methane mixture
print(nrtl_alpha.get_matrix_property(
    "a_i_j",
    [comp1, comp1],
    symbol_format='alphabetic',
    message="NRTL Alpha value",
    mixture_name=mixture_name_methanol_methane
)
)

print(nrtl_alpha.get_matrix_property(
    "a_i_j",
    [comp1, comp3],
    symbol_format='alphabetic',
    message="NRTL Alpha value",
    mixture_name=mixture_name_methanol_methane
)
)

# ! property [i,i]
print(nrtl_alpha.get_matrix_property(
    "a_i_j",
    [comp2, comp2],
    symbol_format='alphabetic',
    message="NRTL Alpha value",
    mixture_name=mixture_name_methanol_ethanol
)
)
# ! property [i,j]
print(nrtl_alpha.get_matrix_property(
    "a_i_j",
    [comp1, comp2],
    symbol_format='alphabetic',
    message="NRTL Alpha value"
)
)
# ! property [i,j]
print(nrtl_alpha.get_matrix_property(
    "a_i_j",
    [comp2, comp1],
    symbol_format='alphabetic',
    message="NRTL Alpha value"
)
)


print(nrtl_alpha.get_matrix_property(
    "b_i_j",
    [comp1, comp2],
    symbol_format='alphabetic',
    message="NRTL Alpha value"
)
)

# SECTION: property name using ij method
prop_name = f"a_{comp1}_{comp2}"
print(prop_name)
print(nrtl_alpha.ij(prop_name))
print(nrtl_alpha.ij(prop_name).get('value'))

prop_name = f"a_{comp1}_{comp1}"
print(prop_name)
print(nrtl_alpha.ij(
    property=prop_name,
    mixture_name=mixture_name_methanol_ethanol
)
)
print(nrtl_alpha.ij(
    property=prop_name,
    mixture_name=mixture_name_methanol_ethanol
).get('value')
)

# SECTION: matrix data
# NOTE: binary
res_2 = nrtl_alpha.mat("a", [comp1, comp2])
print(res_2)

# SECTION: metric
print(nrtl_alpha.ijs(f"a | {comp1} | {comp2}"))
print(nrtl_alpha.ijs(f"b | {comp1} | {comp2}"))
print(nrtl_alpha.ijs(f"c | {comp1} | {comp2}"))

# components
# looping through the matrix data
for comp1 in components:
    for comp2 in components:
        # set property name
        prop_name = f"b_{comp1}_{comp2}"
        # get property value
        prop_value = nrtl_alpha.ij(
            property=prop_name,
            mixture_name=mixture_name_methanol_ethanol
        ).get('value')
        # log
        print(f"Property: {prop_name} = {prop_value}")

# ====================================
# ☑️ BUILD THERMODB
# ====================================
# thermodb name
thermodb_name = "thermodb_nrtl_mixture"

# build a thermodb
thermo_db = ptdb.build_thermodb()
print(type(thermo_db))

# NOTE: add TableMatrixData
thermo_db.add_data('nrtl', nrtl_alpha)

# save
thermo_db.save(
    f'{thermodb_name}',
    file_path=parent_dir
)

# ====================================
# ☑️ CHECK THERMODB
# ====================================
# check all properties and functions registered
print(thermo_db.check_properties())
print(thermo_db.check_functions())
