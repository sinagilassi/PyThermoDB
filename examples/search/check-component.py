# import packages/modules
import pyThermoDB as ptdb
from rich import print

# get versions
print(ptdb.__version__)
print(ptdb.__author__)
print(ptdb.__description__)

# ===============================
# databook reference initialization
# ===============================
tdb = ptdb.init()

# ====================================
# SEARCH IN THE DATABOOK
# ====================================
# search terms
key1 = 'Carbon dioxide'
key2 = 'CO2'
search_terms = [key1, key2]
# search_terms = [key1]
search_res = tdb.search_databook(
    search_terms, res_format='json', search_mode='exact')
print(search_res)

# search terms
# looking through Name
key1 = 'Carbon dioxide'
# search terms
search_terms = [key1]
# # column names
# column_names = ['Name']
# start search
search_res = tdb.search_databook(
    search_terms, res_format='dict', search_mode='exact')
print(search_res)

# search terms
# looking through Formula
key1 = 'CO2'
# search terms
search_terms = [key1]
# column names
column_names = ['Formula']
# start search
search_res = tdb.search_databook(
    search_terms,
    res_format='json',
    search_mode='exact',
    column_names=column_names
)
print(search_res)
