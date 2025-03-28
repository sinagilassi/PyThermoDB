# import packages/modules
import os
from rich import print
import pyThermoDB as ptdb

# verify the version of pyThermoDB
print(ptdb.__version__)

# ====================================
# LOAD THERMODB
# ====================================
# ref # property name
file_name = 'methanol-1'
thermodb_file = f'{file_name}.pkl'
thermodb_path = os.path.join(os.getcwd(), 'notebooks', thermodb_file)
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
