# import packages/modules
import pyThermoDB as pt

# dir
# print(dir(pt))
# get versions
# print(pt.get_version())

# databook reference
tdb = pt.thermo_databook()
print("type: ", type(tdb))
print("dir: ", dir(tdb))

# display databook reference
tdb.init()

# display config
tdb.config()

# databook selected
print(tdb.get_databook())
# table selected
print(tdb.get_table())

# set component
tdb.set_component()
