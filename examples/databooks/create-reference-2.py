# import libs
import os
from rich import print
# locals
from pyThermoDB.references import load_reference_from_str
from pyThermoDB.references.reference_maker import ReferenceMaker, insert_data_to_reference_tables

# ! reference
from examples.databooks.reference import REFERENCE_CONTENT


# SECTION: create reference content
# NOTE: ideal-gas-heat-capacity
# COLUMNS: [No.,Name,Formula,State,a0,a1,a2,a3,a4,R,Eq]
# VALUES:
# - [1,'carbon dioxide','CO2','g',3.259,1.356,1.502,-2.374,1.056,8.314,1]
CO2_dt_1 = [1, 'carbon dioxide', 'CO2', 'g',
            3.259, 1.356, 1.502, -2.374, 1.056, 8.314, 1]
CO_dt_1 = [2, 'carbon monoxide', 'CO', 'g',
           3.912, -3.913, 1.182, -1.302, 0.515, 8.314, 1]


# NOTE: general-data
# COLUMNS: [No.,Name,Formula,State,Molecular-Weight,Critical-Temperature,Critical-Pressure,Critical-Molar-Volume,Critical-Compressibility-Factor,Acentric-Factor,Enthalpy-of-Formation,Gibbs-Energy-of-Formation]
# VALUES:
# - [1,'carbon dioxide','CO2','g',44.01,304.21,7.383,0.094,0.274,0.2236,-393.5,-394.4]
CO2_dt_2 = [1, 'carbon dioxide', 'CO2', 'g', 44.01,
            304.21, 7.383, 0.094, 0.274, 0.2236, -393.5, -394.4]
CO_dt_2 = [2, 'carbon monoxide', 'CO', 'g', 28.01,
           132.92, 3.499, 0.0944, 0.299, 0.0482, -110.5, -137.2]

# NOTE: table data
# ideal-gas-heat-capacity
ideal_gas_heat_capacity_data = [
    [1, 'carbon dioxide', 'CO2', 'g', 3.259,
        1.356, 1.502, -2.374, 1.056, 8.314, 1],
    [2, 'carbon monoxide', 'CO', 'g', 3.912, -
        3.913, 1.182, -1.302, 0.515, 8.314, 1],
    [3, 'hydrogen', 'H2', 'g', 2.883, 3.681, -0.772, 0.692, -0.213, 8.314, 1]
]
# general-data
general_data = [
    [1, 'carbon dioxide', 'CO2', 'g', 44.01, 304.21,
        7.383, 0.094, 0.274, 0.2236, -393.5, -394.4],
    [2, 'carbon monoxide', 'CO', 'g', 28.01, 132.92,
        3.499, 0.0944, 0.299, 0.0482, -110.5, -137.2],
    [3, 'hydrogen', 'H2', 'g', 2.016, 33.19, 1.313, 0.064147, 0.305, -0.216, 0, 0]
]
# vapor-pressure
vapor_pressure_data = [
    [1, 'carbon dioxide', 'CO2', 'g', 140.54, -4735, -21.268,
        4.09E-02, 1, 216.58, 5.19E+05, 304.21, 7.39E+06, 1],
    [2, 'carbon monoxide', 'CO', 'g', 45.698, -1076.6, -4.8814,
        7.57E-05, 2, 68.15, 1.54E+04, 132.92, 3.49E+06, 1],
    [3, 'hydrogen', 'H2', 'g', 12.69, -94.9, 1.1125,
        3.29E-04, 2, 13.95, 7.21E+03, 33.19, 1.32E+06, 1]
]
# liquid-heat-capacity
liquid_heat_capacity_data = [
    [1, 'acetic acid', 'C2H4O2', 'l', 4.375, -
        2.397, 6.757, -8.764, 3.478, 8.314, 1],
    [2, 'ethanol', 'C2H6O', 'l', 4.396, 0.628, 5.546, -7.024, 2.685, 8.314, 1],
    [3, 'water', 'H2O', 'l', 4.395, -4.186, 1.405, -1.564, 0.632, 8.314, 1],
    [4, 'ethyl acetate', 'C4H8O2', 'l', 10.228, -
        14.948, 13.033, -15.736, 5.999, 8.314, 1]
]
# enthalpy-of-vaporization
enthalpy_of_vaporization_data = [
    [1, 'water', 'H2O', 'l', 6.853064, 7.437940, -
        2.937398, -3.282184, 8.396833, 647.096, 8.314, 1],
    [2, 'ammonia', 'NH3', 'g', 5.744770, 7.282878, -
        2.428749, -2.261923, 2.909393, 405.500, 8.314, 1],
    [3, 'hydrogen chloride', 'HCl', 'g', 5.385594, 3.577607,
        1.702220, -4.769082, 5.095527, 324.550, 8.314, 1]
]

tables_data = {
    'ideal-gas-heat-capacity': ideal_gas_heat_capacity_data,
    'general-data': general_data,
    'vapor-pressure': vapor_pressure_data,
    'liquid-heat-capacity': liquid_heat_capacity_data,
    # 'enthalpy-of-vaporization': enthalpy_of_vaporization_data
}

# SECTION: insert data to reference tables
# NOTE: insert data to reference tables
res = insert_data_to_reference_tables(
    reference=REFERENCE_CONTENT,
    databook_name='CUSTOM-REF-1',
    tables_data=tables_data,
    mode='log'
)
print("Data insertion results:")
print(res)
