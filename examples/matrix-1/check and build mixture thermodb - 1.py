# import packages/modules
import pyThermoDB as ptdb
from pyThermoDB.core import TableMatrixData
from pythermodb_settings.models import Component
from pyThermoDB import check_and_build_mixture_thermodb
import os
from rich import print
from typing import Dict, Any

# version
print(ptdb.__version__)

# ====================================
# ☑️ CUSTOM REFERENCES
# ====================================
parent_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Parent directory: {parent_dir}")

# NOTE: format 2
# ! Mixture column
# files
yml_file = 'matrix-format-2.yml'
yml_path = os.path.join(parent_dir, yml_file)

REFERENCES = """
REFERENCES:
    CUSTOM-REF-1:
      DATABOOK-ID: 1
      TABLES:
        Non-randomness parameters of the NRTL equation-3:
          TABLE-ID: 1
          DESCRIPTION:
            This table provides the NRTL non-randomness parameters for the NRTL equation.
          MATRIX-SYMBOL:
            - a-constant: a
            - b
            - c
            - alpha
          STRUCTURE:
            COLUMNS: [No.,Mixture,Name,Formula,State,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
            SYMBOL: [None,None,None,None,None,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
            UNIT: [None,None,None,None,None,1,1,1,1,1,1,1,1]
          VALUES:
            - [1,methanol|ethanol,methanol,CH3OH,l,0,1,1,1.564200272,0,35.05450323,0,4.481683583]
            - [2,methanol|ethanol,ethanol,C2H5OH,l,2,3,-20.63243601,0,0.059982839,0,4.481683583,0]
            - [1,methanol|methane,methanol,CH3OH,l,1,0.300492719,0,1.564200272,0,35.05450323,0,4.481683583]
            - [2,methanol|methane,methane,CH4,g,0.380229054,0,-20.63243601,0,0.059982839,0,4.481683583,0]
"""

# custom ref
custom_reference: Dict[str, Any] = {
    'reference': [REFERENCES]
}

# ====================================
# ☑️ INITIALIZATION OWN THERMO DB
# ====================================
thermo_db = ptdb.init(custom_reference=custom_reference)

# ====================================
# ☑️ GET DATABOOK LIST
# ====================================
db_list = thermo_db.list_databooks()
print(db_list)

# ====================================
# ☑️ SELECT A DATABOOK
# ====================================
# table list
tb_list = thermo_db.list_tables('CUSTOM-REF-1')
print(tb_list)

# ====================================
# ☑️ COMPONENTS AND MIXTURE
# ====================================
# check component availability in the databook and table
# ! component
methanol = Component(name="methanol", formula="CH3OH", state="l")
ethanol = Component(name="ethanol", formula="C2H5OH", state="l")
methane = Component(name="methane", formula="CH4", state="g")

# ! mixture
mixture_methanol_ethanol = methanol.name + ' | ' + ethanol.name
print(f"Mixture: {mixture_methanol_ethanol}")

# comp1
comp1 = methanol.name
comp2 = ethanol.name
# ! components list
components = [comp1, comp2]

# ====================================
# ☑️ CHECK AND BUILD MIXTURE REFERENCE
# ====================================
# NOTE: set databook
databook_ = 'CUSTOM-REF-1'
# NOTE: set table
table_ = 'Non-randomness parameters of the NRTL equation-3'

# ! reference config
reference_config = {
    'nrtl': {
        'databook': databook_,
        'table': table_,
        'symbols': {
            'alpha': 'alpha',
            'a_i_j': 'a_i_j',
            'b_i_j': 'b_i_j',
            'c_i_j': 'c_i_j',
        }
    }
}

# >> yaml reference config
reference_config_yaml = '''
methanol | ethanol:
  nrtl:
    databook: CUSTOM-REF-1
    table: Non-randomness parameters of the NRTL equation-3
    symbols:
      alpha: alpha
      a_i_j: a_i_j
      b_i_j: b_i_j
      c_i_j: c_i_j
methanol | methane | ethanol:
  nrtl:
    databook: CUSTOM-REF-1
    table: Non-randomness parameters of the NRTL equation-3
    symbols:
      alpha: alpha
      a_i_j: a_i_j
      b_i_j: b_i_j
      c_i_j: c_i_j
'''

# NOTE: build a binary mixture thermodb
# ! mixture thermodb (binary mixture)
mixture_thermodb = check_and_build_mixture_thermodb(
    components=[methanol, ethanol],
    reference_config=reference_config_yaml,
    custom_reference=custom_reference,
    component_key='Name-State',
    mixture_key='Name',
    thermodb_name='mixture_thermodb_nrtl',
    thermodb_save=False,
    thermodb_save_path=parent_dir,
    verbose=True,
)
print(type(mixture_thermodb))


# NOTE: build a multi-component mixture thermodb
# ! mixture thermodb (multi-component mixture)
mixture_thermodb_multi = check_and_build_mixture_thermodb(
    components=[methanol, ethanol, methane],
    reference_config=reference_config,
    custom_reference=custom_reference,
    component_key='Name-State',
    mixture_key='Name',
    thermodb_name='mixture_thermodb_nrtl_multi',
    thermodb_save=False,
    thermodb_save_path=parent_dir,
    verbose=True,
)
print(type(mixture_thermodb_multi))

# ! with mixture names
mixture_thermodb_multi = check_and_build_mixture_thermodb(
    components=[methanol, ethanol, methane],
    reference_config=reference_config,
    custom_reference=custom_reference,
    component_key='Name-State',
    mixture_key='Name',
    mixture_names=['methanol|ethanol', 'methanol | methane'],
    thermodb_name='mixture_thermodb_nrtl_multi',
    thermodb_save=False,
    thermodb_save_path=parent_dir,
    verbose=True,
)
print(type(mixture_thermodb_multi))

# ! with yaml reference config
mixture_thermodb_multi = check_and_build_mixture_thermodb(
    components=[methanol, ethanol, methane],
    reference_config=reference_config_yaml,
    custom_reference=custom_reference,
    component_key='Name-State',
    mixture_key='Name',
    mixture_names=['methanol|ethanol', 'methanol | methane'],
    thermodb_name='mixture_thermodb_nrtl_multi',
    thermodb_save=False,
    thermodb_save_path=parent_dir,
    verbose=True,
)
print(type(mixture_thermodb_multi))
