# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp
import os

# ====================================
# LOAD THERMODB
# ====================================
# ref
thermodb_file = 'Carbon Dioxide.pkl'
thermodb_path = os.path.join(os.getcwd(), thermodb_file)
pp(thermodb_path)


# load thermodb
CO2_thermodb = ptdb.load_thermodb(thermodb_path)
pp(type(CO2_thermodb))

# load data
pp(CO2_thermodb.check_properties())

CO2_general = CO2_thermodb.check_property('general')
pp(type(CO2_general))
pp(CO2_general.get_property(
    'dHf_IG')['value'])
