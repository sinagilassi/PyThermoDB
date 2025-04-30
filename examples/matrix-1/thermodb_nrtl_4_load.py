# import packages/modules
import pyThermoDB as ptdb
import os
from rich import print


# ====================================
# COMPONENTS
# ====================================
# comp1
comp1 = "ethanol"
# comp2
comp2 = "butyl-methyl-ether"

# ====================================
# LOAD THERMODB
# ====================================
# ref
thermodb_file = 'thermodb_nrtl_ethanol_butyl-methyl-ether_1.pkl'
thermodb_path = os.path.join(os.getcwd(), 'tests', thermodb_file)
print(thermodb_path)

# ====================================
# LOAD THERMODB
# ====================================
# load thermodb
nrtl_thermodb = ptdb.load_thermodb(thermodb_path)
print(type(nrtl_thermodb))

# ====================================
# CHECK THERMODB
# ====================================
# check all properties and functions registered
print(nrtl_thermodb.check())

# ====================================
# DATA
# ====================================
# list all data
print(nrtl_thermodb.check_properties())

# load data
nrtl_alpha_data = nrtl_thermodb.check_property('non-randomness-parameters')
print(type(nrtl_alpha_data))

# symbol
print(nrtl_alpha_data.matrix_symbol)

# heat of formation at 298.15K
print(nrtl_alpha_data.matrix_data_structure())

# old format
print(nrtl_alpha_data.get_matrix_property("alpha_i_j",
                                          [comp1, comp2], symbol_format='alphabetic'))

# new format
nrtl_data_ = f" non-randomness-parameters | alpha_i_j | {comp1} | {comp2}"
print(nrtl_thermodb.retrieve(nrtl_data_, message="NRTL Alpha value"))

# new format
nrtl_data_ = f"non-randomness-parameters | alpha_{comp1}_{comp2}"
print(nrtl_thermodb.retrieve(nrtl_data_, message="NRTL Alpha value"))

# ij method
nrtl_data_ = f"alpha_{comp1}_{comp2}"
nrtl_data_ = f"alpha | {comp1} | {comp2}"
alpha_ = nrtl_alpha_data.ij(nrtl_data_)
print(alpha_)

# ij matrix
nrtl_data_ = f"alpha_{comp1}_{comp2}"
nrtl_data_ = f"alpha | {comp1} | {comp2}"
alpha_ij = nrtl_alpha_data.ijs(nrtl_data_)
print(alpha_ij)