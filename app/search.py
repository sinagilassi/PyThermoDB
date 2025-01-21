import streamlit as st
# local
from utils import utils

# Initialize session state for search results
if 'search_res' not in st.session_state:
    st.session_state.search_res = None

# title
st.title('Search')

# description
st.write('This page allows users to search for thermodynamic data for chemical species and reactions.')

# search bar
search = st.text_input('Search for a chemical species or reaction')


# create two columns for buttons
col1, col2 = st.columns(2)

# search button
with col1:

    if st.button('Search', use_container_width=True):
        st.write('Searching for:', search)

        # add spinner
        with st.spinner('Searching...'):
            # search for species
            try:
                st.session_state.search_res = utils.search_species(search)
            except Exception as e:
                st.error(f"Error during search: {e}")

# Clear button
with col2:
    if st.button('Clear', use_container_width=True):
        st.session_state.search_res = None


# Display the search results
if st.session_state.search_res:
    search_res = st.session_state.search_res
    if isinstance(search_res, dict):
        for record_key, record_value in search_res.items():
            st.write(f"Databook ID: {record_value.get('databook-id', '')}")
            st.write(f"Databook Name: {record_value.get('databook-name', '')}")
            st.write(f"Table ID: {record_value.get('table-id', '')}")
            st.write(f"Table Name: {record_value.get('table-name', '')}")
            st.write(f"Data Type: {record_value.get('data-type', '')}")
            st.write("---")
    else:
        st.write('No results found.')
