![PyThermoDB](https://drive.google.com/uc?export=view&id=1-yWNEkK4tL1qvi8FE_4OwcLYuTF2AkPP)

![Downloads](https://img.shields.io/pypi/dm/PyThermoDB) ![PyPI](https://img.shields.io/pypi/v/PyThermoDB) ![Python Version](https://img.shields.io/pypi/pyversions/PyThermoDB.svg) ![License](https://img.shields.io/pypi/l/PyThermoDB) ![Read the Docs](https://img.shields.io/readthedocs/pythermodb)

Python Thermodynamics Databook

PyThermoDB is a lightweight and user-friendly Python package designed to provide quick access to essential thermodynamic data. Whether you're a student, researcher, or engineer, this package serves as a valuable resource for retrieving thermodynamic properties, equations, and constants from your `custom thermodynamic database` (csv files).

Key Features:

- **Handbook Data**: The package sources its data from well-established thermodynamics handbooks, ensuring accuracy and reliability (*updated regularly*).
- **Custom Thermodynamic Database**: It is possible to builtin your own thermodynamic databook for your project.
- **Minimal Dependencies**: Built with simplicity in mind, the package has minimal external dependencies, making it easy to integrate into your projects.
- **Open Source**: Feel free to explore, contribute, and customize the package according to your needs.

## Streamlit

Check out `PyThermoDB` in Streamlit! [PyThermoDB on Streamlit](https://pythermodb.streamlit.app/)

## Google Colab

You can use the following code to run `PyThermoDB` in Google Colab:

| Version | Scripts |
|---------|---------|
| 1.6.0 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1vj84afCy0qKfHZzQdvLiJRiVstiCX0so?usp=sharing) |
| 1.5.0 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1jWkaSJ280AZFn9t8X7_bqz_pYtY2QKbr?usp=sharing) |

**Examples on Google Colab**

| Example | Scripts |
|---------|---------|
| CO₂ Thermodynamic Data | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1mzu70kACdvoB_jO6gTGVegGtK_ssOOHq?usp=sharing) |
| Check Component Availability | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1HdGHS_uypEf_yzsq7fZyLZH3dWnjYVSg?usp=sharing) |

## Installation

Install PyThermoDB with pip

```python
import pyThermoDB as ptdb
# check version
print(ptdb.__version__)
```

## Usage Example

* databook reference initialization:

```python
# databook reference initialization
tdb = ptdb.init()
```

* DATABOOK LIST:

```python
# databook
db_list = tdb.list_databooks()
print(db_list)
```

* TABLE LIST:

```python
# table list
tb_lists = tdb.list_tables(1)
print(tb_lists)
```

* TABLE INFO:

```python
# display a table
tb_info = tdb.table_info(1, 2)
print(tb_info)
```

* LOAD TABLES (before building):

```python
# load equation to check
vapor_pressure_tb = tdb.equation_load(1, 4)
pp(vapor_pressure_tb.eq_structure(1))
# load data to check
data_table = tdb.data_load(1, 2)
pp(data_table.data_structure())
```

* CHECK COMPONENT AVAILABILITY IN A TABLE:

```python
# check component availability in the databook and table
comp1 = "carbon Dioxide"
# CO2_check_availability = tdb.check_component(comp1, 1, 2)

# load comp data
# comp_data = tdb.get_component_data(comp1, 1, 2, dataframe=True)
# pp(comp_data)
```

* BUILD DATA OBJECT:

```python
# build data
CO2_data = tdb.build_data(comp1, 1, 2)
pp(CO2_data.data_structure())
pp(CO2_data.get_property(4))
```

* BUILD EQUATION OBJECT:

```python
# build an equation
eq = tdb.build_equation(comp1, 1, 4)
pp(eq.args)
res = eq.cal(T=298.15)
pp(res*1e-5)
```

### Build ThermoDB for Components

DataTable & EquationTable saved as an object in `Carbon Dioxide.pkl`

* BUILD THERMODB:

```python
# build a thermodb
thermo_db = ptdb.build_thermodb()
pp(type(thermo_db))

# * add TableData
thermo_db.add_data('general', comp1_data)
# * add TableEquation
thermo_db.add_data('heat-capacity', comp1_eq)
thermo_db.add_data('vapor-pressure', vapor_pressure_eq)
# add string
# thermo_db.add_data('dHf', {'dHf_IG': 152})
# file name
# thermodb_file_path = os.path.join(os.getcwd(), f'{comp1}')
# save
thermo_db.save(
    f'{comp1}', file_path='E:\\Python Projects\\pyThermoDB\\tests')
```

* CHECK THERMODB:

```python
# check all properties and functions registered
pp(thermo_db.check_properties())
pp(thermo_db.check_functions())
```

### Load a ThermoDB

`Carbon Dioxide.pkl` can be loaded as:

* LOAD THERMODB

```python
# ref
thermodb_file = 'Carbon Dioxide.pkl'
thermodb_path = os.path.join(os.getcwd(), thermodb_file)
pp(thermodb_path)
```

* LOAD THERMODB

```python
# load thermodb
CO2_thermodb = ptdb.load_thermodb(thermodb_path)
pp(type(CO2_thermodb))
```

* CHECK THERMODB

```python
# check all properties and functions registered
pp(CO2_thermodb.check())
```

### Custom Integral

* Step 1:

Modify `yml file` by adding `CUSTOM-INTEGRAL`.

* Step 2:

Add a name for the new integral body.

* Step 3:

Add a list containing the integral body.

```yml
CUSTOM-INTEGRAL:
    Cp/R:
        - A1 = parms['a0']*args['T1']
        - B1 = (parms['a1']/2)*(args['T1']**2)
        - C1 = (parms['a2']/3)*(args['T1']**3)
        - D1 = (parms['a3']/4)*(args['T1']**4)
        - E1 = (parms['a4']/5)*(args['T1']**5)
        - res1 =  A1 + B1 + C1 + D1 + E1
        - A2 = parms['a0']*args['T2']
        - B2 = (parms['a1']/2)*(args['T2']**2)
        - C2 = (parms['a2']/3)*(args['T2']**3)
        - D2 = (parms['a3']/4)*(args['T2']**4)
        - E2 = (parms['a4']/5)*(args['T2']**5)
        - res2 =  A2 + B2 + C2 + D2 + E2
        - res = res2 - res1
```

* CHECK AS:

```python
# check custom integral
pp(comp1_eq.custom_integral)
# check body
pp(comp1_eq.check_custom_integral_equation_body('Cp/R'))

# Cp/R
Cp_cal_custom_integral_Cp__R = comp1_eq.cal_custom_integral(
    'Cp/R', T1=298.15, T2=320)
pp(Cp_cal_custom_integral_Cp__R)
```

## FAQ

For any question, contact me on [LinkedIn](https://www.linkedin.com/in/sina-gilassi/) 


## Authors

- [@sinagilassi](https://www.github.com/sinagilassi)
