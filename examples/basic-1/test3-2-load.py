# import packages/modules
import os
from rich import print
import pyThermoDB as ptdb
from pyThermoDB import (
    TableData,
    TableEquation,
    TableConstants,
    TableMatrixEquation,
    CompBuilder
)

# verify the version
print(ptdb.__version__)

# ====================================
# LOAD THERMODB
# ====================================
# parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))

# files
# file_name = 'Methane-1'
file_name = "Methane-custom-constant-1"
thermodb_file = f'{file_name}.pkl'
thermodb_path = os.path.join(parent_dir, thermodb_file)
print(thermodb_path)

# ====================================
# LOAD THERMODB
# ====================================
# load thermodb
data_thermodb: CompBuilder = ptdb.load_thermodb(thermodb_path)
print(type(data_thermodb))

# ====================================
# CHECK THERMODB
# ====================================
# check all properties and functions registered
print(data_thermodb.check())

# ====================================
# SELECT PROPERTY
# ====================================
print("[bold magenta]Select a property from the thermodb:[/bold magenta]")
prop1_ = data_thermodb.select('general')
# check
if not isinstance(prop1_, TableData):
    raise TypeError("The selected object is not a TableData instance.")
# type
print(type(prop1_))
print(prop1_.prop_data)

# ! old format
print(prop1_.get_property('dHf_IG'))

# ! new format
dHf_IG_src = 'general | dHf_IG'
print(data_thermodb.retrieve(dHf_IG_src, message="enthalpy of formation"))

# ====================================
# SELECT A FUNCTION
# ====================================
print("[bold magenta]Select a function from the thermodb:[/bold magenta]")
# select function
func1_: TableEquation | TableMatrixEquation = data_thermodb.select_function(
    'heat-capacity'
)
print(type(func1_))
print(func1_.args)
print(func1_.cal(T=295.15, message="heat capacity of methanol"))

# ====================================
# SELECT CONSTANTS
# ====================================
print("[bold magenta]Select constants from the thermodb:[/bold magenta]")

# select (universal method)
const0_ = data_thermodb.select('custom-constants')
print(type(const0_))

# select constants
const1_: TableConstants = data_thermodb.select_constant('custom-constants')
print(type(const1_))
# access constant
# ! R (scalar)
print(const1_.get_constant('R'))
# ! dG_rxn (dictionary)
print(const1_.get_constant('dG_rxn'))
# ! Xb (string)
print(const1_.get_constant('Xb'))
# ! X (list)
print(const1_.get_constant('X'))
# ! non-existing constant (can raise error)
print(const1_.get_constant('non_existing_constant', strict=False))
# print(general_const.get_constant('non_existing_constant'))
