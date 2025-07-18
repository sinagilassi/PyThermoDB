# import packages/modules
import os
from rich import print
import pyThermoDB as ptdb

# get versions
# print(pt.get_version())
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
# ====================================
# parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Parent directory: {parent_dir}")

# file
thermodb_file = 'toluene-1.pkl'

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
print(type(prop1_))
print(prop1_.prop_data)

# old format
print(prop1_.get_property('MW'))

# new format
_src = 'general | MW'
print(thermo_db_loaded.retrieve(_src, message="molecular weight"))

# ====================================
# SELECT A FUNCTION
# ====================================
# select function
func1_ = thermo_db_loaded.select_function('vapor-pressure')
print(type(func1_))
print(func1_.args)
print(func1_.cal(T=295.15, message="vapor pressure result"))
