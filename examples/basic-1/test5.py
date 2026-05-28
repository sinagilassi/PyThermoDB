# import packages/modules
import os
from rich import print
import pyThermoDB as ptdb
from pyThermoDB import (
    TableData,
    TableMatrixData,
    TableConstants,
    TableEquation,
    TableMatrixEquation
)

# ====================================
# LOAD THERMODB
# ====================================
# NOTE: parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))

# ref
pkl_dir = os.path.join(parent_dir, '..', 'thermodb')
thermodb_file = 'Acetaldehyde-3.pkl'
thermodb_path = os.path.join(os.getcwd(), 'tests', thermodb_file)
print(thermodb_path)


# load thermodb
Acetaldehyde_thermodb = ptdb.load_thermodb(thermodb_path)
print(type(Acetaldehyde_thermodb))

# load data
print(Acetaldehyde_thermodb.check_properties())

# check property
# method 1
# Acetaldehyde_general = Acetaldehyde_thermodb.check_property('general')

# method 2
Acetaldehyde_general: (
    TableData | TableMatrixData | TableConstants | TableEquation | TableMatrixEquation
) = Acetaldehyde_thermodb.select(
    'general')
print(type(Acetaldehyde_general))

# >> check type
if not isinstance(Acetaldehyde_general, TableData):
    raise TypeError(
        f'Expected Acetaldehyde_general to be of type TableData, but got {type(Acetaldehyde_general)}')

# access property
print(Acetaldehyde_general.prop_data)
print(Acetaldehyde_general.get_property('dHf_IG')['value'])

# load equation
Acetaldehyde_equation = Acetaldehyde_thermodb.check_function('heat-capacity')
print(type(Acetaldehyde_equation))

# cal
Cp_cal = Acetaldehyde_equation.cal(
    T=290,
    message='heat capacity of Acetaldehyde'
)
print(Cp_cal)
