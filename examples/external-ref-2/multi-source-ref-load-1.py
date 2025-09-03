# import packages/modules
import os
from rich import print
import pyThermoDB as ptdb
from pyThermoDB.core import TableData, TableEquation, TableMatrixData

# get versions
# print(pt.get_version())
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
# ====================================
# parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))

# files
thermodb_file_name = 'carbon dioxide-content-1.pkl'
thermodb_file_name = 'carbon dioxide-md-2.pkl'
thermodb_file_name = 'methanol-yml-3.pkl'
thermodb_file = os.path.join(parent_dir, thermodb_file_name)

# ====================================
# LOAD THERMODB
# ====================================
# load a thermodb
thermo_db_loaded = ptdb.load_thermodb(
    os.path.join(parent_dir, thermodb_file))
print(type(thermo_db_loaded))

# check
print(thermo_db_loaded.check())

# ====================================
# SELECT PROPERTY
# ====================================
prop1_ = thermo_db_loaded.select('general')
# check
if not isinstance(prop1_, TableData):
    raise TypeError("The selected property is not of type 'TableData'")
# type
print(type(prop1_))
print(prop1_.prop_data)

# ! old format
print(prop1_.get_property('MW'))

# ! new format
_src = 'general | MW'
print(thermo_db_loaded.retrieve(_src, message="molecular weight"))

# ====================================
# SELECT A FUNCTION
# ====================================
# select function
func1_ = thermo_db_loaded.select_function('heat-capacity')
print(type(func1_))
print(func1_.args)
print(func1_.cal(T=295.15, message="heat capacity result"))


# ====================================
# COMPONENTS
# ====================================
# comp1
comp1 = "ethanol"
# comp2
comp2 = "methanol"

# ====================================
# DATA
# ====================================
# list all data
print(thermo_db_loaded.check_properties())

# load data
nrtl_alpha_data = thermo_db_loaded.check_property('non-randomness-parameters')
# check
if not isinstance(nrtl_alpha_data, TableMatrixData):
    raise TypeError("The selected property is not of type 'TableMatrixData'")
# type
print(type(nrtl_alpha_data))

# symbol
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

# NOTE: new format
# ! retrieve
nrtl_data_ = f"non-randomness-parameters | a_i_j | {comp1} | {comp2}"
print(thermo_db_loaded.retrieve(nrtl_data_, message="NRTL Alpha value"))

nrtl_data_ = f"non-randomness-parameters | alpha_i_j | {comp1} | {comp2}"
print(thermo_db_loaded.retrieve(nrtl_data_, message="NRTL Alpha value"))

# ! retrieve
nrtl_data_ = f"non-randomness-parameters | alpha_{comp1}_{comp2}"
print(thermo_db_loaded.retrieve(nrtl_data_, message="NRTL Alpha value"))

# ! ij method
nrtl_data_ = f"alpha_{comp1}_{comp2}"
nrtl_data_ = f"alpha | {comp1} | {comp2}"
alpha_ = nrtl_alpha_data.ij(nrtl_data_)
print(alpha_)

# ! ij matrix
nrtl_data_ = f"alpha_{comp1}_{comp2}"
nrtl_data_ = f"alpha | {comp1} | {comp2}"
alpha_ij = nrtl_alpha_data.ijs(nrtl_data_)
print(alpha_ij)

# ! ij matrix
mat_ = nrtl_alpha_data.mat('alpha', [comp2, comp1])
print(mat_)
mat_ = nrtl_alpha_data.mat('alpha', [comp1, comp2])
print(mat_)

mat_ = nrtl_alpha_data.mat('a', [comp2, comp1])
print(mat_)
mat_ = nrtl_alpha_data.mat('a', [comp1, comp2])
print(mat_)

mat_ = nrtl_alpha_data.mat('b', [comp2, comp1])
print(mat_)
mat_ = nrtl_alpha_data.mat('b', [comp1, comp2])
print(mat_)

mat_ = nrtl_alpha_data.mat('c', [comp2, comp1])
print(mat_)
mat_ = nrtl_alpha_data.mat('c', [comp1, comp2])
print(mat_)
