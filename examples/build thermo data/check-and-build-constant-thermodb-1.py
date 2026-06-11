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
constants_reference_config: Dict[
    str,
    ComponentConfig
] = constants_ref_thermodb.configs
print("Constants Reference Config:")
print(constants_reference_config)

# ? ==============================================
# SECTION: Build Constants ThermoDB
# ? ==============================================
if constants_ref_thermodb is None:
    print("[bold yellow]No constants tables found in reference content.[/bold yellow]")
else:
    constants_thermodb: CompBuilder | None = check_and_build_constants_thermodb(
        reference_config=constants_reference_config,
        custom_reference=custom_reference,
        thermodb_name='constants',
        thermodb_save=True,
        thermodb_save_path=db_path,
    )

    print("[bold green]Constants ThermoDB:[/bold green]")
    print(constants_thermodb)
    print(type(constants_thermodb))

    if constants_thermodb is None:
        print("[bold red]Failed to build Constants ThermoDB.[/bold red]")
        raise ValueError("Constants ThermoDB build failed.")

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
