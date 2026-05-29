# 📝 README Highlights

This page curates important sections from `README.md` and adapts them for the docs flow.

## ✨ Key Features

- **Handbook Data**: built-in thermodynamic datasets from established sources.
- **Custom Thermodynamic Database**: load external references and tables for project-specific data.
- **Minimal Dependencies**: compact core dependency set.
- **Open Source**: designed for extension and integration.

## 🤖 PyThermoAI

Related project: [PyThermoAI](https://github.com/sinagilassi/PyThermoAI)  
It focuses on AI-assisted thermodynamic data acquisition and conversion to PyThermoDB reference formats.

## 📓 Interactive Notebooks (Binder)

- [Basic Usage 1](https://mybinder.org/v2/gh/sinagilassi/PyThermoDB/HEAD?urlpath=%2Fdoc%2Ftree%2Fnotebooks%2Fdoc1.ipynb)
- [Custom Reference](https://mybinder.org/v2/gh/sinagilassi/PyThermoDB/HEAD?urlpath=%2Fdoc%2Ftree%2Fnotebooks%2Fref-external.ipynb)
- [Check Reference](https://mybinder.org/v2/gh/sinagilassi/PyThermoDB/HEAD?urlpath=%2Fdoc%2Ftree%2Fnotebooks%2Ftable-view.ipynb)

## 🔬 Google Colab Examples

- [Search Database](https://colab.research.google.com/drive/1y5GIE4DH73SwOF2JhsTug2_U_h9Fqexx?usp=sharing)
- [CO2 Thermodynamic Data](https://colab.research.google.com/drive/1mzu70kACdvoB_jO6gTGVegGtK_ssOOHq?usp=sharing)
- [Check Component Availability](https://colab.research.google.com/drive/1HdGHS_uypEf_yzsq7fZyLZH3dWnjYVSg?usp=sharing)
- [Basic Usage 2](https://colab.research.google.com/drive/1vj84afCy0qKfHZzQdvLiJRiVstiCX0so?usp=sharing)
- [Basic Usage 1](https://colab.research.google.com/drive/1jWkaSJ280AZFn9t8X7_bqz_pYtY2QKbr?usp=sharing)

## 🚀 Streamlit App

[PyThermoDB on Streamlit](https://pythermodb.streamlit.app/)

## 🔍 Search Notes (from README)

README demonstrates search-oriented discovery flows. In current API usage, prefer:

- `search_databook(...)` for component-oriented lookup
- `search_constants(...)` for constants tables
- `list_components(...)` / `list_components_info(...)` for broad inventory

Examples are documented in [Search Workflows](search.md) and [Core Workflows](core-workflows.md).

## 📝 License Note

Project code is MIT-licensed. Thermodynamic datasets may have separate upstream licenses/terms and should be sourced/used accordingly.
