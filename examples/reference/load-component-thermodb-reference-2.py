# import packages/modules
from typing import Dict, List, Any
import numpy as np
import pickle
import os
from rich import print
import pyThermoDB as ptdb
from pyThermoDB.core import TableData, TableEquation, TableMatrixData
from pyThermoDB.references import ReferenceConfig
from pyThermoDB import check_and_build_component_thermodb
from pythermodb_settings.models import Component

# versions
print(ptdb.__version__)

# ====================================
# SECTION: DIRECTORY SETUP
# ====================================
# parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))

# ====================================
# SECTION: LOAD CUSTOM REFERENCE
# ====================================
# NOTE: create component identifier
component_name = 'carbon dioxide'
component_formula = 'CO2'
component_state = 'g'

# component id
component_id = f"{component_formula}-{component_state}"
print(f"component_id: {component_id}")

# component thermodb file path
comp_thermodb_file = 'carbon dioxide-g-nasa-1.pkl'
comp_thermodb = os.path.join(parent_dir, comp_thermodb_file)
print(f"comp_thermodb: {comp_thermodb}")

# ===============================
# SECTION: LOAD THERMODB COMPONENT
# ===============================
# load thermodb
component_thermodb = ptdb.load_thermodb(thermodb_file=comp_thermodb)
print(type(component_thermodb))

# NOTE: metadata
# ! build version
print("ThermoDB Build Version:", component_thermodb.build_version)
# ! build date
print("ThermoDB Build Date:", component_thermodb.build_date)
# ! python version
print("ThermoDB Build Python Version:", component_thermodb.build_python)

# NOTE: check
print(component_thermodb.check())

# ====================================
# SECTION: SELECT PROPERTY
# ====================================
# # select a property
# prop1_ = component_thermodb.select('general')
# # check
# if not isinstance(prop1_, TableData):
#     raise TypeError("Not TableData")
# # type
# print(type(prop1_))
# print(prop1_.prop_data)

# # get all data
# all_tb_data = prop1_.table_values
# # to array
# size_bytes = len(pickle.dumps(all_tb_data))
# print(size_bytes, "bytes")
# # bytes to KB
# print(size_bytes / 1024, "KB")
# # bytes to MB
# print(size_bytes / (1024 ** 2), "MB")

# # old format
# print(prop1_.get_property('MW'))

# # new format
# _src = 'general | MW'
# print(component_thermodb.retrieve(_src, message="molecular weight"))

# ====================================
# SELECT A FUNCTION
# ====================================
# select function
func1_ = component_thermodb.select_function('CUSTOM-REF-1::NASA9-MAX-1000-K')
print(type(func1_))
print(func1_.args)
print(func1_.parms)
print(func1_.parms_values)

# select function
func1_ = component_thermodb.select_function('CUSTOM-REF-1::NASA9-MIN-1000-K')
print(type(func1_))
print(func1_.args)
print(func1_.parms)
print(func1_.parms_values)

# - ["carbon dioxide", "CO2", "g", "CO2", 0, 44.0095, -393510, 200, 1000, 9365.469, 49437.8364, -626.429208, 5.30181336, 0.002503601, -2.12e-07, -7.69e-10, 2.85e-13, -45281.8986, -7.0487901, 1]
# - ["carbon dioxide", "CO2", "g", "CO2", 0, 44.0095, -393510, 1000, 6000, 9365.469, 117696.9434, -1788.801467, 8.29154353, -9.22e-05, 4.87e-09, -1.89e-12, 6.33e-16, -39083.4501, -26.52683962, 1]
