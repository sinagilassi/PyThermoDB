# import libs
import logging
import os
from typing import Dict, Any, List
from pythermodb_settings.models import Component
from rich import print
import pyThermoDB as ptdb
from pyThermoDB.core import TableData, TableEquation
from pyThermoDB import build_component_thermodb_from_reference, ComponentThermoDB

# NOTE: logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NOTE: yaml reference content
# current folder
current_dir = os.path.dirname(os.path.abspath(__file__))
# yaml file path
yaml_file_path = os.path.join(current_dir, 'custom_reference_2.yaml')

# NOTE: load reference from yaml file
with open(yaml_file_path, 'r') as f:
    yaml_reference_content = f.read()


# NOTE: custom ref
custom_reference: Dict[str, Any] = {'reference': [yaml_reference_content]}
print("[bold green]Custom reference content:[/bold green]")
print(custom_reference)

# ====================================
# INITIALIZATION OWN THERMO DB
# ====================================
thermo_db = ptdb.init(custom_reference=custom_reference)

# ====================================
# GET DATABOOK LIST
# ====================================
db_list = thermo_db.list_databooks(res_format='list')
print(db_list)

# ====================================
# SELECT A DATABOOK
# ====================================
# NOTE: set databook
databook_ = 'CUSTOM-REF-1'

# table list
tb_list = thermo_db.list_tables(databook_, res_format='list')
print(tb_list)


# table names
tb_names = thermo_db.list_table_names(databook_)
print(tb_names)

# CREATE COMPONENT
comp1 = "carbon dioxide"

# ====================================
# BUILD DATA
# ====================================
# build data
data_1 = thermo_db.build_thermo_property(
    [comp1], databook_, 'general-data')
print(type(data_1))

# retrieve data
if isinstance(data_1, TableData):
    res_ = data_1.get_property("MW")
    print(res_)

# ====================================
# BUILD EQUATION
# ====================================
comp1_eq_1 = thermo_db.build_thermo_property(
    [comp1], databook_, 'ideal-gas-heat-capacity')

# equation details
if isinstance(comp1_eq_1, TableEquation):
    print(comp1_eq_1.equation_parms())
    print(comp1_eq_1.equation_args())
    print(comp1_eq_1.equation_body())
    print(comp1_eq_1.equation_return())
    # cal
    res_ = comp1_eq_1.cal(T=290)
    print(res_)


# ====================================
# SECTION: build component thermodb from reference
# ===================================
# reference
# NOTE: reference content
REFERENCE_CONTENT = yaml_reference_content

# NOTE: components
components: List[Component] = [
    Component(name='carbon dioxide', formula='CO2', state='g'),
]

ignore_state_props = ['MW', 'VaPr', 'Cp_IG']

# SECTION: build component thermodb from reference
for comp in components:
    comp_id = f"{comp.name}-{comp.state}-custom"
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
        thermodb_save_path=current_dir,
        include_data=False,
    )

    if thermodb_component is not None:
        logger.info(f"Successfully built thermodb for component: {comp_id}")
        print(thermodb_component.thermodb.check())
    else:
        logger.error(f"Failed to build thermodb for component: {comp_id}")
