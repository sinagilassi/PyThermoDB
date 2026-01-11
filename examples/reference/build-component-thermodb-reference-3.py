# import packages/modules
from typing import Dict, List, Any
import os
from rich import print
import pyThermoDB as ptdb
from pyThermoDB.core import TableData, TableEquation, TableMatrixData
from pyThermoDB.references import ReferenceConfig
from pyThermoDB.thermodbX import check_and_build_component_thermodb, CustomReferenceSource, CustomReference
from pythermodb_settings.models import Component

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
yml_file = 'str-ref-1.yml'
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
ref: CustomReference = {'reference': [yml_path]}

# ?===========================================================
# SECTION: BUILD COMPONENT THERMODB
# ?===========================================================
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
CO2:
  heat-capacity:
    databook: CUSTOM-REF-1
    table: Ideal-Gas-Molar-Heat-Capacity
    symbol: Cp_IG
  vapor-pressure:
    databook: CUSTOM-REF-1
    table: vapor-Pressure
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

# ?===========================================================
# SECTION: Using build_component_thermodb
# ?===========================================================
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

# ?===========================================================
# SECTION: Using check_and_build_component_thermodb
# ?===========================================================
# NOTE: create CustomReferenceSource
custom_reference_source = CustomReferenceSource(
    reference=ref,
    config=reference_config
)


# ! (by component and Formula-State)
print("[bold magenta]By Component and Formula-State with no ignore[/bold magenta]")
thermodb_component_ = check_and_build_component_thermodb(
    component=CO2_component,
    reference_source=custom_reference_source,
    component_key='Formula-State'
)
# >> check
if thermodb_component_:
    #  check
    print(f"check: {thermodb_component_.thermodb.check()}")
    print(f"message: {thermodb_component_.thermodb.message}")

# ! (by component and Name-State)
print("[bold magenta]By Component and Name-State with no ignore[/bold magenta]")
thermodb_component_ = check_and_build_component_thermodb(
    component=CO2_component,
    reference_source=custom_reference_source,
    component_key='Name-State'
)
# >> check
if thermodb_component_:
    #  check
    print(f"check: {thermodb_component_.thermodb.check()}")
    print(f"message: {thermodb_component_.thermodb.message}")

# ! (by component and Name)
print("[bold magenta]By Component and Name with ignore[/bold magenta]")
thermodb_component_ = check_and_build_component_thermodb(
    component=CO2_component,
    reference_source=custom_reference_source,
    component_key='Name-State',
    ignore_state_props=['VaPr'],
)
# >> check
if thermodb_component_:
    #  check
    print(f"check: {thermodb_component_.thermodb.check()}")
    print(f"message: {thermodb_component_.thermodb.message}")

# ! (by component and Formula)
print("[bold magenta]By Component and Formula with ignore[/bold magenta]")
thermodb_component_ = check_and_build_component_thermodb(
    component=CO2_component,
    reference_source=custom_reference_source,
    component_key='Formula-State',
    ignore_state_props=['VaPr'],
)
# >> check
if thermodb_component_:
    #  check
    print(f"check: {thermodb_component_.thermodb.check()}")
    print(f"message: {thermodb_component_.thermodb.message}")

# ! vapor pressure state enforced to check
# print("[bold magenta]By Component and Formula without ignore[/bold magenta]")
# thermodb_component_ = check_and_build_component_thermodb(
#     component=CO2_component,
#     reference_config=reference_config,
#     custom_reference=ref,
#     component_key='Formula-State',
# )
# #  check
# print(f"check: {thermodb_component_.check()}")
# print(f"message: {thermodb_component_.message}")

# ====================================
# SECTION: SELECT PROPERTY
# ====================================
# ! >> check
if not thermodb_component_:
    raise ValueError("thermodb_component_ is None")

# NOTE: get CompBuilder
thermodb_component_ = thermodb_component_.thermodb

# select a property
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
# SAVE THERMODB
# ====================================
thermodb_file = thermodb_component_.thermodb_name or 'thermodb_component'

# save (pkl format)
res_ = thermodb_component_.save(thermodb_file, file_path=parent_dir)
print(f"ThermoDB saved: {res_}")
