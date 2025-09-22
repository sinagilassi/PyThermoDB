# import packages/modules
import pyThermoDB as ptdb
from pyThermoDB.core import TableMatrixData
from pythermodb_settings.models import Component
import os
from rich import print
from typing import Dict, Any

# version
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
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

# ====================================
# CHECK COMPONENT AVAILABILITY IN A TABLE
# ====================================
# check component availability in the databook and table
# ! component
methanol = Component(name="methanol", formula="CH3OH", state="l")
ethanol = Component(name="ethanol", formula="C2H5OH", state="l")
benzene = Component(name="benzene", formula="C6H6", state="l")

# mixture
mixture_methanol_ethanol = methanol.name + ' | ' + ethanol.name
print(f"Mixture: {mixture_methanol_ethanol}")

# NOTE: binary mixture
# ! direct check
mixture_check_availability = thermo_db.is_binary_mixture_available(
    components=[methanol, ethanol],
    databook='NRTL',
    table="Non-randomness parameters of the NRTL equation-3"
)
print(f"Mixture availability: {mixture_check_availability}")

# ! ignore component state
mixture_check_availability = thermo_db.is_binary_mixture_available(
    components=[methanol, ethanol],
    databook='NRTL',
    table="Non-randomness parameters of the NRTL equation-3",
    ignore_component_state=True
)
print(f"Mixture availability (ignore state): {mixture_check_availability}")

# NOTE: using query
query = f"Name.str.lower() == '{methanol.name.lower()}'"
# ! using query
COMP1_check_availability = thermo_db.check_component(
    component_name=methanol.name,
    databook='NRTL',
    table='Non-randomness parameters of the NRTL equation-3',
    column_name=query,
    query=True,
    res_format='dict'
)
print(f"Component availability (with query): {COMP1_check_availability}")

# ! using query - mixture
query1 = f"Name.str.lower() == '{methanol.name.lower()}' and State.str.lower() == '{methanol.state.lower()}' and Mixture.str.lower() == '{mixture_methanol_ethanol.lower()}'"
# >> check
mixture_check_availability = thermo_db.check_component(
    component_name=methanol.name,
    databook='NRTL',
    table='Non-randomness parameters of the NRTL equation-3',
    column_name=query1,
    query=True,
    res_format='dict'
)
print(f"Mixture availability (with query): {mixture_check_availability}")

# NOTE: components
# comp1
comp1 = methanol.name
comp2 = ethanol.name
comp3 = benzene.name
# components list
components = [comp1, comp2, comp3]

# ====================================
# ! BUILD MATRIX DATA
# ====================================
# NOTE: build a matrix data
nrtl_alpha = thermo_db.build_components_thermo_property(
    [methanol, ethanol],
    'NRTL',
    "Non-randomness parameters of the NRTL equation-3"
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
# ! by name
print(nrtl_alpha.get_property('Alpha_i_1', methanol.name))
# ! by formula
print(nrtl_alpha.get_property('Alpha_i_1', methanol.formula))
#
print(nrtl_alpha.get_property('Alpha_i_2', methanol.name))
print(nrtl_alpha.get_property('Alpha_i_3', methanol.name))
print(nrtl_alpha.get_property('Alpha_i_3', methanol.formula))
# ! unknown
print(nrtl_alpha.get_property('Alpha_i_4', comp1))
print(nrtl_alpha.get_property(4, comp1))
# by symbol
# print(float(Alpha_i_j['value']))

# SECTION: get matrix property
print(nrtl_alpha.get_matrix_property(
    "Alpha_i_j",
    [comp1, comp2],
    symbol_format='alphabetic',
    message="NRTL Alpha value"
)
)

print(nrtl_alpha.get_matrix_property(
    "Beta_i_j",
    [comp1, comp2],
    symbol_format='alphabetic',
    message="NRTL Alpha value"
)
)

# SECTION: property name using ij method
prop_name = f"Alpha_{comp1}_{comp3}"
print(prop_name)
print(nrtl_alpha.ij(prop_name))
print(nrtl_alpha.ij(prop_name).get('value'))


# SECTION: matrix data
# NOTE: multi-component
res_1 = nrtl_alpha.mat("Alpha", [comp2, comp1, comp3])
print(res_1)

# NOTE: binary
res_2 = nrtl_alpha.mat("Alpha", [comp1, comp2])
print(res_2)

# SECTION: metric
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
# ! BUILD THERMODB
# ====================================
# thermodb name
thermodb_name = "thermodb_nrtl"

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
# ! CHECK THERMODB
# ====================================
# check all properties and functions registered
print(thermo_db.check_properties())
print(thermo_db.check_functions())
