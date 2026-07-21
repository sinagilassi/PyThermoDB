# import libs
import numpy as np
from pyThermoDB import (
    MixtureThermoDB,
    TableMatrixData,
    build_mixture_thermodb_from_reference,
)
from pythermodb_settings.models import Component
from rich import print

# SECTION: reference content
# NOTE:
# A ternary mixture is encoded as binary pair rows. For three components,
# the unfiltered multi-component build expects all three binary pairs:
# methanol|ethanol, methanol|butyl-methyl-ether, and
# ethanol|butyl-methyl-ether. Each pair has two rows.
REFERENCE_CONTENT = """
REFERENCES:
    CUSTOM-REF-TERNARY:
      DATABOOK-ID: 1
      TABLES:
        NRTL Non-randomness parameters-ternary:
          TABLE-ID: 1
          DESCRIPTION:
            This table provides NRTL matrix parameters for a ternary mixture through binary pair rows.
          MATRIX-SYMBOL:
            - a constant: a
            - b constant: b
            - c constant: c
            - non-randomness parameter: alpha
          STRUCTURE:
            COLUMNS: [No.,Mixture,Name,Formula,State,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
            SYMBOL: [None,None,None,None,None,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
            UNIT: [None,None,None,None,None,1,1,1,1,1,1,1,1]
          VALUES:
            - [1,methanol|ethanol,methanol,CH3OH,l,0,0.300492719,0,1.564200272,0,35.05450323,0,4.481683583]
            - [2,methanol|ethanol,ethanol,C2H5OH,l,0.380229054,0,-20.63243601,0,0.059982839,0,4.481683583,0]
            - [1,methanol|butyl-methyl-ether,methanol,CH3OH,l,0,0.1201,0,2.25,0,18.4,0,0.680715]
            - [2,methanol|butyl-methyl-ether,butyl-methyl-ether,C5H12O,l,0.2152,0,-8.75,0,0.041,0,0.680715,0]
            - [1,ethanol|butyl-methyl-ether,ethanol,C2H5OH,l,0,0.1803,0,3.268,0,22.6,0,0.680715]
            - [2,ethanol|butyl-methyl-ether,butyl-methyl-ether,C5H12O,l,0.2457,0,-12.48,0,0.052,0,0.680715,0]
"""

# SECTION: components
methanol = Component(
    name='methanol',
    formula='CH3OH',
    state='l'
)

ethanol = Component(
    name='ethanol',
    formula='C2H5OH',
    state='l'
)

butyl_methyl_ether = Component(
    name='butyl-methyl-ether',
    formula='C5H12O',
    state='l'
)

# ! multi-component mixture
multi_component_mixture = [methanol, ethanol, butyl_methyl_ether]

# SECTION: build all binary pairs in the ternary mixture
thermodb_ternary: MixtureThermoDB | None = build_mixture_thermodb_from_reference(
    components=multi_component_mixture,
    reference_content=REFERENCE_CONTENT,
    component_key='Name-State',
    mixture_key='Name',
)
print(f"thermodb_ternary: {type(thermodb_ternary)}")

if thermodb_ternary is not None:
    print(f"thermodb_ternary checks: {thermodb_ternary.thermodb.check()}")

# NOTE: extract matrix parameters for the ternary mixture
if thermodb_ternary is None:
    raise ValueError("thermodb_ternary is None. Cannot extract matrix parameters.")\

# ! thermodb
thermodb_ = thermodb_ternary.thermodb
print(f"thermodb_: {type(thermodb_)}")

# checks
print(f"thermodb_ checks: {thermodb_.check()}")

# NOTE: matrix table methods
matrix_properties = thermodb_.check_properties()
matrix_key = next(iter(matrix_properties))
matrix_table = thermodb_.check_property(matrix_key)

if not isinstance(matrix_table, TableMatrixData):
    raise TypeError(
        f"Expected TableMatrixData for {matrix_key}, got {type(matrix_table)}"
    )

print(f"matrix_key: {matrix_key}")

# SECTION: matrix table info
print("matrix symbols:")
print(matrix_table.matrix_symbol)

print("matrix elements:")
print(matrix_table.matrix_elements)

print("matrix data structure:")
print(matrix_table.matrix_data_structure())

print("matrix table - all:")
print(matrix_table.get_matrix_table(mode='all'))

print("matrix table - selected:")
print(matrix_table.get_matrix_table(mode='selected'))

# SECTION: access one i,j matrix value
print("alpha methanol -> ethanol:")
print(matrix_table.ij("alpha | methanol | ethanol"))

print("a ethanol -> butyl-methyl-ether:")
print(matrix_table.ij("a | ethanol | butyl-methyl-ether"))

# NOTE: lower-level equivalent of ij()
print("b methanol -> butyl-methyl-ether:")
print(matrix_table.get_matrix_property(
    "b_i_j",
    ["methanol", "butyl-methyl-ether"],
))

# SECTION: access via thermodb retrieve()
print("alpha methanol -> ethanol using thermodb.retrieve:")
print(thermodb_.retrieve(
    f"{matrix_key} | alpha_i_j | methanol | ethanol",
    message="NRTL alpha value for methanol-ethanol",
))

# SECTION: access binary-pair matrices with mat()
# NOTE:
# This ternary reference is encoded as binary pair rows, so use mat() for each
# binary pair instead of one 3x3 matrix call.
binary_pairs = [
    ["methanol", "ethanol"],
    ["methanol", "butyl-methyl-ether"],
    ["ethanol", "butyl-methyl-ether"],
]

for pair in binary_pairs:
    print(f"alpha matrix for {pair[0]} | {pair[1]}:")
    print(matrix_table.mat(
        "alpha",
        pair,
        symbol_format='numeric',
    ))

    print(f"alpha matrix as dict for {pair[0]} | {pair[1]}:")
    print(matrix_table.mat(
        "alpha",
        pair,
        symbol_format='alphabetic',
    ))

    # ! formula-state key
    print(f"alpha matrix as dict by formula-state for {pair[0]} | {pair[1]}:")
    print(matrix_table.mat(
        "alpha",
        pair,
        symbol_format='alphabetic',
        component_key='Formula-State',
    ))

print("a matrix for methanol | ethanol:")
print(matrix_table.mat(
    "a",
    ["methanol", "ethanol"],
    symbol_format='numeric',
))

# SECTION: access full ternary matrix with mat()
ternary_components = [
    "methanol",
    "ethanol",
    "butyl-methyl-ether",
]

print("ternary component ids:")
print(matrix_table.get_component_ids(ternary_components))

print("ternary matrix rows:")
print(matrix_table.get_matrix_rows(ternary_components))

alpha_ternary_matrix = matrix_table.mat(
    "alpha",
    ternary_components,
    symbol_format='numeric',
)
print("alpha ternary matrix:")
print(alpha_ternary_matrix)
# >> check
if isinstance(alpha_ternary_matrix, np.ndarray):
    print(f"alpha ternary matrix shape: {alpha_ternary_matrix.shape}")

print("alpha ternary matrix as dict:")
print(matrix_table.mat(
    "alpha",
    ternary_components,
    symbol_format='alphabetic',
))

print("alpha ternary matrix as dict by formula:")
print(matrix_table.mat(
    "alpha",
    ternary_components,
    symbol_format='alphabetic',
    component_key='Formula',
))

print("alpha ternary matrix as dict by formula-state:")
print(matrix_table.mat(
    "alpha",
    ternary_components,
    symbol_format='alphabetic',
    component_key='Formula-State',
))

print("alpha ternary matrix as dict by name-formula:")
print(matrix_table.mat(
    "alpha",
    ternary_components,
    symbol_format='alphabetic',
    component_key='Name-Formula',
))

print("alpha ternary matrix as dict by name-formula-state:")
print(matrix_table.mat(
    "alpha",
    ternary_components,
    symbol_format='alphabetic',
    component_key='Name-Formula-State',
))

a_ternary_matrix = matrix_table.mat(
    "a",
    ternary_components,
    symbol_format='numeric',
)
print("a ternary matrix:")
print(a_ternary_matrix)
# >> check
if isinstance(a_ternary_matrix, np.ndarray):
    print(f"a ternary matrix shape: {a_ternary_matrix.shape}")

# SECTION: use Component objects directly with matX()
alpha_ternary_matrix_x = matrix_table.matX(
    "alpha",
    multi_component_mixture,
    symbol_format='numeric',
)
print("alpha ternary matrix using matX:")
print(alpha_ternary_matrix_x)
# >> check
if isinstance(alpha_ternary_matrix_x, np.ndarray):
    print(f"alpha ternary matrix using matX shape: {alpha_ternary_matrix_x.shape}")

print("alpha ternary matrix using matX as dict by formula-state:")
print(matrix_table.matX(
    "alpha",
    multi_component_mixture,
    symbol_format='alphabetic',
    component_key='Formula-State',
))
