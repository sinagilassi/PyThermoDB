# import packages/modules
import os
import pyThermoDB as ptdb

# version
print(ptdb.__version__)

# ===============================
# CREATE CUSTOM REFERENCE
# ===============================
# files
yml_file = 'tests\\CO2 Hydrogenation.yml'
yml_path = os.path.join(os.getcwd(), yml_file)

csv_file_1 = 'tests\\The Molar Heat Capacities of Gases in the Ideal Gas (Zero-Pressure) State.csv'
csv_file_2 = 'tests\\General Data.csv'
csv_path_1 = os.path.join(os.getcwd(), csv_file_1)
csv_path_2 = os.path.join(os.getcwd(), csv_file_2)

# custom ref
custom_ref = {'reference': [yml_path], 'tables': [csv_path_1, csv_path_2]}

# ===============================
# CHECKING THE REFERENCE
# ===============================
# init
ref = ptdb.ref(custom_ref)

# extract information
# list databooks
print(ref.list_databooks())
# list tables
print(ref.list_tables(7))
# load table
print(ref.load_table(7, 2))
# search table
print(ref.search_table(7, 2, "Formula", "CO2"))
# search table (query)
print(ref.search_table(7, 2, ["Formula", "State"], ["CO2", "g"]))
