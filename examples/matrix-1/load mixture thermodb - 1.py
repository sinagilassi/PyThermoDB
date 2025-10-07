# import packages/modules
import os
import pyThermoDB as ptdb
from pyThermoDB.core import TableMatrixData
from pythermodb_settings.models import Component
from rich import print

# version
print(ptdb.__version__)

# ====================================
# ☑️ CUSTOM REFERENCES
# ====================================
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Parent directory: {parent_dir}")

# ref
thermodb_file = 'thermodb_nrtl_mixture_inline.pkl'
thermodb_path = os.path.join(parent_dir, thermodb_file)
print(thermodb_path)

# ====================================
# ☑️ LOAD THERMODB
# ====================================
# load thermodb
nrtl_thermodb = ptdb.load_thermodb(thermodb_path)
print(type(nrtl_thermodb))

# ====================================
# ☑️ CHECK THERMODB
# ====================================
# check all properties and functions registered
print(nrtl_thermodb.check())

# ====================================
# ☑️ COMPONENTS AND MIXTURE
# ====================================
# check component availability in the databook and table
# ! component
methanol = Component(name="methanol", formula="CH3OH", state="l")
ethanol = Component(name="ethanol", formula="C2H5OH", state="l")

# ! mixture
mixture_methanol_ethanol = methanol.name + ' | ' + ethanol.name
print(f"Mixture: {mixture_methanol_ethanol}")

# comp1
comp1 = methanol.name
comp2 = ethanol.name
# ! components list
components = [comp1, comp2]

# ====================================
# ☑️ LOAD MATRIX DATA
# ====================================
# ! mixture thermodb (binary mixture)
# NOTE: build a matrix data
nrtl_alpha = nrtl_thermodb.check_property('nrtl')
# check type
if not isinstance(nrtl_alpha, TableMatrixData):
    raise TypeError("nrtl_alpha is not an instance of TableMatrixData")

# ====================================
# ☑️ CHECK MATRIX DATA
# ====================================
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
