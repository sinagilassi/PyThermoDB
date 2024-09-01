# import packages/modules
import pyThermoDB as ptdb
from pprint import pprint as pp


# dir
# print(dir(pt))
# get versions
# print(pt.get_version())
print(ptdb.__version__)

# ===============================
# databook reference initialization
# ===============================
tdb = ptdb.init()
# print("type: ", type(tdb))
# print("dir: ", dir(tdb))

# databook
# db = tdb.databooks()
# print(db)

# select a database
# tdb.select_databook("Perry's Chemical Engineers' Handbook")
# tdb.select_databook(1)

# check selected database
# print(tdb.selected_databook)
# list table available
# print(tdb.tables())

# manually
# print(tdb.tables(databook=1))

# display a table
tb_info = tdb.table_info(1, 1)
print(tb_info)

# load table
vapor_pressure_tb = tdb.table_load(1, 1)
pp(vapor_pressure_tb.eq_info(0))

# test equation with sample data


# ===============================
# set component
# ===============================
# comp1 = "ethane"
# check component availability
# tdb.check_component_availability(comp1)
# check component availability manually
# tdb.check_component_availability_manual(comp1, 1, 4)

# ===============================
# get data
# ===============================
# data = tdb.get_data(comp1)
# manual
# data = tdb.get_data_manual(comp1, 1, 4)
# print(f"data for {comp1}:")
# print(f"data for {data.view()}:")
# print(f"equation body for {data.equation_body()}:")
# print(f"equation parms for {data.equation_parms()}:")
# print(f"equation args for {data.equation_args()}:")
# print(f"equation return for {data.equation_return()}:")
# pprint.pprint(data)

# define args for a function
# args = {"T": 290, "Tc": 305.32}
# res = data.equation_exe(args=args)
# print(f"function exe value: {res}")

# get a prop value
# prop = data.get_prop("GiEn_IG")
# print(f"prop value: {prop}")
