# import packages/modules
import os
from rich import print
import pyThermoDB as ptdb
from pyThermoDB import TableData

# verify the version
print(ptdb.__version__)

# ====================================
# LOAD THERMODB
# ====================================
# parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))

# files
file_name = 'Methane-1'
thermodb_file = f'{file_name}.pkl'
thermodb_path = os.path.join(parent_dir, thermodb_file)
print(thermodb_path)

# ====================================
# LOAD THERMODB
# ====================================
# load thermodb
data_thermodb = ptdb.load_thermodb(thermodb_path)
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
func1_ = data_thermodb.select_function('heat-capacity')
print(type(func1_))
print(func1_.args)
print(func1_.cal(T=295.15, message="heat capacity of methanol"))
