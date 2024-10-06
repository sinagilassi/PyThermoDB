# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp
import os

# dir
# print(dir(pt))
# get versions
# print(pt.get_version())
print(ptdb.__version__)

# ====================================
# WEB APP
# ====================================
ptdb.check_thermodb()
