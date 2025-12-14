# import packages/modules
import pyThermoDB as ptdb
from rich import print

# versions
print(ptdb.__version__)

# ===============================
# databook reference initialization
# ===============================
tdb = ptdb.init()

# ===============================
# DATABOOK LIST
# ===============================
# databook
db_list = tdb.list_databooks()
print(db_list)

# ===============================
# TABLE LIST
# ===============================
# table list
tb_lists = tdb.list_tables(1, res_format='dict')
print(tb_lists)

# ===============================
# TABLE INFO
# ===============================
# select a table
tb_select = tdb.select_table(7, 1)
print(tb_select)

tb_select = tdb.select_table(7, 2)
print(tb_select)

# display a table
tb_info = tdb.table_info(7, 1)
print(tb_info)

# ===============================
# TABLE LOAD
# ===============================
# table load
res_ = tdb.table_data(7, 1)
print(res_)
print(type(res_))

# ===============================
# TABLE IN THE BROWSER
# ===============================
# open table in the browser
# tdb.table_view(1, 2)

# open all tables in the browser
# tdb.tables_view()
