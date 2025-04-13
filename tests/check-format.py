# import packages/modules
import os
from rich import print
import pyThermoDB as ptdb

# get versions
# print(pt.get_version())
print(ptdb.__version__)

# ====================================
# INITIALIZATION OWN THERMO DB
# ====================================
thermo_db = ptdb.init()

# ====================================
# EQUATION BODY
# ====================================
# files
yml_file = 'tests\\equation-body.yml'
yml_path = os.path.join(os.getcwd(), yml_file)

# check equation body
res = thermo_db.equation_format_checker(yml_path)
print(res)
