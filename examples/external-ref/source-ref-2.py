# import packages/modules
import os
from rich import print
import pyThermoDB as ptdb

# get versions
# print(pt.get_version())
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
# ====================================
# files 1
yml_file_1 = 'examples\\external-ref\\source-ref-1.yml'
yml_path_1 = os.path.join(os.getcwd(), yml_file_1)
print(yml_path_1)

# files 2
yml_file_2 = 'examples\\external-ref\\source-ref-2.yml'
yml_path_2 = os.path.join(os.getcwd(), yml_file_2)
print(yml_path_2)

# custom ref
ref = {'reference': [yml_path_1, yml_path_2]}

# ====================================
# INITIALIZATION OWN THERMO DB
# ====================================
thermo_db = ptdb.init(custom_reference=ref)

# ====================================
# GET DATABOOK LIST
# ====================================
db_list = thermo_db.list_databooks()
print(db_list)

# ====================================
# SELECT A DATABOOK
# ====================================
# table list
tb_list = thermo_db.list_tables('CUSTOM-REF-1')
print(tb_list)

# ====================================
# DISPLAY TABLE INFO
# ====================================
# display a table
tb_info = thermo_db.table_info('CUSTOM-REF-1', 'General-Data')
print(tb_info)

# tb_info = thermo_db.table_info('CUSTOM-REF-1', 'Vapor-Pressure')
# print(tb_info)

# tb_info = thermo_db.table_info('CUSTOM-REF-1', 'Ideal-Gas-Molar-Heat-Capacity')
# print(tb_info)

# ====================================
# LOAD TABLE
# ====================================
# table-data
dt_ = thermo_db.data_load(
    1, 'TABLE 2-141 Critical Constants and Acentric Factors of Inorganic and Organic Compounds')
print(dt_.data_structure())
print(dt_.table_columns)
print(dt_.table_symbols)
print(dt_.table_units)
print(dt_.table_values)


# table-data
dt_ = thermo_db.data_load('CUSTOM-REF-2', 'General-Data')
print(dt_.data_structure())
print(dt_.table_columns)
print(dt_.table_symbols)
print(dt_.table_units)
print(dt_.table_values)

# table-equation
tb_eq = thermo_db.equation_load('CUSTOM-REF-1', 'Vapor-Pressure')
# equation structure
tb_eq_structure = tb_eq.eq_structure()
print(tb_eq_structure)
print(tb_eq.eqs_structure())
print(tb_eq.table_columns)
print(tb_eq.table_symbols)
print(tb_eq.table_units)
print(tb_eq.table_values)

# ===============================
# TABLE LOAD
# ===============================
# table load
res_ = thermo_db.table_data('CUSTOM-REF-1', 'Vapor-Pressure')
print(type(res_))
print(res_)

# res_ = thermo_db.table_view('CUSTOM-REF-1', 'Vapor-Pressure')

# ====================================
# CHECK COMPONENT AVAILABILITY IN A TABLE
# ====================================
# check component availability in the databook and table
# comp1 = "Carbon Dioxide"
comp1 = "toluene"
# COMP1_check_availability = thermo_db.check_component(comp1, 3, 2)

# query
# query = f"Name.str.lower() == '{comp1.lower()}' & State == 'g'"
# COMP1_check_availability = thermo_db.check_component(
#     comp1, 3, 2, query, query=True)


# ====================================
# BUILD DATA
# ====================================
# build data
data_1 = thermo_db.build_thermo_property(
    [comp1], 'CUSTOM-REF-2', 'General-Data')
print(type(data_1))

# retrieve data
res_ = data_1.get_property("MW")
print(res_)

# ====================================
# BUILD EQUATION
# ====================================
# ! build equation
comp1_eq_1 = thermo_db.build_thermo_property(
    [comp1], 'CUSTOM-REF-1', 'Vapor-Pressure')

# equation details
print(comp1_eq_1.equation_parms())
print(comp1_eq_1.equation_args())
print(comp1_eq_1.equation_body())
print(comp1_eq_1.equation_return())

# cal
res_ = comp1_eq_1.cal(T=290)
print(res_)

# ! build equation
# comp1_eq_2 = thermo_db.build_thermo_property(
#     [comp1], 'CUSTOM-REF-1', 'Ideal-Gas-Molar-Heat-Capacity')

# # equation details
# print(comp1_eq_2.equation_parms())
# print(comp1_eq_2.equation_args())
# print(comp1_eq_2.equation_body())
# print(comp1_eq_2.equation_return())

# # cal
# res_ = comp1_eq_2.cal(T=290)
# print(res_)

# ====================================
# BUILD THERMODB
# ====================================
# build a thermodb
thermo_db = ptdb.build_thermodb()
print(type(thermo_db))

# add TableData
thermo_db.add_data('general', data_1)
# add TableEquation
thermo_db.add_data('vapor-pressure', comp1_eq_1)
# add TableEquation
# thermo_db.add_data('heat-capacity', comp1_eq_2)
# add string
# thermo_db.add_data('dHf', {'dHf_IG': 152})
# export
# thermo_db.export_data_structure(comp1)

thermodb_file = f'{comp1}-3.pkl'
thermodb_path = os.path.join(
    os.getcwd(), 'examples', 'external-ref', 'thermodb')

# save
thermo_db.save(thermodb_file, file_path=thermodb_path)

# check
print(thermo_db.check())

# ====================================
# LOAD THERMODB
# ====================================
# load a thermodb
thermo_db_loaded = ptdb.load_thermodb(
    os.path.join(thermodb_path, thermodb_file))
print(type(thermo_db_loaded))

# check
print(thermo_db_loaded.check())

# ====================================
# SELECT PROPERTY
# ====================================
prop1_ = thermo_db_loaded.select('general')
print(type(prop1_))
print(prop1_.prop_data)

# old format
print(prop1_.get_property('MW'))

# new format
_src = 'general | MW'
print(thermo_db_loaded.retrieve(_src, message="molecular weight"))

# ====================================
# SELECT A FUNCTION
# ====================================
# select function
# func1_ = thermo_db_loaded.select_function('heat-capacity')
# print(type(func1_))
# print(func1_.args)
# print(func1_.cal(T=295.15, message="heat capacity result"))

# select function
func2_ = thermo_db_loaded.select_function('vapor-pressure')
print(type(func2_))
print(func2_.args)
print(func2_.cal(T=295.15, message="vapor pressure result"))
