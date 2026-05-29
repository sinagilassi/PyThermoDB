# 🚀 Quickstart

This walkthrough covers the minimum end-to-end flow:

1. initialize the app
2. build one `TableData` and one `TableEquation`
3. store them in a ThermoDB file
4. load the file and retrieve values

```python
import os
import pyThermoDB as ptdb

# 1) initialize references
tdb = ptdb.init()

# 2) build thermo properties
component = "carbon dioxide"
data_obj = tdb.build_data(component, 1, 2)
eq_obj = tdb.build_equation(component, 1, 3)

print(data_obj.get_property("MW"))
print(eq_obj.cal(T=298.15))

# 3) create and save thermodb
db = ptdb.build_thermodb(thermodb_name="co2-demo")
db.add_data("general", data_obj)
db.add_data("vapor-pressure", eq_obj)
db.save("co2-demo.pkl", file_path=os.getcwd())

# 4) load and use
loaded = ptdb.load_thermodb(os.path.join(os.getcwd(), "co2-demo.pkl"))
print(loaded.check())
print(loaded.retrieve("general | MW", message="molecular weight"))
```

## 🔜 Next Steps

- [Core Workflows](core-workflows.md)
- [Constants](constants.md)
- [Examples Map](examples.md)
