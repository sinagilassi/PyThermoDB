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
# files
yml_file = 'tests\\source-ref-1.yml'
yml_path = os.path.join(os.getcwd(), yml_file)

# custom ref
ref = {'reference': [yml_path]}

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
dt_ = thermo_db.data_load('CUSTOM-REF-1', 'General-Data')
print(dt_.data_structure())

# load equation
# tb_eq = thermo_db.equation_load('CUSTOM-REF-1', 'Vapor-Pressure')
# # equation structure
# tb_eq_structure = tb_eq.eq_structure()
# print(tb_eq_structure)

#
tb_eq = thermo_db.equation_load("Perry's Chemical Engineers' Handbook",
                                'TABLE 2-153 Heat Capacities of Inorganic and Organic Liquids')
# equation structure
tb_eq_structure = tb_eq.eq_structure()
print(tb_eq_structure)

# ====================================
# CHECK COMPONENT AVAILABILITY IN A TABLE
# ====================================
# check component availability in the databook and table
# comp1 = "Carbon Dioxide"
comp1 = "carbon dioxide"
# COMP1_check_availability = thermo_db.check_component(comp1, 3, 2)

# query
# query = f"Name.str.lower() == '{comp1.lower()}' & State == 'g'"
# COMP1_check_availability = thermo_db.check_component(
#     comp1, 3, 2, query, query=True)


# ====================================
# BUILD DATA
# ====================================
# # build data
# data_1 = thermo_db.build_thermo_property(
#     [comp1], 'CUSTOM-REF-1', 'General-Data')
# print(type(data_1))

# # retrieve data
# res_ = data_1.get_property("MW")
# print(res_)


# ====================================
# BUILD EQUATION
# ====================================
# build equation
comp1_eq = thermo_db.build_thermo_property(
    [comp1], 'CUSTOM-REF-1', 'Vapor-Pressure')

# equation details
print(comp1_eq.equation_parms())
print(comp1_eq.equation_args())
print(comp1_eq.equation_body())
print(comp1_eq.equation_return())

# cal
Cp_cal = comp1_eq.cal(T=290)
print(Cp_cal)

# first derivative
Cp_cal_first = comp1_eq.cal_first_derivative(T=273.15)
print(Cp_cal_first)

# second derivative
Cp_cal_second = comp1_eq.cal_second_derivative(T=273.15)
print(Cp_cal_second)

# integral
Cp_cal_integral = comp1_eq.cal_integral(T1=273.15, T2=373.15)
print(Cp_cal_integral)


# ====================================
# BUILD THERMODB
# ====================================
# build a thermodb
thermo_db = ptdb.build_thermodb()
print(type(thermo_db))

# add TableData
thermo_db.add_data('general', comp1_data)
# add TableEquation
thermo_db.add_data('heat-capacity', comp1_eq)
# add string
# thermo_db.add_data('dHf', {'dHf_IG': 152})
# export
# thermo_db.export_data_structure(comp1)
# save
thermo_db.save(f'{comp1}-4.pkl')
