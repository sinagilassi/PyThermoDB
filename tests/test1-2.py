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
tb_lists = tdb.list_tables('Chemical Thermodynamics for Process Simulation')
print(tb_lists)


# ===============================
# TABLE INFO
# ===============================
# display a table
tb_info = tdb.table_info('Chemical Thermodynamics for Process Simulation', 1)
print(tb_info)

# ===============================
# LOAD TABLES
# ===============================
# load equation to check
vapor_pressure_tb = tdb.equation_load(
    'Chemical Thermodynamics for Process Simulation', 2)
pp(vapor_pressure_tb.eq_structure(1))

# load data to check
data_table = tdb.data_load('Chemical Thermodynamics for Process Simulation', 1)
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
                                             "Chemical Thermodynamics for Process Simulation",
                                             "Table A.1 General data for selected compounds")
pp(CO2_check_availability)


# ====================================
# BUILD DATA
# ====================================
# build data
CO2_data = tdb.build_data(comp1, "Chemical Thermodynamics for Process Simulation",
                          "Table A.1 General data for selected compounds")
pp(CO2_data.data_structure())

# ACCESS DATA
# by ID
pp(CO2_data.get_property(12))
# by property name
pp(CO2_data.get_property('standard-Gibbs-energy-of-formation'))
# by symbol
pp(CO2_data.get_property('dGf_std'))

# CO2 Tc [K]
CO2_Tc = float(CO2_data.get_property('Tc')['value'])
# CO2 Pc [bar]
CO2_Pc = float(CO2_data.get_property('Pc')['value'])


# ====================================
# BUILD EQUATION
# ====================================
# build an equation
eq = tdb.build_equation(
    comp1, "Chemical Thermodynamics for Process Simulation", "Table A.2 Vapor pressure correlations for selected compounds")

# args
pp(eq.args)

res = eq.cal(T=253.15, Tc=CO2_Tc, Pc=CO2_Pc)

# return
pp(eq.returns)
pp(res)
