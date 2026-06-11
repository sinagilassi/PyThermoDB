# import packages/modules
from typing import Any, Dict, Optional
import os
from rich import print
import pyThermoDB as ptdb
from pyThermoDB import CompBuilder, TableConstants

# get versions
print(ptdb.__version__)

# ====================================
# CUSTOM REFERENCES
# ====================================
# parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))

# files
yml_file = 'str-ref-1.yml'
yml_path = os.path.join(parent_dir, yml_file)

# NOTE: custom ref
ref: Dict[str, Any] = {'reference': [yml_path]}

# ====================================
# SECTION: BUILD CONSTANT THERMODB
# ====================================
# NOTE:
# build_constant_thermodb expects an explicit constants reference config.
# Each config entry becomes a TableConstants source in the saved thermodb.
reference_config = {
    'custom-1': {
        'databook': 'CUSTOM-REF-1',
        'table': 'Custom-Constants',
        'mode': 'CONSTANTS',
        'labels': {
            'Universal Gas Constant': 'R',
            'enthalpy of reaction': 'dH_rxn',
            'binary parameter': 'Xb',
            'custom constants': 'X',
        },
    },
    'custom-2': {
        'databook': 'CUSTOM-REF-1',
        'table': 'Custom-Constants-2',
        'mode': 'CONSTANTS',
        'labels': {
            'Universal Gas Constant': 'R',
            'enthalpy of reaction': 'dG_rxn',
        },
    },
}

# NOTE: build constants thermodb
thermodb_constants_: Optional[CompBuilder] = ptdb.build_constants_thermodb(
    reference_config=reference_config,
    custom_reference=ref,
    thermodb_name='custom-constants-reference-1',
    thermodb_save=True,
    thermodb_save_path=parent_dir,
)

if thermodb_constants_ is None:
    raise ValueError("Constants thermodb was not built.")

# check
print(f"check:")
print(thermodb_constants_.check())
print(f"message:")
print(thermodb_constants_.message)
print(f"constants sources:")
print(list(thermodb_constants_.check_constants().keys()))

# check methods defined in CompBuilder
# all_constants_details
print("All constants details:")
print(thermodb_constants_.all_constants_details())
# all_constants_identifiers
print("All constants identifiers:")
print(thermodb_constants_.all_constants_identifiers())
# all_constants_id_labels
print("All constants id labels:")
print(thermodb_constants_.all_constants_id_labels())

# ====================================
# SECTION: SELECT CONSTANTS
# ====================================
# NOTE: extract table constants by id
custom_1: TableConstants = thermodb_constants_.select_constant(
    'custom-1'
)
print(type(custom_1))
print(custom_1.data_structure())

# access constants
# ! R (scalar)
print(custom_1.get_constant('R', message='gas constant'))
# ! dH_rxn (dictionary)
print(custom_1.get_constant('dH_rxn', message='enthalpy of reaction'))
# ! Xb (string)
print(custom_1.get_constant('Xb', message='binary parameter'))
# ! X (list)
print(custom_1.get_constant('X', message='custom constants'))
# ! non-existing constant
print(custom_1.get_constant('non_existing_constant', strict=False))

# retrieve constants using the CompBuilder helper
print(thermodb_constants_.retrieve(
    'custom-1 | R',
    message='gas constant'
))
print(thermodb_constants_.retrieve(
    'custom-1 | dH_rxn',
    message='enthalpy of reaction'
))

# NOTE: extract table constants by id
custom_2: TableConstants = thermodb_constants_.select_constant(
    'custom-2'
)
print(custom_2.get_constant(
    'dG_rxn',
    message='Gibbs free energy of reaction'
))

# ====================================
# SECTION: LOAD THERMODB
# ====================================
# NOTE: load the saved thermodb with constants
thermodb_file = 'custom-constants-reference-1.pkl'
thermodb_path = os.path.join(parent_dir, thermodb_file)

thermodb_loaded: CompBuilder = ptdb.load_thermodb(thermodb_path)
print(type(thermodb_loaded))
print(f"loaded check: {thermodb_loaded.check()}")

# ! access loaded constants
const1_: TableConstants = thermodb_loaded.select_constant('custom-1')
print(const1_.get_constant('R', message='loaded gas constant'))
# ! access loaded constants using the CompBuilder helper
print(thermodb_loaded.retrieve(
    'custom-2 | dG_rxn',
    message='loaded Gibbs free energy of reaction'
))
