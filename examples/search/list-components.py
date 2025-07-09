# import packages/modules
import pyThermoDB as ptdb
from rich import print


# dir
# print(dir(pt))
# get versions
# print(pt.get_version())
print(ptdb.__version__)
print(ptdb.__author__)
print(ptdb.__description__)

# ===============================
# databook reference initialization
# ===============================
tdb = ptdb.init()

# ===============================
# DESCRIPTIONS
# ===============================
# databook description
db_descriptions = tdb.list_descriptions(res_format='json')
print(db_descriptions)

# ===============================
# COMPONENT LIST
# ===============================
# component list
component_list = tdb.list_components(res_format='json')
print(component_list)
print(len(component_list))

# component info
component_info = tdb.list_components_info(res_format='json')
print(component_info)
print(len(component_info))
