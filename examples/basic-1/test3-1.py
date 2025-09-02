# import packages/modules
import os
import pyThermoDB as ptdb
from rich import print

# get versions
print(ptdb.__version__)

# ====================================
# BUILD THERMODB
# ====================================
# current file path
current_path = os.path.dirname(os.path.abspath(__file__))
print(current_path)

# build a thermodb
thermo_db = ptdb.build_thermodb(thermodb_name="CO2-thermodb")
print(type(thermo_db))

# version
print(thermo_db.build_version)

# thermodb name
print(thermo_db.thermodb_name)

# add TableData
# add TableEquation

# property name
property_name = 'CO2-enthalpy-of-formation'

# add dict
thermo_db.add_data(
    property_name,
    {'dHf_IG': 152, 'units': 'kJ/mol', 'message': 'from NIST'}
)

# save
thermo_db.save(f'{property_name}', current_path)
