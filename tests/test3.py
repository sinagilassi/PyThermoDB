# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp
import os

# dir
# print(dir(pt))
# get versions
# print(pt.get_version())
print(ptdb.__version__)


# CUSTOM REFERENCES
# ===============================
# files
yml_file = 'tests\\ref1.yml'
yml_path = os.path.join(os.getcwd(), yml_file)

csv_file = 'tests\\csv1.csv'
csv_path = os.path.join(os.getcwd(), csv_file)


# custom ref
ref = {'yml': [yml_path], 'csv': [csv_path]}

# init
ptdb.init(ref)
