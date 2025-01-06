# Search Databooks

## Search through databooks

This page will contain a search bar to search across all the databooks.  This feature is currently under development.

### Example 1 (Search by Name and Formula)

Looking for a component by name **Carbon dioxide** and by formula **CO2**, the search mode is set to **exact**. 

```python
# search terms
# looking through Name 
key1 = 'Carbon dioxide'
# looking through Formula 
key2 = 'CO2'

# search terms
search_terms = [key1, key2]

# start search
search_res = tdb.search_databook(
    search_terms, res_format='json', search_mode='exact')
print(search_res)
```

### Example 2 (Search by Name Only)

Looking for a component only by name **Carbon dioxide**, the search mode is set to **exact**. 

```python
# search terms
# looking through Name 
key1 = 'Carbon dioxide'

# search terms
search_terms = [key1]

# column names (optional)
# column_names = ['Name']

# start search
search_res = tdb.search_databook(
    search_terms, res_format='json', search_mode='exact', column_names=column_names)
print(search_res)
```

### Example 3 (Search by Formula Only)

Looking for a component only by formula **CO2**, the search mode is set to **exact**. 

```python
# search terms
# looking through Formula 
key1 = 'CO2'

# search terms
search_terms = [key1]

# column names (optional)
# column_names = ['Formula']

# start search
search_res = tdb.search_databook(
    search_terms, res_format='json', search_mode='exact', column_names=column_names)
print(search_res)
```

## List all components

You can view a list of all components in all databooks and also view a complete list including databook name/id, table name/id, and data type.

### Example 1 (components)

```python 
# component list
component_list = tdb.list_components(res_format='json')
print(component_list)
print(len(component_list))
```

### Example 2 (component info)

```python 
# component info
component_info = tdb.list_component_info(res_format='json')
print(component_info)
print(len(component_info))
```