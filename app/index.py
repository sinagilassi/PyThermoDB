import streamlit as st 

# page config
st.set_page_config(page_title='PyThermoDB App', page_icon='🧊', layout='wide', initial_sidebar_state='expanded')

# pages
pages = [
    st.Page('home.py',title='Home',icon='🧊'),
    st.Page('search.py',title='Search',icon='🔍'),
    st.Page('about.py',title='About',icon='📚'),
]

pg = st.navigation(pages)
pg.run()
