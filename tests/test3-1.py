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
# BUILD THERMODB
# ====================================
# build a thermodb
thermo_db = ptdb.build_thermodb()
print(type(thermo_db))

# add TableData
# add TableEquation

# property name
property_name = 'CO2-enthalpy-of-formation'

# add dict
thermo_db.add_data(
    property_name, {'dHf_IG': 152, 'units': 'kJ/mol', 'message': 'from NIST'})

# save
thermo_db.save(f'{property_name}', 'tests')
