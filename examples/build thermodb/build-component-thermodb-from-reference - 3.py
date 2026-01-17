# import libs
import os
import logging
from typing import List
from pythermodb_settings.models import Component
from pyThermoDB import build_component_thermodb_from_reference, ComponentThermoDB
from pyThermoDB.thermodbX import build_component_thermodb_from_reference_source
from rich import print
# local
from reference_content_nasa import REFERENCE_CONTENT

# NOTE: logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NOTE: current file path
parent_path = os.path.dirname(os.path.abspath(__file__))
print(f"parent_path: {parent_path}")

# database
db_path = os.path.join(parent_path, 'thermodb')
print(f"db_path: {db_path}")

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
    # Component(name='benzene', formula='C6H6', state='l'),
    # Component(name='toluene', formula='C7H8', state='l'),
    # Component(name='ethanol', formula='C2H6O', state='l'),
    Component(name='carbon dioxide', formula='CO2', state='g'),
]

ignore_state_props = ['nasamin', 'nasamax']

# SECTION: build component thermodb from reference
for comp in components:
    comp_id = f"{comp.name}-{comp.state}-nasa"
    logger.info(f"Building thermodb for component: {comp_id}")

    thermodb_component: ComponentThermoDB | None = build_component_thermodb_from_reference(
        component_name=comp.name,
        component_formula=comp.formula,
        component_state=comp.state,
        reference_content=REFERENCE_CONTENT,
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
