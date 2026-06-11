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

# ? ==============================================
# SECTION: check component availability
# ? ==============================================
component_name = 'carbon dioxide'
component_formula = 'CO2'
component_state = 'g'

component = Component(
    name=component_name,
    formula=component_formula,
    state=component_state
)

# component id
component_id = f"{component_name}-{component_state}"
print(f"component_id: {component_id}")

# ? ==============================================
# SECTION: Map Component Reference ThermoDB
# ? ==============================================

# ! ignore_state_props to ignore state check for specific properties
ignore_state_props = ['Cp_IG', 'MW', 'VaPr']
component_ref_thermodb2: ComponentReferenceThermoDB = component_reference_mapper(
    component=component,
    reference_content=REFERENCE_CONTENT,
    component_key='Formula-State',
    ignore_state_props=ignore_state_props
)

print("[bold green]Ignored State Properties:[/bold green]")
print(ignore_state_props)


print("component ref thermodb 2:")
print(component_ref_thermodb2)


# ! custom reference
custom_reference: Dict[str, List[str]] = {'reference': [REFERENCE_CONTENT]}
# ! reference config
reference_config: Dict[
    str,
    ComponentConfig
] = component_ref_thermodb2.reference_thermodb.configs
# ! ignore labels
ignore_labels = component_ref_thermodb2.reference_thermodb.ignore_labels

# ? ==============================================
# SECTION: Build Component ThermoDB
# ? ==============================================
# build component thermodb
component_thermodb: Optional[CompBuilder] = check_and_build_component_thermodb(
    component=component,
    reference_config=reference_config,
    custom_reference=custom_reference,
    component_key='Formula-State',
    ignore_state_props=ignore_labels,
    thermodb_name=component_id,
    thermodb_save=True,
    thermodb_save_path=db_path,
    include_data=False,
)

print(
    f"[bold green]Component ThermoDB (from custom reference):[/bold green]")
print(ignore_state_props)

print("Component ThermoDB:")
print({component_thermodb})
print(type(component_thermodb))

# ? ==============================================
# SECTION: Check Component ThermoDB
# ? ==============================================

# check result
if component_thermodb is None:
    print("[bold red]Failed to build Component ThermoDB.[/bold red]")
    raise ValueError("Component ThermoDB build failed.")

# NOTE: ideal-gas-heat-capacity calculation
Cp_eq = component_thermodb.select_function(
    function_name='CUSTOM-REF-1::ideal-gas-heat-capacity'
)
print(type(Cp_eq))

# TableEquation instance
if not isinstance(Cp_eq, TableEquation):
    raise TypeError("Cp_eq is not an instance of TableEquation.")

# equation summary
print(Cp_eq.summary)

# ! normalized equation
print(Cp_eq.normalized_fn_body(1))

# ! normalized all equations
print(Cp_eq.normalized_fns())

# ! get records
print("Cp_eq Records:")
print(Cp_eq.get_records())

# NOTE: calculate Cp at T=300 K
T = 300  # temperature in K
Cp_value = Cp_eq.cal(T=T)
print(
    f"[bold white]Calculated ideal-gas-heat-capacity at T={T} K:[/bold white]")
print(Cp_value)


# NOTE: check general data
general_data = component_thermodb.select('CUSTOM-REF-1::general-data')
print(type(general_data))

# TableData instance
if not isinstance(general_data, TableData):
    raise TypeError("general_data is not an instance of TableData.")

# symbols
print("General Data Symbols:")
print(general_data.table_symbols)

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
