import pyThermoDB as ptdb

# initialize databook reference
tdb = ptdb.init()

# search for a chemical species


def search_species(species):
    try:
        # search terms
        search_terms = [species]
        # # column names
        # column_names = ['Name']
        # start search
        search_res = tdb.search_databook(
            search_terms, res_format='dict', search_mode='exact')

        return search_res
    except Exception:
        return None
