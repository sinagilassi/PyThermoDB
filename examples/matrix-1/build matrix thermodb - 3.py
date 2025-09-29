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
# ☑️ CUSTOM REFERENCES
# ====================================
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Parent directory: {parent_dir}")

# NOTE: format 2
# ! Mixture column
# files
yml_file = 'matrix-format-2.yml'
yml_path = os.path.join(parent_dir, yml_file)

REFERENCES = """
REFERENCES:
    NRTL:
      DATABOOK-ID: 1
      TABLES:
        Non-randomness parameters of the NRTL equation-3:
          TABLE-ID: 1
          DESCRIPTION:
            This table provides the NRTL non-randomness parameters for the NRTL equation.
          MATRIX-SYMBOL:
            - a-constant: a
            - b
            - c
            - alpha
          STRUCTURE:
            COLUMNS: [No.,Mixture,Name,Formula,State,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
            SYMBOL: [None,None,None,None,None,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
            UNIT: [None,None,None,None,None,1,1,1,1,1,1,1,1]
          VALUES:
            - [1,methanol|ethanol,methanol,CH3OH,l,0,1,1,1.564200272,0,35.05450323,0,4.481683583]
            - [2,methanol|ethanol,ethanol,C2H5OH,g,2,3,-20.63243601,0,0.059982839,0,4.481683583,0]
            - [1,methanol|methane,methanol,CH3OH,l,1,0.300492719,0,1.564200272,0,35.05450323,0,4.481683583]
            - [2,methanol|methane,methane,CH4,g,0.380229054,0,-20.63243601,0,0.059982839,0,4.481683583,0]
"""

# custom ref
custom_reference: Dict[str, Any] = {
    'reference': [REFERENCES]
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
tb_list = thermo_db.list_tables('NRTL')
print(tb_list)

# ====================================
# ☑️ CHECK COMPONENT AVAILABILITY IN A TABLE
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
# components list
components = [comp1, comp2]

# ====================================
# ☑️ GET MIXTURE DATA
# ====================================
# NOTE: get mixture data
mixture_data = thermo_db.get_binary_mixture_data(
    components=[methanol, ethanol],
    databook='NRTL',
    table='Non-randomness parameters of the NRTL equation-3',
    component_key='Name-State',
    ignore_component_state=True,
)
print(f"Mixture data: {mixture_data}")

# ====================================
# ☑️ BUILD MATRIX DATA
# ====================================
# NOTE: build a matrix data
nrtl_alpha = thermo_db.build_components_thermo_property(
    [methanol, ethanol],
    'NRTL',
    "Non-randomness parameters of the NRTL equation-3",
    ignore_component_state=True,
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
print(nrtl_alpha.get_property('a_i_1', methanol.name))
# ! by formula
print(nrtl_alpha.get_property('a_i_1', methanol.formula))
#
print(nrtl_alpha.get_property('a_i_2', methanol.name))
print(nrtl_alpha.get_property('a_i_2', methanol.name))
print(nrtl_alpha.get_property('a_i_3', methanol.formula))
# ! unknown
print(nrtl_alpha.get_property('b_i_1', comp1))
print(nrtl_alpha.get_property(4, comp1))
# by symbol
# print(float(Alpha_i_j['value']))

# SECTION: get matrix property
# mixture name
mixture_name = f"{comp1} | {comp2}"
print(f"Mixture name: {mixture_name}")

# ! property [i,i]
print(nrtl_alpha.get_matrix_property(
    "a_i_j",
    [comp1, comp1],
    symbol_format='alphabetic',
    message="NRTL Alpha value",
    mixture_name=mixture_name
)
)
# ! property [i,i]
print(nrtl_alpha.get_matrix_property(
    "a_i_j",
    [comp2, comp2],
    symbol_format='alphabetic',
    message="NRTL Alpha value",
    mixture_name=mixture_name
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
    mixture_name=mixture_name
)
)
print(nrtl_alpha.ij(
    property=prop_name,
    mixture_name=mixture_name
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
            mixture_name=mixture_name
        ).get('value')
        # log
        print(f"Property: {prop_name} = {prop_value}")


# ====================================
# ☑️ BUILD THERMODB
# ====================================
# thermodb name
thermodb_name = "thermodb_nrtl_mixture_inline"

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
