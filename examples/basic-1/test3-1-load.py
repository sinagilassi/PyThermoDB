# import packages/modules
import os
from rich import print
import pyThermoDB as ptdb

# version
print(ptdb.__version__)

# ====================================
# LOAD THERMODB
# ====================================
# current dir
current_dir = os.getcwd()
print(current_dir)
# file path
current_path = os.path.dirname(os.path.abspath(__file__))
print(current_path)
# ref # property name
file_name = 'CO2-enthalpy-of-formation'
thermodb_file = f'{file_name}.pkl'
thermodb_path = os.path.join(current_path, thermodb_file)
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
