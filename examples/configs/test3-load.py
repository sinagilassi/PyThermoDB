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
file_name = 'CO2_thermodb'
file_name = 'CO2_thermodb_ignore_state'
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
prop1_ = data_thermodb.select('CUSTOM-REF-1::general-data')
# check
if not isinstance(prop1_, TableData):
    raise TypeError("The selected object is not a TableData instance.")
# type
print(type(prop1_))
print(prop1_.prop_data)

# ! old format
print(prop1_.get_property('EnFo'))

# ! new format
src_ = 'CUSTOM-REF-1::general-data | EnFo'
print(data_thermodb.retrieve(src_, message="enthalpy of formation"))

# ====================================
# SELECT A FUNCTION
# ====================================
print("[bold magenta]Select a function from the thermodb:[/bold magenta]")
# select function
func1_ = data_thermodb.select_function('CUSTOM-REF-1::vapor-pressure')
print(type(func1_))
print(func1_.args)
print(func1_.cal(T=295.15, message="vapor pressure"))

# select function
func2_ = data_thermodb.select_function('CUSTOM-REF-1::ideal-gas-heat-capacity')
print(type(func2_))
print(func2_.args)
print(func2_.cal(T=350.0, message="heat capacity"))
