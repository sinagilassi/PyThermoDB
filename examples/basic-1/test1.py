# import packages/modules
import pyThermoDB as ptdb
from rich import print

# versions
print(ptdb.__version__)

# ===============================
# INITIALIZE THE DATABASE
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
tb_select = tdb.select_table(1, 2)
print(tb_select)

tb_select = tdb.select_table(
    1, 'TABLE 2-179 Enthalpies and Gibbs Energies of Formation, '
       'Entropies, and Net Enthalpies of Combustion')
print(tb_select)

# display a table
tb_info = tdb.table_info(1, 2)
print(tb_info)

# ===============================
# TABLE LOAD
# ===============================
# table load
res_ = tdb.table_data(1, 2)
print(res_)
print(type(res_))

# ===============================
# TABLE IN THE BROWSER
# ===============================
# open table in the browser
# tdb.table_view(1, 2)

# open all tables in the browser
# tdb.tables_view()

# ===============================
# LOAD TABLES
# ===============================
# load equation to check
vapor_pressure_tb = tdb.equation_load(1, 4)
print(vapor_pressure_tb.eq_structure(1))
# load data to check
data_table = tdb.data_load(1, 2)
print(data_table.data_structure())

# ====================================
# CHECK COMPONENT AVAILABILITY IN A TABLE
# ====================================
# check component availability in the databook and table
comp1 = "carbon Dioxide"
# CO2_check_availability = tdb.check_component(comp1, 1, 2)

# load comp data
# comp_data = tdb.get_component_data(comp1, 1, 2, dataframe=True)
# print(comp_data)

# check component
CO2_check_availability = tdb.check_component(comp1,
                                             "Perry's Chemical Engineers' Handbook",
                                             'TABLE 2-153 Heat Capacities of Inorganic '
                                             'and Organic Liquids')
print(CO2_check_availability)


# ====================================
# BUILD THERMO PROPERTY
# ====================================
# build thermo property
CO2_data_0 = tdb.build_thermo_property([comp1], 1, 2)
print(CO2_data_0.data_structure())
# get property
res_ = CO2_data_0.get_property(5)
print(res_, type(res_))
# by symbol
print(CO2_data_0.get_property('MW'))
# by property name
print(CO2_data_0.get_property('molecular-weight'))


# ====================================
# BUILD DATA
# ====================================
# build data
CO2_data = tdb.build_data(comp1, 1, 2)
print(CO2_data.data_structure())
# get property
res_ = CO2_data.get_property(5)
print(res_, type(res_))
# by symbol
print(CO2_data.get_property('MW'))
# by property name
print(CO2_data.get_property('molecular-weight'))

# ====================================
# BUILD EQUATION
# ====================================
# build an equation
eq = tdb.build_equation(comp1, 1, 4)
print(eq.args)
res = eq.cal(T=298.15)
print(res)
