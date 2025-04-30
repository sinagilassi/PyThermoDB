# import packages/modules
import os
from rich import print
import pyThermoDB as ptdb

# get versions
# print(pt.get_version())
print(ptdb.__version__)

# ====================================
# ! SET FILES
# ====================================
# component
comp1 = 'toluene'

thermodb_file = f'{comp1}-1.pkl'
thermodb_path = os.path.join(os.getcwd(), 'tests', 'external-ref', 'thermodb')

# ====================================
# ! LOAD THERMODB
# ====================================
# load a thermodb
thermo_db_loaded = ptdb.load_thermodb(
    os.path.join(thermodb_path, thermodb_file))
print(type(thermo_db_loaded))

# check
print(thermo_db_loaded.check())

# check properties
print(thermo_db_loaded.check_properties())


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
# func1_ = thermo_db_loaded.select_function('heat-capacity')
# print(type(func1_))
# print(func1_.args)
# print(func1_.cal(T=295.15, message="heat capacity result"))

# select function
func2_ = thermo_db_loaded.select_function('vapor-pressure')
print(type(func2_))
print(func2_.args)
print(func2_.cal(T=295.15, message="vapor pressure result"))
