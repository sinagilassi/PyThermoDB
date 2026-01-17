# import libs
import os
from pyThermoDB.utils import filter_yaml_for_component
from rich import print


# ? =====================================================
# SECTION: paths
# ? =====================================================
# NOTE: current file path
parent_path = os.path.dirname(os.path.abspath(__file__))
print(f"parent_path: {parent_path}")

# database
db_path = os.path.join(parent_path, 'thermodb')
print(f"db_path: {db_path}")

# ? =====================================================
# SECTION: load reference content
# ? =====================================================
# NOTE: reference path
reference_path = r"D:\Google Cloud\Python Source\pyThermoDB\data\upd\reference_content.yaml"

# ? =====================================================
# SECTION: filter component data
# ? =====================================================
# output file
component_id = "methyl tert-butyl ether 0"
output_path = os.path.join(parent_path, f'res_comp_{component_id}.yaml')
print(f"output_path: {output_path}")


# yaml file
res = filter_yaml_for_component(
    component=component_id,
    match_by="name",
    input_path=reference_path,
    output_path=output_path
)
print(res)

res = filter_yaml_for_component(
    component=component_id,
    match_by="name",
    input_path=reference_path,
    verbose=True
)
print(res)
