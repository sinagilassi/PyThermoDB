# Build ThermoDB for Components

## Import Libs

```python
# import packages/modules
import pyThermoDB as ptdb
from rich import print

# app version
print(ptdb.__version__)
```

## Initialize app

```python
# initialize the app to load all reference files including databook and tables
tdb = ptdb.init()
```

## Databooks

Databooks are thermodynamic property sources such as enthalpy of formation data, equations for the calculation of heat capacity.

### Databook Description

List all databooks and tables with their descriptions.

```python
# databook description
db_descriptions = tdb.list_descriptions(res_format='json')
# log
print(db_descriptions)

# {
#     "Perry's Chemical Engineers' Handbook": {
#         "DATABOOK-ID": 1,
#         "TABLE 2-8 Vapor Pressure of Inorganic and Organic Liquids": {
#             "DATABOOK-ID": 1,
#             "TABLE-ID": 1,
#             "DESCRIPTION": "This table provides the vapor pressure (VaPr) of inorganic and organic liquids as a function of temperature (T)   
# and its unit is in Pascal (Pa)."
#         },
#         "TABLE 2-179 Enthalpies and Gibbs Energies of Formation, Entropies, and Net Enthalpies of Combustion": {
#             "DATABOOK-ID": 1,
#             "TABLE-ID": 2,
#             "DESCRIPTION": "This table provides the ideal gas enthalpies of formation (EnFo_IG) in J/kmol, ideal gas Gibbs energies of        
# formation (GiEnFo_IG) in J/kmol, entropies (Ent_IG) in J/kmol.K, and standard net enthalpies of combustion (EnCo_STD) in J/kmol."
#         },
#         ...
#     }
# }
```

### How to list all databooks

List all databooks in the app.

```python
# databook list
# res_format can be 'json', 'dataframe', 'list' or 'dict'
db_list = tdb.list_databooks(res_format='json')
# log
print(db_list)

# {
#     "databook-1": "Perry's Chemical Engineers' Handbook",
#     "databook-2": "Chemical Thermodynamics for Process Simulation",
#     "databook-3": "Chemical and Engineering Thermodynamics",
#     "databook-4": "CO2 Hydrogenation Reaction"
# }
```

### Databook Id

Databook id can be used to access a databook in the app.

```python
# databook name
databook_name = "Perry's Chemical Engineers' Handbook"
# get databook id
db_id = tdb.get_databook_id(databook_name, res_format='dict')
# log
print(db_id)

# {'databook_id': '2'}
```

## Tables

### List tables in a databook

List all tables available in a databook.

```python
# databook name or id
databook_name = 'Chemical Thermodynamics for Process Simulation'
# show all the table list
tb_lists = tdb.list_tables(databook_name, res_format='json')
# log
print(tb_lists)

# {
#     "table-1": "Table A.1 General data for selected compounds",
#     "table-2": "Table A.2 Vapor pressure correlations for selected compounds",
#     "table-3": "Table A.3 Liquid density correlations for selected compounds",
#     "table-4": "Table A.4 Enthalpy of vaporization correlations for selected compounds",
#     "table-5": "Table A.5 Liquid heat capacity correlations for selected compounds"
# }
```

### Table Info

A table type can be data, matrix-data, equation, or matrix-equation.

```python
# databook name or id
databook_name = 'Chemical Thermodynamics for Process Simulation'
# table name or id
table_name = 'Table A.1 General data for selected compounds'
# show table info
tb_info = tdb.table_info(databook_name, table_name, res_format='dict')
# log
print(tb_info)

# {
#     'Table Name': 'Table A.1 General data for selected compounds',
#     'Type': 'Data',
#     'Equations': 0,
#     'Data': 1,
#     'Matrix-Equations': 0,
#     'Matrix-Data': 0
# }
```

### Table Id

Table id can be used to access a table in a databook.

```python
# databook name
databook_name = 'Chemical Thermodynamics for Process Simulation'
# table name
table_name = 'Table A.1 General data for selected compounds'
# get table id
tb_id = tdb.get_table_id(databook_name, table_name, res_format='dict')
# log
print(tb_id)

# {'table_id': '3'}
```

### Table Data Structure

Show the table content including thermodynamic property, symbol, unit, and conversion factor.

```python
# databook name or id
databook_name = 'Chemical Thermodynamics for Process Simulation'
# table name or id
table_name = 1
# load data to check
data_table = tdb.data_load(databook_name, table_name)
# log
print(data_table.data_structure())

#                                COLUMNS     SYMBOL     UNIT CONVERSION  ID
# 0                                  No.       None     None       None   1
# 1                                 Name       None     None       None   2
# 2                 critical-temperature         Tc        K          1   3
# 3                    critical-pressure         Pc      bar          1   4
# 4                critical-molar-volume         Vc  cm3/mol          1   5
```

### Equation Table Structure

The equation structure consists of id, body, params, args, and returns.

```python
# databook name or id
databook_name = 'Chemical Thermodynamics for Process Simulation'
# table name or id
table_name = 2
# load equation to check
vapor_pressure_tb = tdb.equation_load(databook_name, table_name)
# log
print(vapor_pressure_tb.eq_structure(1))

# {
#     "id": 1,
#     "body":"",
#     "params": {},
#     "args": {},
#     "returns": {},
#     "custom_integral": {},
#     "body-integral": {},
#     "body-first-derivative": {},
#     "body-second-derivative": {}
# }
```

## Check Component Availability

Check a component availability in the selected databook and table, databook and tables are defined by name or id, and return a dictionary.

```python
# component name
component_name = "carbon Dioxide"

# databook id
databook_id = 1
# table id
table_id = 2
# check component availability
check_availability = tdb.check_component(component_name, databook_id, table_id)
# log
print(check_availability)

# {
#     "databook_id": 1,
#     "table_id": 2,
#     "component_name": "carbon Dioxide",
#     "availability": true
# }

# databook name
databook_name = 'Chemical Thermodynamics for Process Simulation'
# table name
table_name = "Table A.1 General data for selected compounds"

# check component
check_availability = tdb.check_component(component_name, databook_name, table_name)
print(check_availability)

# {
#     "databook_id": 2,
#     "table_id": 1,
#     "component_name": "carbon Dioxide",
#     "availability": true
# }
```

## How to Build a ThermoDB

## Build Data

Build a thermodb for a component consists of the follow:

```python
# component name
component_name = "carbon Dioxide"
# databook name 
databook_name = 'Chemical Thermodynamics for Process Simulation'
# table name
table_name = "Table A.1 General data for selected compounds"
# build data
component_data = tdb.build_data(component_name, databook_name, table_name)
# log
print(component_data.data_structure())

#                              COLUMNS     SYMBOL     UNIT CONVERSION  ID
# 0                                  No.       None     None       None   1
# 1                                 Name       None     None       None   2
# 2                 critical-temperature         Tc        K          1   3
# 3                    critical-pressure         Pc      bar          1   4
# 4                critical-molar-volume         Vc  cm3/mol          1   5
```

### Access Data

```python
# by ID
print(component_data.get_property(12))

# {'value': '-394380', 'unit': 'J/mol', 'symbol': 'GiEnFo_IG', 'property_name': 'standard-Gibbs-energy-of-formation', 'message': 'No message'}

# by property name
print(component_data.get_property('standard-Gibbs-energy-of-formation'))

# {'value': '-394380', 'unit': 'J/mol', 'symbol': 'GiEnFo_IG', 'property_name': 'standard-Gibbs-energy-of-formation', 'message': 'No message'}

# by symbol
print(component_data.get_property('GiEnFo_IG'))

# {'value': '-394380', 'unit': 'J/mol', 'symbol': 'GiEnFo_IG', 'property_name': 'standard-Gibbs-energy-of-formation', 'message': 'No message'}

# Tc [K]
critical_temperature = float(component_data.get_property('Tc')['value'])
# log
print(critical_temperature)
# 304.128

# Pc [bar]
critical_pressure = float(component_data.get_property('Pc')['value'])
# log
print(critical_pressure)
# 73.773

# MW [g/mol]
molecular_weight = float(component_data.get_property('MW')['value'])
# log
print(molecular_weight)
# 44.009
```

## Build Equation

Build an equation block for a component

```python
# build an equation

# component name
component_name = "carbon dioxide"
# databook name
databook_name = "Chemical Thermodynamics for Process Simulation"
# table name
table_name = "Table A.2 Vapor pressure correlations for selected compounds"
# vapor pressure
eq = tdb.build_equation(component_name, databook_name, table_name)


# args
print(eq.args)
# parameters
print(eq.parms)
# return
print(eq.returns)
# body
print(eq.body)
# execute equation
res = eq.cal(T=253.15, Tc=73.773, Pc=44.009)
print(res)

# liquid density
rho_eq = tdb.build_equation(comp1, "Chemical Thermodynamics for Process Simulation",
                            "Table A.3 Liquid density correlations for selected compounds")
# execute equation
pp(rho_eq.cal(T=298.15, Tc=CO2_Tc))

# enthalpy of vaporization
Hvap_eq = tdb.build_equation(comp1, "Chemical Thermodynamics for Process Simulation",
                             "Table A.4 Enthalpy of vaporization correlations for selected compounds")
# parms
print('enthalpy of vaporization', Hvap_eq.cal(T=298.15, Tc=CO2_Tc, MW=CO2_MW))

# liquid heat capacity
# databook name
databook_name = "Chemical Thermodynamics for Process Simulation"
# table name
table_name = "Table A.5 Liquid heat capacity correlations for selected compounds"
# build an equation
Cp_eq = tdb.build_equation(component_name, databook_name, table_name)

# log
print(Cp_eq.eq_id)

# 1

# args
print(Cp_eq.args)

# {
#     'temperature': {'name': 'temperature', 'symbol': 'T', 'unit': 'K'},
#     'critical_temperature': {'name': 'critical temperature', 'symbol': 'Tc', 'unit': 'K'},
#     'molecular_weight': {'name': 'molecular weight', 'symbol': 'MW', 'unit': 'g/mol'}
# }

print(Cp_eq.arg_symbols)

# {
#     'T': {'name': 'temperature', 'symbol': 'T', 'unit': 'K'},
#     'Tc': {'name': 'critical temperature', 'symbol': 'Tc', 'unit': 'K'},
#     'MW': {'name': 'molecular weight', 'symbol': 'MW', 'unit': 'g/mol'}
# }

# parms
print(Cp_eq.parms)

# {
#     'A': {'name': 'A', 'symbol': 'A', 'unit': 'None', 'conversion': 1},
#     'B': {'name': 'B', 'symbol': 'B', 'unit': 'None', 'conversion': 1},
#     'C': {'name': 'C', 'symbol': 'C', 'unit': 'None', 'conversion': 1},
#     'D': {'name': 'D', 'symbol': 'D', 'unit': 'None', 'conversion': 1},
#     'E': {'name': 'E', 'symbol': 'E', 'unit': 'None', 'conversion': 1},
#     'F': {'name': 'F', 'symbol': 'F', 'unit': 'None', 'conversion': 1},
#     'R': {'name': 'universal gas constant', 'symbol': 'R', 'unit': 'None', 'conversion': 1}
# }

# return
print(Cp_eq.returns)

# {'liquid_heat_capacity': {'name': 'liquid heat capacity', 'symbol': 'Cp_LIQ', 'unit': 'J/g.K'}}

# body
print(Cp_eq.body)

# Tau = 1 - (args['T']/args['Tc']);A = parms['A']/Tau;B = parms['B'];C = parms['C']*Tau;D = parms['D']*math.pow(Tau,2);E =
# parms['E']*math.pow(Tau,3);F = parms['F']*math.pow(Tau,4);res = (parms['R']*(A+B+C+D+E+F))/args['MW']


# execute equation
# CO2_Tc
CO2_Tc = 304.128
CO2_MW = 44.009
# log
print('liquid heat capacity', Cp_eq.cal(T=253.15, Tc=CO2_Tc, MW=CO2_MW))

# liquid heat capacity
# {'value': 2.1653, 'name': 'liquid heat capacity', 'symbol': 'Cp_LIQ', 'unit': 'J/g.K', 'message': 'No message'}
```