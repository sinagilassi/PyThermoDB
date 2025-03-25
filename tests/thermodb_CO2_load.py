# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp
import os
from rich import print

# ====================================
# LOAD THERMODB
# ====================================
# ref
thermodb_file = 'Carbon Dioxide.pkl'
thermodb_path = os.path.join(os.getcwd(), 'tests', thermodb_file)
print(thermodb_path)

# ====================================
# LOAD THERMODB
# ====================================
# load thermodb
CO2_thermodb = ptdb.load_thermodb(thermodb_path)
print(type(CO2_thermodb))

# ====================================
# CHECK THERMODB
# ====================================
# check all properties and functions registered
print(CO2_thermodb.check())

# ====================================
# DATA
# ====================================
# list all data
print(CO2_thermodb.check_properties())

# ! load data
CO2_general = CO2_thermodb.check_property('general')
print(type(CO2_general))
# heat of formation at 298.15K
print(CO2_general.data_structure())
# raw result
CO2_dHf_IG = CO2_general.get_property(11)
# print(CO2_general.get_property(11, dataframe=True))
CO2_dHf_IG = float(CO2_general.get_property(11)['value'])
# by name
# print(CO2_general.get_property('dHf_IG', dataframe=True))
CO2_dHf_IG = float(CO2_general.get_property('dHf_IG')['value'])
CO2_dHf_IG_unit = CO2_general.get_property('dHf_IG')['unit']
CO2_dHf_IG_J__mol = CO2_dHf_IG*1000
print(f'CO2_dHf_IG = {CO2_dHf_IG} {
      CO2_dHf_IG_unit}, {CO2_dHf_IG_J__mol} J/mol')
# Gibbs free energy of formation at 298.15 K
CO2_dGf_IG = float(CO2_general.get_property('dGf_IG')['value'])
print(f'CO2_dGf_IG = {CO2_dGf_IG}')

# ====================================
# EQUATIONS
# ====================================
# list all functions
print(CO2_thermodb.check_functions())

# ! equation 1
CO2_Cp_eq = CO2_thermodb.check_function('heat-capacity')
# args
print(CO2_Cp_eq.args)
# return
print(CO2_Cp_eq.returns)
# parms values
print(CO2_Cp_eq.parms_values)
# cal
CO2_Cp_cal = CO2_Cp_eq.cal(T=298.15)
print(f'CO2_Cp_cal = {CO2_Cp_cal}')

# calculate dH at 320
CO2_Cp_integral = CO2_Cp_eq.cal_integral(T1=298.15, T2=320)
print(f'CO2_Cp_integral = {CO2_Cp_integral}')

# enthalpy at 320 K
CO2_Cp_enthalpy = (CO2_dHf_IG_J__mol + CO2_Cp_integral)/1000
print(f'CO2_Cp_enthalpy = {CO2_Cp_enthalpy}')

# ! equation 2
CO2_VaPr_eq = CO2_thermodb.check_function('vapor-pressure')
# args
print(CO2_VaPr_eq.args)
# return
print(CO2_VaPr_eq.returns)
# parms values
print(CO2_VaPr_eq.parms_values)
# cal
CO2_VaPr_cal = CO2_VaPr_eq.cal(T=304.21)
print(f'CO2_VaPr_cal = {CO2_VaPr_cal}')
