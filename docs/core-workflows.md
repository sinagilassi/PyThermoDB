# ⚙️ Core Workflows

## 🔌 Initialize

```python
import pyThermoDB as ptdb
tdb = ptdb.init()
```

## 📋 Inspect Databooks and Tables

```python
print(tdb.list_databooks(res_format="dataframe"))
print(tdb.list_tables(1, res_format="dict"))
print(tdb.table_info(1, 2, res_format="dict"))
```

## 🧱 Load Table Structure Before Building

```python
data_table = tdb.data_load(1, 2)
print(data_table.data_structure())

eq_table = tdb.equation_load(1, 3)
print(eq_table.eq_structure(1))
```

## ✅ Check Component Availability

```python
check = tdb.check_component("carbon dioxide", 1, 2, res_format="dict")
print(check)
```

## 🛠️ Build Data and Equation Objects

```python
co2_data = tdb.build_data("carbon dioxide", 1, 2)
print(co2_data.get_property("MW"))
print(co2_data.get_property("molecular-weight"))

co2_vapr = tdb.build_equation("carbon dioxide", 1, 3)
print(co2_vapr.args)
print(co2_vapr.cal(T=298.15))
```

## 🔎 Search Databooks

```python
# exact name + formula
print(tdb.search_databook(
    ["Carbon dioxide", "CO2"],
    res_format="dict",
    search_mode="exact"
))

# formula-only search
print(tdb.search_databook(
    ["CO2"],
    column_names=["Formula"],
    res_format="json",
    search_mode="exact"
))
```

## ⚠️ Gotchas

!!! warning "Component key modes"
    API surfaces use different component key conventions depending on method:
    `Name`, `Formula`, `Name-State`, and `Formula-State`.

!!! warning "Table types"
    Always check `table_info(...)` first. Behavior differs across `Data`,
    `Equation`, `Matrix-Data`, `Matrix-Equation`, and `Constants`.
