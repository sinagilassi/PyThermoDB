# import libs
import os
import pyThermoDB as ptdb
from pyThermoDB.core import TableMatrixData
from rich import print

# ====================================
# COMPONENTS
# ====================================
# comp1
comp1 = "ethanol"
# comp2
comp2 = "methanol"

# ====================================
# LOAD THERMODB
# ====================================
# parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Parent directory: {parent_dir}")

# ref
thermodb_file = 'thermodb_nrtl_mixture.pkl'
thermodb_file = 'thermodb_nrtl_mixture_inline.pkl'
thermodb_path = os.path.join(parent_dir, thermodb_file)
print(thermodb_path)

# ====================================
# ! LOAD THERMODB
# ====================================
# load thermodb
nrtl_thermodb = ptdb.load_thermodb(thermodb_path)
print(type(nrtl_thermodb))

# ====================================
# ! CHECK THERMODB
# ====================================
# check all properties and functions registered
print(nrtl_thermodb.check())

# ====================================
# ! DATA
# ====================================
# list all data
print(nrtl_thermodb.check_properties())

# SECTION: load data
nrtl_alpha_data = nrtl_thermodb.check_property('nrtl')
# check type
if not isinstance(nrtl_alpha_data, TableMatrixData):
    raise Exception("Data is not of type TableMatrixData!")

# check type
print(type(nrtl_alpha_data))

# NOTE: matrix table
print(nrtl_alpha_data.matrix_table)

# NOTE: symbol
print(nrtl_alpha_data.matrix_symbol)

# heat of formation at 298.15K
print(nrtl_alpha_data.matrix_data_structure())

# NOTE: old format
print(nrtl_alpha_data.get_matrix_property(
    "alpha_i_j",
    [comp1, comp2],
    symbol_format='alphabetic')
)

print(nrtl_alpha_data.get_matrix_property(
    "a_i_j",
    [comp1, comp2],
    symbol_format='alphabetic')
)

print(nrtl_alpha_data.get_matrix_property(
    "b_i_j",
    [comp1, comp2],
    symbol_format='alphabetic')
)

print(nrtl_alpha_data.get_matrix_property(
    "c_i_j",
    [comp1, comp2],
    symbol_format='alphabetic')
)

# SECTION: using retrieve
# NOTE: new format
# ! retrieve
nrtl_data_ = f"nrtl | a_i_j | {comp1} | {comp2}"
print(
    nrtl_thermodb.retrieve(
        nrtl_data_,
        message=f"NRTL Alpha value {comp1}-{comp2}"
    )
)

# ! retrieve
nrtl_data_ = f"nrtl | a_{comp1}_{comp2}"
print(
    nrtl_thermodb.retrieve(
        nrtl_data_,
        message=f"NRTL Alpha value {comp1}-{comp2}"
    )
)

nrtl_data_ = f"nrtl | b_{comp1}_{comp2}"
print(
    nrtl_thermodb.retrieve(
        nrtl_data_,
        message=f"NRTL Alpha value {comp1}-{comp2}"
    )
)

# SECTION: matrix data
# NOTE: binary
# a
res_ = nrtl_alpha_data.mat("a", [comp1, comp2])
print(res_)
res_ = nrtl_alpha_data.mat("a", [comp2, comp1])
print(res_)

# b
res_ = nrtl_alpha_data.mat("b", [comp1, comp2])
print(res_)
res_ = nrtl_alpha_data.mat("b", [comp2, comp1])
print(res_)

# c
res_ = nrtl_alpha_data.mat("c", [comp1, comp2])
print(res_)
res_ = nrtl_alpha_data.mat("c", [comp2, comp1])
print(res_)

# alpha
res_ = nrtl_alpha_data.mat("alpha", [comp1, comp2])
print(res_)

# unknown
res_ = nrtl_alpha_data.mat("unknown", [comp1, comp2])
print(res_)

# SECTION: using TableMatrixData methods
# NOTE: ij method
nrtl_data_ = f"a_{comp1}_{comp2}"
nrtl_data_ = f"a | {comp1} | {comp2}"
alpha_ = nrtl_alpha_data.ij(nrtl_data_)
print(alpha_)

# NOTE: ijs matrix
nrtl_data_ = f"a_{comp1}_{comp2}"
nrtl_data_ = f"a | {comp1} | {comp2}"
alpha_ij = nrtl_alpha_data.ijs(nrtl_data_)
print(alpha_ij)

# NOTE: mat matrix
mat_ = nrtl_alpha_data.mat('a', [comp2, comp1])
print(mat_)
