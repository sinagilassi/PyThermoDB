# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp
import os
from rich import print

# ====================================
# LOAD THERMODB
# ====================================
# ref
thermodb_file = 'Acetaldehyde-3.pkl'
thermodb_path = os.path.join(os.getcwd(), 'tests', thermodb_file)
print(thermodb_path)


# load thermodb
Acetaldehyde_thermodb = ptdb.load_thermodb(thermodb_path)
print(type(Acetaldehyde_thermodb))

# load data
print(Acetaldehyde_thermodb.check_properties())

Acetaldehyde_general = Acetaldehyde_thermodb.check_property('general')
print(type(Acetaldehyde_general))
print(Acetaldehyde_general.prop_data)
# print(Acetaldehyde_general.get_property(
#     'dHf_IG')['value'])

# load equation
Acetaldehyde_equation = Acetaldehyde_thermodb.check_function('heat-capacity')
print(type(Acetaldehyde_equation))
# cal
Cp_cal = Acetaldehyde_equation.cal(
    T=290, message='heat capacity of Acetaldehyde')
print(Cp_cal)
