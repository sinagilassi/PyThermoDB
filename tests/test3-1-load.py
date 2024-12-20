# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp
import os
from rich import print

# dir
# print(dir(pt))
# get versions
# print(pt.get_version())
print(ptdb.__version__)

# ====================================
# LOAD THERMODB
# ====================================
# ref # property name
file_name = 'CO2-enthalpy-of-formation'
thermodb_file = f'{file_name}.pkl'
thermodb_path = os.path.join(os.getcwd(), 'tests', thermodb_file)
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
