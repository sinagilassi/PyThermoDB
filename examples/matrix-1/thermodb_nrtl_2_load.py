# import packages/modules
import pyThermoDB as ptdb
import os
from rich import print


# ====================================
# COMPONENTS
# ====================================
# comp1
comp1 = "methanol"
# comp2
comp2 = "ethanol"
# comp3
comp3 = 'benzene'

# ====================================
# LOAD THERMODB
# ====================================
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Parent directory: {parent_dir}")

# ref
thermodb_file = 'thermodb_nrtl_1.pkl'
thermodb_path = os.path.join(parent_dir, thermodb_file)
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

# ! load data
nrtl_alpha_data = nrtl_thermodb.check_property('nrtl_alpha')
print(type(nrtl_alpha_data))

nrtl_alpha_data = nrtl_thermodb.select_property('nrtl_alpha')
print(type(nrtl_alpha_data))

# heat of formation at 298.15K
print(nrtl_alpha_data.matrix_data_structure())

print(nrtl_alpha_data.get_property('Alpha_i_1', comp1))
# by symbol

# old format
print(nrtl_alpha_data.get_matrix_property("Alpha_i_j",
                                          [comp1, comp2], symbol_format='alphabetic'))

# new format
nrtl_data_ = " nrtl_alpha | Alpha_i_j | methanol | ethanol"
print(nrtl_thermodb.retrieve(nrtl_data_, message="NRTL Alpha value"))

# new format
nrtl_data_ = "nrtl_alpha | Alpha_methanol_ethanol"
print(nrtl_thermodb.retrieve(nrtl_data_, message="NRTL Alpha value"))

# ij method
nrtl_data_ = "Alpha_methanol_ethanol"
alpha_ = nrtl_alpha_data.ij(nrtl_data_)
print(alpha_)

# ====================================
# EQUATIONS
# ====================================
# list all functions
print(nrtl_thermodb.check_functions())

# ! equation 1
nrtl_tau_eq = nrtl_thermodb.check_function('nrtl_tau')
# args
print(nrtl_tau_eq.args)
# return
print(nrtl_tau_eq.returns)
# parms values
print(nrtl_tau_eq.parms_values)
# cal
nrtl_tau_cal = nrtl_tau_eq.cal(message=f"NRTL Tau value", T=298.15)
print(nrtl_tau_cal)
