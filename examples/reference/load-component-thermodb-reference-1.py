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
comp_thermodb = os.path.join(parent_dir, f"{component_id}.pkl")
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
# select a property
prop1_ = component_thermodb.select('general')
# check
if not isinstance(prop1_, TableData):
    raise TypeError("Not TableData")
# type
print(type(prop1_))
print(prop1_.prop_data)

# get all data
all_tb_data = prop1_.table_values
# to array
size_bytes = len(pickle.dumps(all_tb_data))
print(size_bytes, "bytes")
# bytes to KB
print(size_bytes / 1024, "KB")
# bytes to MB
print(size_bytes / (1024 ** 2), "MB")

# old format
print(prop1_.get_property('MW'))

# new format
_src = 'general | MW'
print(component_thermodb.retrieve(_src, message="molecular weight"))

# ====================================
# SELECT A FUNCTION
# ====================================
# select function
func1_ = component_thermodb.select_function('heat-capacity')
print(type(func1_))
print(func1_.args)
print(func1_.cal(T=295.15, message="heat capacity result"))

# select function
func2_ = component_thermodb.select_function('vapor-pressure')
print(type(func2_))
print(func2_.args)
print(func2_.cal(T=295.15, message="vapor pressure result"))
