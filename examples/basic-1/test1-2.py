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

# ===============================
# DATABOOK LIST
# ===============================
# databook
db_list = tdb.list_databooks(res_format='json')
print(db_list)

# databook info
db_info = tdb.databook_info(
    'Chemical Thermodynamics for Process Simulation',
    res_format='json'
)
print(db_info)

# databook info
db_info = tdb.databook_info(
    1,
    res_format='json'
)
print(db_info)

# databook info
db_info = tdb.databook_info(
    "1",
    res_format='json'
)
print(db_info)

# ===============================
# DATABOOK ID
# ===============================
db_id = tdb.get_databook_id(
    'Chemical Thermodynamics for Process Simulation',
    res_format='dict'
)
print(db_id)

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
# tb_lists = tdb.list_tables(
#     'Chemical Thermodynamics for Process Simulation', res_format='json')
# print(tb_lists)

tb_lists = tdb.list_tables(
    'Properties of Gases and Liquids',
    res_format='json'
)
print(tb_lists)

# ===============================
# TABLE DESCRIPTION
# ===============================
# table info
tb_description = tdb.table_description(
    'Properties of Gases and Liquids', 1,
    res_format='str'
)
print(tb_description)

tb_description = tdb.table_description(
    'Chemical Thermodynamics for Process Simulation',
    1,
    res_format='str'
)
print(tb_description)

tb_description = tdb.table_description(
    3, 2, res_format='str')
print(tb_description)

# ===============================
# TABLE ID
# ===============================
tb_id = tdb.get_table_id(
    'Properties of Gases and Liquids',
    'Section C Ideal Gas and Liquid Heat Capacities',
    res_format='dict'
)
print(tb_id)

# ===============================
# TABLE SOURCE
# ===============================
# databook name from table name
db_name = tdb.find_table_source(
    'Section C Ideal Gas and Liquid Heat Capacities')
print(db_name)

# ===============================
# TABLE INFO
# ===============================
# display a table
# tb_info = tdb.table_info(
#     'Chemical Thermodynamics for Process Simulation', 1, res_format='dict')
tb_info = tdb.table_info(
    'Properties of Gases and Liquids',
    'Section C Ideal Gas and Liquid Heat Capacities',
    res_format='dict'
)
print(tb_info)

# ===============================
# LOAD TABLES
# ===============================
# load equation to check
vapor_pressure_tb = tdb.equation_load(
    'Chemical Thermodynamics for Process Simulation',
    2
)
print(vapor_pressure_tb.eq_structure(1))

# all equations
eq_sample = tdb.equation_load(1, 4)
print(eq_sample.eqs_structure())

# heat capacity
heat_capacity_ig_tb = tdb.equation_load(
    'Properties of Gases and Liquids',
    'Section C Ideal Gas and Liquid Heat Capacities'
)
print(heat_capacity_ig_tb.eq_structure(1))

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
CO2_check_availability = tdb.check_component(comp1, 1, 2)
print(CO2_check_availability)


CO2_check_availability = tdb.check_component(
    comp1,
    'Properties of Gases and Liquids',
    'Section C Ideal Gas and Liquid Heat Capacities'
)
print(CO2_check_availability)

# load comp data
# comp_data = tdb.get_component_data(comp1, 1, 2, dataframe=True)
# pp(comp_data)

# check component
CO2_check_availability = tdb.check_component(
    comp1,
    "Chemical Thermodynamics for Process Simulation",
    "Table A.1 General data for selected compounds"
)
print(CO2_check_availability)


CO2_check_availability = tdb.check_component(
    comp1,
    "Chemical Thermodynamics for Process Simulation",
    "Table A.2 Vapor pressure correlations for selected compounds"
)
print(CO2_check_availability)

# ====================================
# SEARCH IN THE DATABOOK
# ====================================
# search terms
# key1 = 'Carbon dioxide'
# key2 = 'CO2'
# search_terms = [key1, key2]
# # search_terms = [key1]
# search_res = tdb.search_databook(
#     search_terms, res_format='json', search_mode='exact')
# print(search_res)

# search terms
# looking through Name
key1 = 'Carbon dioxide'
# search terms
search_terms = [key1]
# # column names
# column_names = ['Name']
# start search
search_res = tdb.search_databook(
    search_terms,
    res_format='dict',
    search_mode='exact'
)
print(search_res)

# search terms
# looking through Formula
key1 = 'CO2'
# search terms
search_terms = [key1]
# column names
column_names = ['Formula']
# start search
search_res = tdb.search_databook(
    search_terms,
    res_format='json',
    search_mode='exact',
    column_names=column_names
)
print(search_res)

# ====================================
# BUILD DATA
# ====================================
# build data
CO2_data = tdb.build_data(
    comp1,
    "Chemical Thermodynamics for Process Simulation",
    "Table A.1 General data for selected compounds"
)
print(CO2_data.data_structure())

# ACCESS DATA
# by ID
print(CO2_data.get_property(12))
# by property name
print(CO2_data.get_property('standard-Gibbs-energy-of-formation'))
# by symbol
print(CO2_data.get_property('GiEnFo_IG'))

#
print(CO2_data.get_property('EnFo_IG'))

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

# heat capacity (CO2)
# "record-5": {
#         "search-mode": "exact",
#         "search-terms": "CO2",
#         "databook-id": 1,
#         "databook-name": "Perry's Chemical Engineers' Handbook",
#         "table-id": 4,
#         "table-name": "TABLE 2-153 Heat Capacities of Inorganic and Organic Liquids",
#         "data-type": "equations"
#     }
CO2_cp_IG = tdb.build_equation(
    comp1,
    "Perry's Chemical Engineers' Handbook",
    'TABLE 2-153 Heat Capacities of Inorganic and Organic Liquids'
)
# parms
print(CO2_cp_IG.eq_id)
print(CO2_cp_IG.args)
print(CO2_cp_IG.arg_symbols)
print(CO2_cp_IG.parms)
print(CO2_cp_IG.parms_values)
print(CO2_cp_IG.returns)
print(CO2_cp_IG.return_symbols)
print(CO2_cp_IG.body)
print(CO2_cp_IG.equations)
print('CO2 heat capacity (IG)', CO2_cp_IG.cal(T=300))

# summary
print(CO2_cp_IG.summary)

# NOTE: normalization
print(CO2_cp_IG.normalized_fn_body(1))
print('Normalized functions:')
print(CO2_cp_IG.normalized_fns())

# args
CO2_cp_IG_args = {
    'T': 300
}
print('CO2 heat capacity (IG)', CO2_cp_IG.cal(**CO2_cp_IG_args))

a = 1

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
Cp_eq = tdb.build_equation(
    comp1,
    "Chemical Thermodynamics for Process Simulation",
    "Table A.5 Liquid heat capacity correlations for selected compounds"
)
# parms
print(Cp_eq.eq_id)
print(Cp_eq.args)
print(Cp_eq.arg_symbols)
print(Cp_eq.parms)
print(Cp_eq.parms_values)
print(Cp_eq.returns)
print(Cp_eq.return_symbols)
# print(Cp_eq.body)
# print(Cp_eq.equations)
print('liquid heat capacity', Cp_eq.cal(T=253.15, Tc=CO2_Tc, MW=CO2_MW))

# using args dict
args_dict = {'T': 253.15, 'Tc': CO2_Tc, 'MW': CO2_MW}
print('liquid heat capacity', Cp_eq.cal(**args_dict))

# # summary
# print(Cp_eq.summary)

# ideal gas heat capacity
Cp_ig_eq = tdb.build_equation(
    'trichloromethane',
    'Properties of Gases and Liquids',
    'Section C Ideal Gas and Liquid Heat Capacities'
)

# parms
print(Cp_ig_eq.eq_id)
print(Cp_ig_eq.args)
print(Cp_ig_eq.arg_symbols)
# print(Cp_ig_eq.parms)
print(Cp_ig_eq.returns)
print(Cp_ig_eq.return_symbols)
# print(Cp_ig_eq.body)
# print(Cp_ig_eq.equations)
print('ideal-gas heat capacity', Cp_ig_eq.cal(T=298.15))
# # summary
# print(Cp_ig_eq.summary)
