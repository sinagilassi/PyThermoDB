# import libs
from rich import print
import os
import logging
from typing import Dict, List, Optional
from pyThermoDB import (
    check_and_build_component_thermodb,
    check_and_build_constants_thermodb,
    CompBuilder
)
from pyThermoDB.references import component_reference_mapper, constants_reference_mapper
from pyThermoDB.core import (
    TableEquation,
    TableData,
    TableConstants
)
from pythermodb_settings.models import (
    Component,
    ComponentReferenceThermoDB,
    ReferenceThermoDB
)
from pythermodb_settings.models import ComponentConfig
# local
# ! reference content
from ref_content import REFERENCE_CONTENT

# NOTE: logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ? ==============================================
# SECTION: current file path and database path
# ? ==============================================
# NOTE: current file path
parent_path = os.path.dirname(os.path.abspath(__file__))
print(f"parent_path: {parent_path}")

# database
db_path = os.path.join(parent_path, 'thermodb')
print(f"db_path: {db_path}")

# ! custom reference
custom_reference: Dict[str, List[str]] = {'reference': [REFERENCE_CONTENT]}

# ? ==============================================
# SECTION: Map Constants Reference ThermoDB
# ? ==============================================
constants_ref_thermodb: ReferenceThermoDB | None = constants_reference_mapper(
    reference_content=REFERENCE_CONTENT
)

print("[bold green]Constants Reference ThermoDB:[/bold green]")
print(constants_ref_thermodb)

# constant reference config
if constants_ref_thermodb is None:
    raise

# ----------------------------------------------------------------------------
# NOTE: extract constants reference config from the mapped reference content
# ----------------------------------------------------------------------------
constants_reference_config: Dict[
    str,
    ComponentConfig
] = constants_ref_thermodb.configs
print("Constants Reference Config:")
print(constants_reference_config)

# --------------------------------
# NOTE: custom reference config
# --------------------------------
custom_reference_config: Dict[str, ComponentConfig] = {
    'custom-1': {
        'databook': 'CUSTOM-REF-1',
        'table': 'Custom-Constants',
        'mode': 'CONSTANTS',
        'labels': {
            'Universal Gas Constant': 'R',
            'Constant1': 'C1',
            'total heat capacity of ideal gas': 'Cp_IG',
            'enthalpy of reaction': 'dH_rxn',
            'binary parameter': 'Xb',
            'custom constants': 'X',
            'gibbs energy of reaction': 'dG_rxn'
        }
    },
    'custom-2': {
        'databook': 'CUSTOM-REF-1',
        'table': 'Custom-Constants-2',
        'mode': 'CONSTANTS',
        'labels': {
            'Universal Gas Constant': 'R',
            'Constant1': 'C1',
            'total heat capacity of ideal gas': 'Cp_IG',
            'enthalpy of reaction': 'dG_rxn'
        }
    }
}

# ! select reference config
reference_config_selected = custom_reference_config

# ==============================================
# SECTION: Build Constants ThermoDB
# ==============================================
# NOTE: check and build constants thermodb
constants_thermodb: Optional[CompBuilder] = check_and_build_constants_thermodb(
    reference_config=reference_config_selected,
    custom_reference=custom_reference,
    thermodb_name='constants',
    thermodb_save=True,
    thermodb_save_path=db_path,
)

print("[bold green]Constants ThermoDB:[/bold green]")
print(constants_thermodb)
print(type(constants_thermodb))

# check if the constants thermodb was built successfully
if constants_thermodb is None:
    print("[bold red]Failed to build Constants ThermoDB.[/bold red]")
    raise ValueError("Constants ThermoDB build failed.")

# checks
print(f"check:")
print(constants_thermodb.check())

constants_sources = constants_thermodb.check_constants()
print("Constants Sources:")
print(constants_sources)

for source_name, source in constants_sources.items():
    if not isinstance(source, TableConstants):
        raise TypeError(
            f"Constants source '{source_name}' is not an instance of TableConstants."
        )
    print(f"Constants source '{source_name}' data structure:")
    print(source.data_structure())
