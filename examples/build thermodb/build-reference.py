# import libs
import logging
import os
import yaml
from typing import List
from string import Template

# NOTE: logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

# load reference content from yaml file and convert to string
with open(reference_path, 'r') as file:
    reference_data = yaml.safe_load(file)

# upd - TABLE 2-141 Critical Constants and Acentric Factors of Inorganic and Organic Compounds
general_data_path = r"D:\Google Cloud\Python Source\pyThermoDB\data\upd\upd - TABLE 2-141 Critical Constants and Acentric Factors of Inorganic and Organic Compounds.yaml"
# upd - TABLE 2-8 Vapor Pressure of Inorganic and Organic Liquids
vapor_pressure_path = r"D:\Google Cloud\Python Source\pyThermoDB\data\upd\upd - TABLE 2-8 Vapor Pressure of Inorganic and Organic Liquids.yaml"
# upd - TABLE 2-32 Densities of Inorganic and Organic Liquids
density_path = r"D:\Google Cloud\Python Source\pyThermoDB\data\upd\upd - TABLE 2-32 Densities of Inorganic and Organic Liquids.yaml"
# upd - TABLE 2-153 Heat Capacities of Inorganic and Organic Liquids
heat_capacity_liq_path = r"D:\Google Cloud\Python Source\pyThermoDB\data\upd\upd - TABLE 2-153 Heat Capacities of Inorganic and Organic Liquids.yaml"
# upd - TABLE 2-156 Heat Capacity at Constant Pressure of Inorganic and Organic Compounds in the Ideal Gas
heat_capacity_ig_path = r"D:\Google Cloud\Python Source\pyThermoDB\data\upd\upd - TABLE 2-156 Heat Capacity at Constant Pressure of Inorganic and Organic Compounds in the Ideal Gas.yaml"

# load all
general_data_value = yaml.safe_load(open(general_data_path, 'r'))
vapor_pressure_value = yaml.safe_load(open(vapor_pressure_path, 'r'))
density_value = yaml.safe_load(open(density_path, 'r'))
heat_capacity_liq_value = yaml.safe_load(open(heat_capacity_liq_path, 'r'))
heat_capacity_ig_value = yaml.safe_load(open(heat_capacity_ig_path, 'r'))


# NOTE: open reference
with open(reference_path, 'r') as file:
    reference_content = file.read()

# template
template = Template(reference_content).substitute(
    general_data_values=yaml.safe_dump(general_data_value),
    vapor_pressure_values=yaml.safe_dump(vapor_pressure_value),
    ideal_gas_heat_capacity_at_constant_pressure_values=yaml.safe_dump(
        heat_capacity_ig_value),
    liquid_heat_capacity_at_constant_pressure_values=yaml.safe_dump(
        heat_capacity_liq_value),
    liquid_density_values=yaml.safe_dump(density_value),
)

# NOTE: save to a new reference content file
new_reference_path = os.path.join(parent_path, 'reference_content_temp.yaml')
with open(new_reference_path, 'w') as file:
    file.write(template)
