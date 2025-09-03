# import packages/modules
import os
from typing import Any, Dict
from rich import print
import pyThermoDB as ptdb
from pyThermoDB.core import TableData, TableEquation

# get versions
# print(pt.get_version())
print(ptdb.__version__)

# ====================================
# ! SET FILES
# ====================================
# component
comp1 = 'toluene'
comp1 = 'methane'

thermodb_file = f'{comp1}-1.pkl'

parent_path = os.path.dirname(os.path.abspath(__file__))
print(parent_path)

# ====================================
# ! LOAD THERMODB
# ====================================
# load a thermodb
thermo_db_loaded = ptdb.load_thermodb(
    os.path.join(parent_path, thermodb_file))
print(type(thermo_db_loaded))

# check
print(thermo_db_loaded.check())

# check properties
print(thermo_db_loaded.check_properties())


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
# old format
print(prop1_.get_property('MW'))

# new format
_src = 'general | MW'
print(thermo_db_loaded.retrieve(_src, message="molecular weight"))

# ====================================
# SELECT A FUNCTION
# ====================================
# select function
# func1_ = thermo_db_loaded.select_function('heat-capacity')
# print(type(func1_))
# print(func1_.args)
# print(func1_.cal(T=295.15, message="heat capacity result"))

# select function
func2_ = thermo_db_loaded.select_function('vapor-pressure')
print(type(func2_))
print(func2_.args)
print(func2_.cal(T=295.15, message="vapor pressure result"))
