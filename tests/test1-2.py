# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp
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
# DATABOOK LIST
# ===============================
# databook
db_list = tdb.list_databooks(res_format='json')
print(db_list)

# ===============================
# SYMBOL LIST
# ===============================
# symbols
symbol_list = tdb.list_symbols(res_format='json')
print(symbol_list)

# ===============================
# TABLE LIST
# ===============================
# table list
tb_lists = tdb.list_tables(
    'Chemical Thermodynamics for Process Simulation', res_format='json')
print(tb_lists)


# ===============================
# TABLE INFO
# ===============================
# display a table
# tb_info = tdb.table_info(
#     'Chemical Thermodynamics for Process Simulation', 1, res_format='dict')
tb_info = tdb.table_info(
    'CO2 Hydrogenation Reaction', 3, res_format='dict')
print(tb_info)

# ===============================
# LOAD TABLES
# ===============================
# load equation to check
vapor_pressure_tb = tdb.equation_load(
    'Chemical Thermodynamics for Process Simulation', 2)
print(vapor_pressure_tb.eq_structure(1))

# load data to check
data_table = tdb.data_load('Chemical Thermodynamics for Process Simulation', 1)
print(data_table.data_structure())

# ====================================
# CHECK COMPONENT AVAILABILITY IN A TABLE
# ====================================
# check component availability in the databook and table
comp1 = "carbon Dioxide"
#  CO
# comp1 = "carbon monoxide"
# CO2_check_availability = tdb.check_component(comp1, 1, 2)

# load comp data
# comp_data = tdb.get_component_data(comp1, 1, 2, dataframe=True)
# pp(comp_data)

# check component
CO2_check_availability = tdb.check_component(comp1,
                                             "Chemical Thermodynamics for Process Simulation",
                                             "Table A.1 General data for selected compounds")
print(CO2_check_availability)


CO2_check_availability = tdb.check_component(comp1,
                                             "Chemical Thermodynamics for Process Simulation",
                                             "Table A.2 Vapor pressure correlations for selected compounds")
print(CO2_check_availability)

# ====================================
# BUILD DATA
# ====================================
# build data
CO2_data = tdb.build_data(comp1, "Chemical Thermodynamics for Process Simulation",
                          "Table A.1 General data for selected compounds")
print(CO2_data.data_structure())

# ACCESS DATA
# by ID
print(CO2_data.get_property(12))
# by property name
print(CO2_data.get_property('standard-Gibbs-energy-of-formation'))
# by symbol
print(CO2_data.get_property('GiEnFo_IG'))

# CO2 Tc [K]
CO2_Tc = float(CO2_data.get_property('Tc')['value'])
print(CO2_Tc)
# CO2 Pc [bar]
CO2_Pc = float(CO2_data.get_property('Pc')['value'])
print(CO2_Pc)
# CO2 MW [g/mol]
CO2_MW = float(CO2_data.get_property('MW')['value'])
print(CO2_MW)

# ====================================
# BUILD EQUATION
# ====================================
# build an equation
# * vapor pressure
# eq = tdb.build_equation(
#     comp1, "Chemical Thermodynamics for Process Simulation", "Table A.2 Vapor pressure correlations for selected compounds")

# # args
# pp(eq.args)
# pp(eq.parms)

# res = eq.cal(T=253.15, Tc=CO2_Tc, Pc=CO2_Pc)

# # return
# pp(eq.returns)
# pp(res)

# liquid density
# rho_eq = tdb.build_equation(comp1, "Chemical Thermodynamics for Process Simulation",
#                             "Table A.3 Liquid density correlations for selected compounds")
# # parms
# pp(rho_eq.parms)
# pp(rho_eq.returns)
# pp(rho_eq.cal(T=253.15, Tc=CO2_Tc))

# enthalpy of vaporization
# Hvap_eq = tdb.build_equation(comp1, "Chemical Thermodynamics for Process Simulation",
#                              "Table A.4 Enthalpy of vaporization correlations for selected compounds")
# # parms
# pp(Hvap_eq.parms)
# pp(Hvap_eq.returns)
# print('enthalpy of vaporization', Hvap_eq.cal(T=253.15, Tc=CO2_Tc, MW=CO2_MW))

# liquid heat capacity
Cp_eq = tdb.build_equation(comp1, "Chemical Thermodynamics for Process Simulation",
                           "Table A.5 Liquid heat capacity correlations for selected compounds")
# parms
print(Cp_eq.eq_id)
print(Cp_eq.args)
print(Cp_eq.parms)
print(Cp_eq.returns)
print(Cp_eq.equations)
print('liquid heat capacity', Cp_eq.cal(T=253.15, Tc=CO2_Tc, MW=CO2_MW))
# summary
print(Cp_eq.summary)
