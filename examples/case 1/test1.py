# import packages/modules
import pyThermoDB as ptdb
from rich import print


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
tb_lists = tdb.list_tables(3)
print(tb_lists)


# ===============================
# TABLE INFO
# ===============================
# display a table
tb_info = tdb.table_info(3, 2)
print(tb_info)

# ===============================
# LOAD TABLES
# ===============================
# load equation to check
vapor_pressure_tb = tdb.equation_load(3, 1)
print(vapor_pressure_tb.eq_structure(1))
# load data to check
data_table = tdb.data_load(3, 2)
print(data_table.data_structure())

# ====================================
# CHECK COMPONENT AVAILABILITY IN A TABLE
# ====================================
# check component availability in the databook and table
comp1 = "acetylene"
CO2_check_availability = tdb.check_component(comp1, 1, 2)

# load comp data
# comp_data = tdb.get_component_data(comp1, 1, 2, dataframe=True)
# pp(comp_data)

# ====================================
# CHECK COMPONENT AVAILABILITY IN A TABLE BY QUERY
# ====================================
# query
query = f"Name.str.lower() == '{comp1.lower()}' & State == 'g'"
COMP1_check_availability = tdb.check_component(
    comp1, 3, 2, query, query=True)

COMP1_check_availability = tdb.check_component(
    comp1, "Chemical and Engineering Thermodynamics", "Table A.IV Enthalpies and Gibbs Energies of Formation", query, query=True)

# ====================================
# BUILD DATA
# ====================================
# build data
comp1_data = tdb.build_data(comp1, 3, 2)
print(comp1_data.data_structure())

print(comp1_data.get_property(5))
print(comp1_data.get_property(6))
# ====================================
# BUILD EQUATION
# ====================================
# build an equation
comp1_eq = tdb.build_equation(comp1, 3, 1)

print(comp1_eq.args)
print(comp1_eq.returns)
print(comp1_eq.body_integral)
print(comp1_eq.custom_integral)


# res = comp1_eq.cal(T=298.15)
# pp(res)

# integral
# res1 = comp1_eq.cal_integral(T1=125, T2=220)
# derivative
res2 = comp1_eq.cal_first_derivative(T=298.15)
