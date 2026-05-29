# 🧩 Custom References

Use custom references when your source tables are outside built-in package data.

## 1️⃣ Option 1: YAML Reference Only

```python
import pyThermoDB as ptdb

ref = {
    "reference": ["path/to/source-ref-1.yml"]
}
tdb = ptdb.init(custom_reference=ref)
print(tdb.list_databooks(res_format="dict"))
```

## 2️⃣ Option 2: YAML + External CSV Tables

```python
import pyThermoDB as ptdb

ref = {
    "reference": ["path/to/ref1.yml"],
    "tables": [
        "path/to/General Data.csv",
        "path/to/Vapor Pressure.csv"
    ]
}
tdb = ptdb.init(custom_reference=ref)
print(tdb.list_tables("CUSTOM-REF-1", res_format="dict"))
```

## ✅ Validate and Build from Custom Reference

```python
component = "carbon dioxide"
general = tdb.build_data(component, "CUSTOM-REF-1", "General-Data")
vapr = tdb.build_equation(component, "CUSTOM-REF-1", "Vapor-Pressure")
print(general.get_property("MW"))
print(vapr.cal(T=290))
```

## 📐 Constants in Custom References

If your reference includes constants tables, use:

```python
const_table = tdb.build_constants("CUSTOM-REF-1", "Custom-Constants")
print(const_table.get_constant("R"))
```

## ⚠️ Gotchas

!!! warning "CSV availability"
    Several examples in this repository expect local CSV files that are not
    committed for licensing reasons. Ensure those files are present before running
    related scripts.
