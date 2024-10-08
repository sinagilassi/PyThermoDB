# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp
import os

# ====================================
# LOAD THERMODB
# ====================================
# ref
thermodb_file = 'Carbon Dioxide-multiple-3.pkl'
# current dir
current_path = os.getcwd()
thermodb_path = os.path.join(os.getcwd(), 'tests', thermodb_file)
pp(thermodb_path)

# ====================================
# LOAD THERMODB
# ====================================
# load thermodb
CO2_thermodb = ptdb.load_thermodb(thermodb_path)
pp(type(CO2_thermodb))

# ====================================
# CHECK THERMODB
# ====================================
# check all properties and functions registered
pp(CO2_thermodb.check())

# ====================================
# DATA
# ====================================
# list all data
pp(CO2_thermodb.check_properties())

# ! load data
CO2_general = CO2_thermodb.check_property('GENERAL')
pp(type(CO2_general))
# heat of formation at 298.15K
CO2_dHf_IG = float(CO2_general.get_property('dHf_IG')['value'])
CO2_dHf_IG_unit = CO2_general.get_property('dHf_IG')['unit']
CO2_dHf_IG_J__mol = CO2_dHf_IG*1000
pp(f'CO2_dHf_IG = {CO2_dHf_IG} {CO2_dHf_IG_unit}, {CO2_dHf_IG_J__mol} J/mol')
# Gibbs free energy of formation at 298.15 K
CO2_dGf_IG = float(CO2_general.get_property('dGf_IG')['value'])
pp(f'CO2_dGf_IG = {CO2_dGf_IG}')

# ====================================
# EQUATIONS
# ====================================
# list all functions
pp(CO2_thermodb.check_functions())

# ! equation 1
CO2_Cp_eq = CO2_thermodb.check_function('heat-capacity')
# args
pp(CO2_Cp_eq.args)
# return
pp(CO2_Cp_eq.returns)
# parms values
pp(CO2_Cp_eq.parms_values)
# cal
CO2_Cp_cal = CO2_Cp_eq.cal(T=298.15)
pp(f'CO2_Cp_cal = {CO2_Cp_cal}')

# calculate dH at 320
CO2_Cp_integral = CO2_Cp_eq.cal_integral(T1=298.15, T2=320)
pp(f'CO2_Cp_integral = {CO2_Cp_integral}')

# enthalpy at 320 K
CO2_Cp_enthalpy = (CO2_dHf_IG_J__mol + CO2_Cp_integral)/1000
pp(f'CO2_Cp_enthalpy = {CO2_Cp_enthalpy}')

# ! equation 2
CO2_VaPr_eq = CO2_thermodb.check_function('vapor-pressure')
# args
pp(CO2_VaPr_eq.args)
# return
pp(CO2_VaPr_eq.returns)
# parms values
pp(CO2_VaPr_eq.parms_values)
# cal
CO2_VaPr_cal = CO2_VaPr_eq.cal(T=304.21)
pp(f'CO2_VaPr_cal = {CO2_VaPr_cal}')
