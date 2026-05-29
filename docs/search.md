# Search Workflows

## Search Components Across Databooks

```python
import pyThermoDB as ptdb
tdb = ptdb.init()

print(tdb.search_databook(
    ["Carbon dioxide", "CO2"],
    res_format="dict",
    search_mode="exact"
))

print(tdb.search_databook(
    ["CO2"],
    column_names=["Formula"],
    res_format="json",
    search_mode="exact"
))
```

## List Components

```python
print(tdb.list_components(res_format="dict"))
print(tdb.list_components_info(res_format="dict"))
```

## Constants Search

```python
print(tdb.list_constants(res_format="dataframe"))
print(tdb.search_constants(
    search_terms=["R"],
    column_names=["Symbol"],
    search_mode="exact",
    res_format="dict"
))
```
