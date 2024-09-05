# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp
import os

# dir
# print(dir(pt))
# get versions
# print(pt.get_version())
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
# ====================================
# files
yml_file = 'tests\\ref1.yml'
yml_path = os.path.join(os.getcwd(), yml_file)

csv_file_1 = 'tests\\Table A.II The Molar Heat Capacities of Gases in the Ideal Gas (Zero-Pressure) State.csv'
csv_file_2 = 'tests\\Table A.IV Enthalpies and Gibbs Energies of Formation.csv'
csv_path_1 = os.path.join(os.getcwd(), csv_file_1)
csv_path_2 = os.path.join(os.getcwd(), csv_file_2)

# custom ref
ref = {'yml': [yml_path], 'csv': [csv_path_1, csv_path_2]}

# ====================================
# INITIALIZATION OWN THERMO DB
# ====================================
thermo_db = ptdb.init(ref)

# ====================================
# GET DATABOOK LIST
# ====================================
db_list = thermo_db.list_databooks()
print(db_list)

# ====================================
# SELECT A DATABOOK
# ====================================
# table list
tb_list = thermo_db.list_tables(3)
print(tb_list)

# ====================================
# DISPLAY TABLE INFO
# ====================================
# display a table
tb_info = thermo_db.table_info(3, 2)
print(tb_info)

# ====================================
# LOAD TABLE
# ====================================
# load equation
tb_eq = thermo_db.equation_load(3, 1)
# equation structure
tb_eq_structure = tb_eq.eq_structure(1)
pp(tb_eq_structure)

# ====================================
# CHECK COMPONENT AVAILABILITY IN A TABLE
# ====================================
# check component availability in the databook and table
comp1 = "carbon Dioxide"
COMP1_check_availability = thermo_db.check_component(comp1, 3, 2)

# ====================================
# BUILD DATA
# ====================================
# build data
comp1_data = thermo_db.build_data(comp1, 3, 2)
pp(comp1_data.data_structure())

pp(comp1_data.get_property(6))

# ====================================
# BUILD EQUATION
# ====================================
# build equation
comp1_eq = thermo_db.build_equation(comp1, 3, 1)
# args
pp(comp1_eq.args)

# variables
args = {
    "T": 290,
}
# cal
pp(comp1_eq.cal(args))
