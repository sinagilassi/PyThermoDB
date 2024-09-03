# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp


# dir
# print(dir(pt))
# get versions
# print(pt.get_version())
print(ptdb.__version__)


# REFERENCE OBJECT
# ===============================
# init
ref = ptdb.ref()

# extract information
# list databooks
print(ref.list_databooks())
# list tables
print(ref.list_tables(1))
# load table
print(ref.load_table(1, 1))
# search table
print(ref.search_table(1, 1, "Formula", "CO2"))
