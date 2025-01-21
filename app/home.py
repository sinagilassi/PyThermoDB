import streamlit as st

# title
st.title('Welcome to PyThermoDB')

# description
st.write('This app is a simple web interface for the PyThermoDB Python package. It allows users to search for thermodynamic data for chemical species and reactions.')

code = '''
# import package
import pyThermoDB as ptdb
# check version
print(ptdb.__version__)
'''
st.code(code, language='python', line_numbers=False)

# section title
st.header('Features')

# list
st.markdown('''
- Search for chemical species and reactions.
- View thermodynamic data for chemical species and reactions.
- Download thermodynamic data for chemical species and reactions.
''')


# content
st.write(
    'Check out examples of how to use the PyThermoDB package in the [documentation](https://pythermodb.readthedocs.io/en/latest/).')

st.write('You can also have a look at `tests folder` in the github repository to see how the package is used.')

# ask question
st.write(
    'If you have any questions or would like to report a bug, please open an issue in the [github repository](https://github.com/sinagilassi/PyThermoDB/issues)')
