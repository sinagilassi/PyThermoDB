# 📘 Comprehensive Walkthrough

This page provides a detailed, end-to-end walkthrough similar to the published
ReadTheDocs examples page, while keeping API names aligned with current package behavior.

## 1) Import and Initialize

```python
import pyThermoDB as ptdb
from rich import print

print(ptdb.__version__)
tdb = ptdb.init()
```

## 2) Databook Discovery

### List databook and table descriptions

```python
db_descriptions = tdb.list_descriptions(res_format="json")
print(db_descriptions)
```

### List databooks

```python
db_list = tdb.list_databooks(res_format="json")
print(db_list)
```

### Get databook id

```python
db_id = tdb.get_databook_id("Perry's Chemical Engineers' Handbook", res_format="dict")
print(db_id)
```

## 3) Table Discovery

### List tables in databook

```python
tb_list = tdb.list_tables("Chemical Thermodynamics for Process Simulation", res_format="json")
print(tb_list)
```

### Table info (type and counts)

```python
tb_info = tdb.table_info(
    "Chemical Thermodynamics for Process Simulation",
    "Table A.1 General data for selected compounds",
    res_format="dict",
)
print(tb_info)
```

### Get table id

```python
tb_id = tdb.get_table_id(
    "Chemical Thermodynamics for Process Simulation",
    "Table A.1 General data for selected compounds",
    res_format="dict",
)
print(tb_id)
```

## 4) Inspect Table Structures Before Build

### Data table structure

```python
data_table = tdb.data_load("Chemical Thermodynamics for Process Simulation", 1)
print(data_table.data_structure())
```

### Equation structure

```python
eq_table = tdb.equation_load("Chemical Thermodynamics for Process Simulation", 2)
print(eq_table.eq_structure(1))
```

## 5) Check Component Availability

```python
check_res = tdb.check_component(
    "carbon dioxide",
    "Chemical Thermodynamics for Process Simulation",
    "Table A.1 General data for selected compounds",
    res_format="dict",
)
print(check_res)
```

## 6) Build Data Object

```python
component_data = tdb.build_data(
    "carbon dioxide",
    "Chemical Thermodynamics for Process Simulation",
    "Table A.1 General data for selected compounds",
)
print(component_data.data_structure())
```

### Access property by id / name / symbol

```python
print(component_data.get_property(12))
print(component_data.get_property("standard-Gibbs-energy-of-formation"))
print(component_data.get_property("GiEnFo_IG"))
```

### Typical scalar extraction

```python
Tc = float(component_data.get_property("Tc")["value"])
Pc = float(component_data.get_property("Pc")["value"])
MW = float(component_data.get_property("MW")["value"])
print(Tc, Pc, MW)
```

## 7) Build Equation Object

```python
eq = tdb.build_equation(
    "carbon dioxide",
    "Chemical Thermodynamics for Process Simulation",
    "Table A.2 Vapor pressure correlations for selected compounds",
)
print(eq.args)
print(eq.parms)
print(eq.returns)
print(eq.body)
print(eq.cal(T=253.15, Tc=73.773, Pc=44.009))
```

## 8) Search Workflows

### Name + formula

```python
print(tdb.search_databook(
    ["Carbon dioxide", "CO2"],
    res_format="json",
    search_mode="exact",
))
```

### Name only

```python
print(tdb.search_databook(
    ["Carbon dioxide"],
    res_format="dict",
    search_mode="exact",
))
```

### Formula only

```python
print(tdb.search_databook(
    ["CO2"],
    column_names=["Formula"],
    res_format="json",
    search_mode="exact",
))
```

## 9) Build and Save ThermoDB

```python
import os
thermodb = ptdb.build_thermodb(thermodb_name="co2-thermodb")
thermodb.add_data("general", component_data)
thermodb.add_data("vapor-pressure", eq)
thermodb.save("co2-thermodb.pkl", file_path=os.getcwd())
print(thermodb.check_properties())
print(thermodb.check_functions())
```

## 10) Load ThermoDB

```python
loaded = ptdb.load_thermodb(os.path.join(os.getcwd(), "co2-thermodb.pkl"))
print(loaded.check())
print(loaded.retrieve("general | MW", message="molecular weight"))
```

## Notes

!!! warning "Table-type awareness is required"
    Always inspect table type first. Build and retrieval behavior differs for
    `Data`, `Equation`, `Matrix-Data`, `Matrix-Equation`, and `Constants`.

!!! warning "Key-mode consistency"
    For advanced methods, ensure component key mode (`Name`, `Formula`,
    `Name-State`, `Formula-State`) is consistent with table schema and API call.
