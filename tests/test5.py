# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp
import os

# ====================================
# LOAD THERMODB
# ====================================
# ref
thermodb_file = 'Acetaldehyde-2.pkl'
thermodb_path = os.path.join(os.getcwd(), thermodb_file)
pp(thermodb_path)


# load thermodb
Acetaldehyde_thermodb = ptdb.load_thermodb(thermodb_path)
pp(type(Acetaldehyde_thermodb))

# load data
pp(Acetaldehyde_thermodb.check_properties())

Acetaldehyde_general = Acetaldehyde_thermodb.check_property('general')
pp(type(Acetaldehyde_general))
pp(Acetaldehyde_general.prop_data)
pp(Acetaldehyde_general.get_property(
    'Standard Enthalpy of Formation')['value'])

# load equation
Acetaldehyde_equation = Acetaldehyde_thermodb.check_function('heat-capacity')
pp(type(Acetaldehyde_equation))
# cal
Cp_cal = Acetaldehyde_equation.cal(T=290)
pp(Cp_cal)
