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
tb_lists = tdb.list_tables(1)
print(tb_lists)


# ===============================
# TABLE INFO
# ===============================
# display a table
tb_info = tdb.table_info(1, 2)
print(tb_info)

# ===============================
# LOAD TABLES
# ===============================
# load equation to check
vapor_pressure_tb = tdb.equation_load(1, 4)
pp(vapor_pressure_tb.eq_structure(1))
# load data to check
data_table = tdb.data_load(1, 2)
pp(data_table.data_structure())

# ====================================
# CHECK COMPONENT AVAILABILITY IN A TABLE
# ====================================
# check component availability in the databook and table
comp1 = "carbon Dioxide"
# CO2_check_availability = tdb.check_component(comp1, 1, 2)

# load comp data
# comp_data = tdb.get_component_data(comp1, 1, 2, dataframe=True)
# pp(comp_data)

# check component
CO2_check_availability = tdb.check_component(comp1,
                                             "Perry's Chemical Engineers' Handbook",
                                             "TABLE 2-153 Heat Capacities of Inorganic and Organic Liquids")
pp(CO2_check_availability)

# ====================================
# BUILD DATA
# ====================================
# build data
CO2_data = tdb.build_data(comp1, 1, 2)
pp(CO2_data.data_structure())

pp(CO2_data.get_property(4))

# ====================================
# BUILD EQUATION
# ====================================
# build an equation
eq = tdb.build_equation(comp1, 1, 4)

pp(eq.args)

res = eq.cal(T=298.15)

pp(res*1e-5)
