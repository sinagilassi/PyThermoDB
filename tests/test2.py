# import packages/modules
import os
import pyThermoDB as ptdb

# dir
# print(dir(pt))
# get versions
# print(pt.get_version())
print(ptdb.__version__)

# ===============================
# REFERENCE
# ===============================
# init
ref = ptdb.ref()

# extract information
# list databooks
print(ref.list_databooks())
# list tables
print(ref.list_tables(1))
# load table
print(ref.load_table(1, 1))
# search table
print(ref.search_table(1, 1, "Formula", "CO2"))

# ===============================
# CREATE CUSTOM REFERENCE
# ===============================
# files
yml_file = 'tests\\ref1.yml'
yml_path = os.path.join(os.getcwd(), yml_file)

csv_file_1 = 'tests\\Table A.II The Molar Heat Capacities of Gases in the Ideal Gas (Zero-Pressure) State.csv'
csv_file_2 = 'tests\\Table A.IV Enthalpies and Gibbs Energies of Formation.csv'
csv_path_1 = os.path.join(os.getcwd(), csv_file_1)
csv_path_2 = os.path.join(os.getcwd(), csv_file_2)

# custom ref
ref = {'yml': [yml_path], 'csv': [csv_path_1, csv_path_2]}
