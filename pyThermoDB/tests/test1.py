# import packages/modules
import pyThermoDB as pt
import pprint


# dir
# print(dir(pt))
# get versions
# print(pt.get_version())
print(pt.__version__)

# databook reference
tdb = pt.thermo_databook()
print("type: ", type(tdb))
print("dir: ", dir(tdb))

# display databook reference
# tdb.init()

# display config
# tdb.config()

# databook selected
# print(tdb.get_databook())
# table selected
# print(tdb.get_table())

# set component
comp1 = "Carbon dioxide"
# check component availability
# tdb.check_component_availability(comp1)
# check component availability manually
tdb.check_component_availability_manual(comp1, 1, 1)

# get data
# data = tdb.get_data(comp1)
# manual
data = tdb.get_data_manual(comp1, 1, 2)
# print(f"data for {comp1}:")
print(f"data for {data.view()}:")
# print(f"equation body for {data.equation_body()}:")
# print(f"equation parms for {data.equation_parms()}:")
# print(f"equation args for {data.equation_args()}:")
# print(f"equation return for {data.equation_return()}:")
# pprint.pprint(data)

# define args for a function
args = {"T": 304.21}
res = data.equation_exe(args=args)
print(f"function exe value: {res}")