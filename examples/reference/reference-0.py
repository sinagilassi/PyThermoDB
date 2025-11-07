# import packages/modules
from typing import Dict, List, Any
import os
from rich import print
import pyThermoDB as ptdb
from pyThermoDB.core import TableData, TableEquation, TableMatrixData
from pyThermoDB.core import TableUtil

# versions
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
# ====================================
# parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))

# files
# SECTION:
yml_file = 'reference-1.yml'
yml_path = os.path.join(parent_dir, yml_file)

# SECTION:
md_file = 'reference-1.md'
md_path = os.path.join(parent_dir, md_file)

# SECTION: file contents
file_contents = """

"""

# NOTE: custom ref
# ref: Dict[str, Any] = {'reference': [file_contents]}
# md ref
# ref = {'reference': [md_path]}
# yml ref
ref: Dict[str, Any] = {'reference': [yml_path]}


# SECTION: load custom reference
# ====================================
# INITIALIZATION OWN THERMO DB
# ====================================
thermo_db = ptdb.init(custom_reference=ref)

# ====================================
# GET DATABOOK LIST
# ====================================
db_list = thermo_db.list_databooks()
print(db_list)

# ====================================
# SELECT A DATABOOK
# ====================================
# table list
tb_list = thermo_db.list_tables('CUSTOM-REF-1')
print(tb_list)

# ====================================
# SELECT A TABLE
# ====================================
# table data
# ! (all data)
table_data = thermo_db.table_data(
    'CUSTOM-REF-1',
    'general-data'
)
print(table_data)

# table structure
# ! (only structure)
res_ = thermo_db.data_table_structure(
    'CUSTOM-REF-1',
    'general-data'
)
print(res_)

# ! (table equations)
eq_str_res_ = thermo_db.equation_table_structure(
    'CUSTOM-REF-1',
    'vapor-pressure'
)
# >> check
if eq_str_res_ is None:
    raise ValueError("No equation table structure found!")

print(eq_str_res_)

# >> symbol
eq_str_symbols = eq_str_res_.get('SYMBOL')
# >> check
if eq_str_symbols is None:
    raise ValueError("No equation table symbols found!")

print(eq_str_symbols)

# ====================================
# SELECT A COMPONENT
# ====================================

# NOTE: select a component
comp1 = "Carbon Dioxide"

# ====================================
# BUILD DATA
# ====================================
# build data
comp1_data = thermo_db.build_data(
    comp1,
    'CUSTOM-REF-1',
    'general-data'
)
print(comp1_data.data_structure())

print(comp1_data.get_property(6, message=f"{comp1} Enthalpy of formation"))
# by symbol
print(comp1_data.get_property('gibbs-energy-of-formation')['value'])

# ====================================
# BUILD EQUATION
# ====================================
# build equation
vapor_pressure_eq = thermo_db.build_equation(
    comp1,
    'CUSTOM-REF-1',
    2
)

# NOTE: check variable range values
# ! get variable range availability
res_ = vapor_pressure_eq.get_variable_range_values()
print(res_)

# NOTE: extract data
print(vapor_pressure_eq.eq_structure())
print(vapor_pressure_eq.equation_args())
print(vapor_pressure_eq.equation_return())
print(vapor_pressure_eq.parms_values)
VaPr = vapor_pressure_eq.cal(message=f'{comp1} Vapor Pressure', T=304.21)
VaPr = vapor_pressure_eq.cal(T=304.21)
print(VaPr)

# args
VaPr_args = vapor_pressure_eq.arg_symbols
print(VaPr_args)
VaPr_args_2 = vapor_pressure_eq.get_arg_symbols()
print(VaPr_args_2)

# ====================================
# CALCULATION OVER RANGE
# ====================================
# calculate over range
Ts = [290.0, 300.0, 310.0, 320.0, 330.0]
VaPr_range = vapor_pressure_eq.cal_range(
    variable_id='T',
    variable_range_values=Ts,
    message=f'{comp1} Vapor Pressure over range',
    decimal_accuracy=3
)
print(VaPr_range)
