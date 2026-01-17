# import libs
import os
from pathlib import Path
import logging
from typing import List
from pythermodb_settings.models import Component
from pyThermoDB import build_component_thermodb_from_reference, ComponentThermoDB
from pyThermoDB.thermodbX import build_component_thermodb_from_reference_source, ReferenceContentSource
from rich import print
from pythermodb_settings.references import extract_reference_components, check_reference_component_availability
# local
from reference_content_nasa import REFERENCE_CONTENT

# NOTE: logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NOTE: current file path
parent_path = os.path.dirname(os.path.abspath(__file__))
print(f"parent_path: {parent_path}")

# database
db_path = os.path.join(parent_path, 'thermodb-nasa')
print(f"db_path: {db_path}")

# source reference file path
reference_file_path = os.path.join(parent_path, 'reference_content.yaml')
print(f"reference_file_path: {reference_file_path}")

# SECTION: check component availability
component_name = 'carbon dioxide'
component_formula = 'CO2'
component_state = 'g'
# component id
component_id = f"{component_name}-{component_state}"
print(f"component_id: {component_id}")

# # SECTION: build component thermodb with ignore state
# # NOTE: ignore state for specific properties
# ignore_state_props = ['MW', 'VaPr']
# thermodb_component_ignore_state_: ComponentThermoDB | None = build_component_thermodb_from_reference(
#     component_name=component_name,
#     component_formula=component_formula,
#     component_state=component_state,
#     reference_content=REFERENCE_CONTENT,
#     ignore_state_props=ignore_state_props,
#     thermodb_name=component_id,
#     thermodb_save=True,
#     thermodb_save_path=db_path,
# )

# print(f"thermodb_component_ignore_state_: {thermodb_component_ignore_state_}")
# if thermodb_component_ignore_state_ is not None:
#     # NOTE: thermodb
#     thermodb_ignore_state_ = thermodb_component_ignore_state_.thermodb
#     print(f"thermodb_ignore_state_: {thermodb_ignore_state_}")
#     # check
#     print(f"thermodb_ignore_state_ checks: {thermodb_ignore_state_.check()}")


# NOTE: components
components: List[Component] = [
    Component(name='benzene', formula='C6H6', state='g'),
    Component(name='toluene', formula='C7H8', state='g'),
    Component(name='ethanol', formula='C2H6O', state='g'),
    Component(name='methane', formula='CH4', state='g'),
    Component(name="methanol", formula='CH4O', state='g'),
    Component(name='propane', formula='C3H8', state='g'),
    Component(name='ethane', formula='C2H6', state='g'),
    Component(name='carbon dioxide', formula='CO2', state='g'),
    Component(name='carbon monoxide', formula='CO', state='g'),
    Component(name='dinitrogen', formula='N2', state='g'),
    Component(name='dioxygen', formula='O2', state='g'),
    Component(name='water', formula='H2O', state='g'),
    Component(name='dihydrogen', formula='H2', state='g'),
]

# SECTION: Check reference component availability
availability_results = check_reference_component_availability(
    reference=reference_file_path,
    component_keys=['C6H6', 'C7H8', 'C2H6O', 'CH4', 'CH4O',
                    'C3H8', 'C2H6', 'CO2', 'CO', 'N2', 'O2', 'H2O', 'H2'],
    component_key="Formula",
    separator_symbol="-",
    case=None,
    renumber=False
)
print(f"availability_results:")
print(availability_results)

# SECTION: build component thermodb from reference

# NOTE: ignore state for specific properties
ignore_state_props = [
    'nasa9_200_1000_K',
    'nasa9_1000_6000_K',
    'nasa9_6000_20000_K'
]

# SECTION: reference source
# SECTION: reference source
REFERENCE_SOURCE = ReferenceContentSource(
    content=REFERENCE_CONTENT,
)

# SECTION: build component thermodb from reference
for comp in components:
    comp_id = f"{comp.name}-{comp.formula}-{comp.state}-nasa-1"
    logger.info(f"Building thermodb for component: {comp_id}")

    thermodb_component: ComponentThermoDB | None = build_component_thermodb_from_reference_source(
        component=comp,
        reference_source=REFERENCE_SOURCE,
        component_key='Formula-State',
        ignore_state_props=ignore_state_props,
        check_labels=False,
        thermodb_name=comp_id,
        thermodb_save=True,
        thermodb_save_path=db_path,
        include_data=False,
    )

    if thermodb_component is not None:
        logger.info(f"Successfully built thermodb for component: {comp_id}")
        print(thermodb_component.thermodb.check())
    else:
        logger.error(f"Failed to build thermodb for component: {comp_id}")
