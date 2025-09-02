# import packages/modules
import os
import pyThermoDB as ptdb

# version
print(ptdb.__version__)

# ===============================
# CREATE CUSTOM REFERENCE
# ===============================
# source dir
source_dir = os.path.join(os.getcwd(), 'examples', 'CO2 Hydrogenation')
# files
yml_file = 'CO2 Hydrogenation.yml'
yml_path = os.path.join(source_dir, yml_file)

csv_file_1 = 'The Molar Heat Capacities of Gases in the Ideal Gas (Zero-Pressure) State.csv'
csv_file_2 = 'General Data.csv'
csv_path_1 = os.path.join(source_dir, csv_file_1)
csv_path_2 = os.path.join(source_dir, csv_file_2)

# custom ref
custom_ref = {
    'reference': [yml_path],
    'tables': [csv_path_1, csv_path_2]
}

# ===============================
# CHECKING THE REFERENCE
# ===============================
# init
ref = ptdb.ref(custom_ref)

# extract information
# list databooks
print(ref.list_databooks())
# list tables
print(ref.list_tables(8))
# load table
print(ref.load_table(8, 2))
# search table
print(ref.search_table(8, 2, "Formula", "CO2"))
# search table (query)
print(ref.search_table(8, 2, ["Formula", "State"], ["CO2", "g"]))
