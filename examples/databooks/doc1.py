# import libs
import os
from rich import print
from pyThermoDB.references import ThermoDatabook

# SECTION: create a new databook instance
databook = ThermoDatabook("CO2 Hydrogenation")

# SECTION: sources
# current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Current directory: {current_dir}")

# NOTE: csv file path
# ! general data
general_data = os.path.join(current_dir, "General Data.csv")
print(f"General data file: {general_data}")

# add general data table
databook.add_data_table(
    "General Data",
    general_data,
    description="General data for CO2 hydrogenation process."
)

# get the table by name
general_data_table = databook.tables["General Data"]
print(f"General Data Table: {general_data_table}")
# description of the table
print(f"Description: {general_data_table.description}")

# ! vapor pressure equation
vapor_pressure_equation = os.path.join(current_dir, "Vapor Pressure.csv")
print(f"Vapor Pressure file: {vapor_pressure_equation}")

# equation body
equation_body = "f([vapor-pressure, VaPr, Pa] | [Temperature, T, K] | C1, C2, C3, C4, C5) = math.exp(C1 + C2/T + C3*math.log(T) + C4*(T**C5))"

# add vapor pressure equation table
databook.add_equation_table(
    table_name="Vapor Pressure",
    data=vapor_pressure_equation,
    equations=equation_body,
    description="Vapor pressure equation for CO2 hydrogenation process."
)

# SECTION: build the databook
databook.build()
# databook
print(f"Databook built with ID: {databook.databook_id}")
# print the databook
print(f"Databook Description: {databook.description}")
# contents of the databook
databook_contents = databook.get_contents(res_format='yml')
print(f"Databook Contents: {databook_contents}")

# save the contents to a file
output_file = os.path.join(current_dir, "CO2_Hydrogenation_Databook.yml")
databook.save_contents(output_file, res_format='yml')
