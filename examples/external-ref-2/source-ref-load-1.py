# import packages/modules
from typing import Dict, Any
import os
from rich import print
import pyThermoDB as ptdb
from pyThermoDB.models import Component
from pyThermoDB.core import TableData, TableEquation

# get versions
# print(pt.get_version())
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
# ====================================
# parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))

# file
thermodb_file = 'carbon dioxide-yml-3.pkl'
thermodb_path = os.path.join(parent_dir, thermodb_file)
print(thermodb_path)

# ====================================
# LOAD THERMODB
# ====================================
# load a thermodb
thermo_db_loaded = ptdb.load_thermodb(
    thermodb_file=thermodb_path
)
print(type(thermo_db_loaded))

# check
print(thermo_db_loaded.check())

# ====================================
# SELECT PROPERTY
# ====================================
prop1_ = thermo_db_loaded.select('general')
# check
if not isinstance(prop1_, TableData):
    raise TypeError("prop1_ is not a TableData instance")
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
