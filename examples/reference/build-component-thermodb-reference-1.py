# import packages/modules
from typing import Dict, List, Any
import os
from rich import print
import pyThermoDB as ptdb
from pyThermoDB.core import TableData, TableEquation, TableMatrixData
from pyThermoDB.references import ReferenceConfig
from pyThermoDB import check_and_build_component_thermodb
from pyThermoDB.models import Component

# get versions
# print(pt.get_version())
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

print(vapor_pressure_eq.equation_args())
print(vapor_pressure_eq.equation_return())
VaPr = vapor_pressure_eq.cal(message=f'{comp1} Vapor Pressure', T=304.21)
VaPr = vapor_pressure_eq.cal(T=304.21)
print(VaPr)


# SECTION: build component thermodb for each component
# ====================================
# BUILD COMPONENT THERMODB
# ====================================
# property
reference_config = {
    'heat-capacity': {
        'databook': 'CUSTOM-REF-1',
        'table': 'Ideal-Gas-Molar-Heat-Capacity',
    },
    'vapor-pressure': {
        'databook': 'CUSTOM-REF-1',
        'table': 'vapor-pressure',
    },
    'general': {
        'databook': 'CUSTOM-REF-1',
        'table': 'general-data',
    },
}

# string
reference_config_yml = """
ALL:
  heat-capacity:
    databook: CUSTOM-REF-1
    table: Ideal-Gas-Molar-Heat-Capacity
    symbol: Cp_IG
  vapor-pressure:
    databook: CUSTOM-REF-1
    table: vapor-pressure
    symbol: VaPr
  general:
    databook: CUSTOM-REF-1
    table: general-data
    symbols:
      Pc: Pc
      Tc: Tc
      AcFa: AcFa
carbon dioxide:
  heat-capacity:
    databook: CUSTOM-REF-1
    table: XXX
    symbol: Cp_IG
  vapor-pressure:
    databook: CUSTOM-REF-1
    table: vapor-pressure
    symbol: VaPr
  general:
    databook: CUSTOM-REF-1
    table: general-data
    symbols:
      Pc: Pc
      Tc: Tc
      AcFa: AcFa
CO2-g:
  heat-capacity:
    databook: CUSTOM-REF-1
    table: XXX
    symbol: Cp_IG
  vapor-pressure:
    databook: CUSTOM-REF-1
    table: vapor-pressure
    symbol: VaPr
  general:
    databook: CUSTOM-REF-1
    table: general-data
    symbols:
      Pc: Pc
      Tc: Tc
      AcFa: AcFa
CO:
  heat-capacity:
    databook: CUSTOM-REF-1
    table: Ideal-Gas-Molar-Heat-Capacity
    symbol: Cp_IG
  vapor-pressure:
    databook: CUSTOM-REF-1
    table: Vapor-Pressure
    symbol: VaPr
  general:
    databook: CUSTOM-REF-1
    table: General-Data
    symbols:
      Pc: Pc
      Tc: Tc
      AcFa: AcFa
"""

# NOTE: convert reference config to dict
# reference_config = ReferenceConfig().set_reference_config(
#     reference_config=reference_config_yml
# )
# print(f"Reference Config: {reference_config}")

# no change
reference_config = reference_config_yml


# NOTE: build component thermodb
# ! (by name)
thermodb_component_ = ptdb.build_component_thermodb(
    component_name='carbon dioxide',
    reference_config=reference_config,
    custom_reference=ref
)

#  check
print(f"check: {thermodb_component_.check()}")
print(f"message: {thermodb_component_.message}")

# ! (by formula)
thermodb_component_ = ptdb.build_component_thermodb(
    component_name='CO2',
    reference_config=reference_config,
    custom_reference=ref,
    component_key='Formula'
)

#  check
print(f"check: {thermodb_component_.check()}")
print(f"message: {thermodb_component_.message}")

# NOTE: build component thermodb (by name) and check
CO2_component = Component(
    name='carbon dioxide',
    formula='CO2',
    state='g'
)

# ! (by component and Formula-State)
print("[bold magenta]By Component and Formula-State[/bold magenta]")
thermodb_component_ = ptdb.check_and_build_component_thermodb(
    component=CO2_component,
    reference_config=reference_config,
    custom_reference=ref,
    component_key='Formula-State'
)

#  check
print(f"check: {thermodb_component_.check()}")
print(f"message: {thermodb_component_.message}")

# ! (by component and Name-State)
print("[bold magenta]By Component and Name-State[/bold magenta]")
thermodb_component_ = ptdb.check_and_build_component_thermodb(
    component=CO2_component,
    reference_config=reference_config,
    custom_reference=ref,
    component_key='Name-State'
)

#  check
print(f"check: {thermodb_component_.check()}")
print(f"message: {thermodb_component_.message}")

# ! (by component and Name)
print("[bold magenta]By Component and Name[/bold magenta]")
thermodb_component_ = ptdb.check_and_build_component_thermodb(
    component=CO2_component,
    reference_config=reference_config,
    custom_reference=ref,
    ignore_state_props=['VaPr'],
)
#  check
print(f"check: {thermodb_component_.check()}")
print(f"message: {thermodb_component_.message}")

# ! (by component and Formula)
print("[bold magenta]By Component and Formula[/bold magenta]")
thermodb_component_ = ptdb.check_and_build_component_thermodb(
    component=CO2_component,
    reference_config=reference_config,
    custom_reference=ref,
    ignore_state_props=['VaPr'],
)
#  check
print(f"check: {thermodb_component_.check()}")
print(f"message: {thermodb_component_.message}")

# ====================================
# BUILD COMPONENTS THERMODB
# ====================================
# property
reference_config_2 = {
    'nrtl': {
        'databook': 'CUSTOM-REF-1',
        'table': "NRTL Non-randomness parameters-2"
    }
}

# build components thermodb
thermodb_components_ = ptdb.build_components_thermodb(
    component_names=['ethanol', 'methanol'],
    reference_config=reference_config_2,
    custom_reference=ref)
# check
print(thermodb_components_.check())
print(thermodb_components_.message)

# ====================================
# SELECT PROPERTY
# ====================================
prop1_ = thermodb_component_.select('general')
# check
if not isinstance(prop1_, TableData):
    raise TypeError("Not TableData")
# type
print(type(prop1_))
print(prop1_.prop_data)

# old format
print(prop1_.get_property('MW'))

# new format
_src = 'general | MW'
print(thermodb_component_.retrieve(_src, message="molecular weight"))

# ====================================
# SELECT A FUNCTION
# ====================================
# select function
func1_ = thermodb_component_.select_function('heat-capacity')
print(type(func1_))
print(func1_.args)
print(func1_.cal(T=295.15, message="heat capacity result"))

# select function
func2_ = thermodb_component_.select_function('vapor-pressure')
print(type(func2_))
print(func2_.args)
print(func2_.cal(T=295.15, message="vapor pressure result"))

# ====================================
# BUILD MATRIX DATA
# ====================================
# components
comp1 = "methanol"
comp2 = "ethanol"

components = [comp1, comp2]

# NOTE: build a matrix data
nrtl_alpha = thermodb_components_.select('nrtl')
# check
if not isinstance(nrtl_alpha, TableMatrixData):
    raise TypeError("Not TableMatrixData")

# matrix table
print(nrtl_alpha.matrix_table)
# matrix table
res_ = nrtl_alpha.get_matrix_table(mode='selected')
print(res_, type(res_))

# symbol
print(nrtl_alpha.matrix_symbol)

print(nrtl_alpha.matrix_data_structure())

# matrix data
print(nrtl_alpha.get_matrix_property(
    "a_i_j",
    [comp1, comp2],
    symbol_format='alphabetic',
    message="NRTL Alpha value")
)

print(nrtl_alpha.get_matrix_property(
    "b_i_j",
    [comp1, comp2],
    symbol_format='alphabetic',
    message="NRTL Alpha value")
)

# property name using ij method
prop_name = f"a_{comp1}_{comp2}"
print(prop_name)
res_1 = nrtl_alpha.ij(prop_name)
print(res_1)
print(res_1.get('value'))

# get property value using the matrix data
# format 1
# prop_name = f"dg_{comp1}_{comp2}"
# format 2
prop_name = f"a | {comp1} | {comp2}"
# get values
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='alphabetic')
print(prop_matrix, type(prop_matrix))

print("*" * 20)
prop_name = f"b | {comp1} | {comp2}"
# get values
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='alphabetic')
print(prop_matrix, type(prop_matrix))

print("*" * 20)
prop_name = f"c | {comp1} | {comp2}"
# get values
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='alphabetic')
print(prop_matrix, type(prop_matrix))
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='numeric')
print(prop_matrix, type(prop_matrix))
mat_ = nrtl_alpha.mat('c', [comp1, comp2])
print(mat_)
# get values
prop_name = f"c | {comp2} | {comp1}"
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='alphabetic')
print(prop_matrix, type(prop_matrix))
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='numeric')
print(prop_matrix, type(prop_matrix))
# ! ij matrix
mat_ = nrtl_alpha.mat('c', [comp2, comp1])
print(mat_)
print("*" * 20)

prop_name = f"alpha | {comp1} | {comp2}"
# get values
prop_matrix = nrtl_alpha.ijs(prop_name, res_format='alphabetic')
print(prop_matrix, type(prop_matrix))

# ! ij matrix
mat_ = nrtl_alpha.mat('alpha', [comp2, comp1])
print(mat_)
print("*" * 20)

# ====================================
# SAVE THERMODB
# ====================================
# thermodb_file = thermodb_component_.thermodb_name or 'thermodb_component'

# # save (pkl format)
# res_ = thermodb_component_.save(thermodb_file, file_path=parent_dir)
# print(f"ThermoDB saved: {res_}")

# multi-component
thermodb_file = thermodb_components_.thermodb_name or 'thermodb_component'

# save (pkl format)
res_ = thermodb_components_.save(thermodb_file, file_path=parent_dir)
print(f"ThermoDB saved: {res_}")
