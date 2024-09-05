# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp


# dir
# print(dir(pt))
# get versions
# print(pt.get_version())
print(ptdb.__version__)

# ===============================
# databook reference initialization
# ===============================
tdb = ptdb.init()
# print("type: ", type(tdb))
# print("dir: ", dir(tdb))

# databook
# db = tdb.databooks()
# print(db)

# select a database
# tdb.select_databook("Perry's Chemical Engineers' Handbook")
# tdb.select_databook(1)

# check selected database
# print(tdb.selected_databook)
# list table available
# print(tdb.tables())

# manually
# print(tdb.tables(databook=1))

# display a table
tb_info = tdb.table_info(1, 2)
print(tb_info)

# load table
# vapor_pressure_tb = tdb.equation_load(1, 4)
# pp(vapor_pressure_tb.eq_structure(1))

# data_table = tdb.data_load(1, 2)
# pp(data_table.data_structure())

# check component availability in the databook and table
comp1 = "carbon Dioxide"
# CO2_check_availability = tdb.check_component(comp1, 1, 2)

# load comp data
# comp_data = tdb.get_component_data(comp1, 1, 2, dataframe=True)
# pp(comp_data)

# build data
# CO2_data = tdb.build_data(comp1, 1, 2)
# pp(CO2_data.data_structure())

# pp(CO2_data.get_property(4))

# build an equation
eq = tdb.build_equation(comp1, 1, 4)

args = {
    "T": 290,
}
pp(eq.args)

res = eq.cal(args)

pp(res*1e-5)
