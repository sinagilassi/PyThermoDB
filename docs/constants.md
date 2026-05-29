# 📐 Constants

Constants tables are table-wide sources and are not component-specific.

## 📥 Load or Build Constants Table

```python
import pyThermoDB as ptdb
tdb = ptdb.init()

constants = tdb.build_constants("CUSTOM-REF-1", "Custom-Constants")
print(constants.data_structure())
```

## 🎯 Retrieve Constants

`TableConstants.get_constant(...)` may return scalar, dictionary, list, or string
depending on the stored value.

```python
print(constants.get_constant("R"))         # scalar
print(constants.get_constant("dH_rxn"))    # dict-like
print(constants.get_constant("X"))         # list-like
print(constants.get_constant("Xb"))        # string-like
```

## 🔎 Search and List Constants Across Databooks

```python
print(tdb.list_constants(res_format="dataframe"))

print(tdb.search_constants(
    search_terms=["R", "Universal Gas Constant"],
    column_names=["Symbol", "Name"],
    res_format="dict",
    search_mode="exact"
))
```

## ⚠️ Gotchas

!!! warning "Constants vs component search"
    `search_databook(...)` is component-oriented. Use `search_constants(...)`
    for constants discovery.
