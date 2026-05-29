# import libs
import logging
import os
import pickle

from pyThermoDB.core import TableConstants
from rich import print
import pyThermoDB as ptdb

# NOTE: logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NOTE: current file path
parent_path = os.path.dirname(os.path.abspath(__file__))
print(f"parent_path: {parent_path}")

# database
db_path = os.path.join(parent_path, 'thermodb')
print(f"db_path: {db_path}")

# constants thermodb file path
constants_thermodb_file = os.path.join(db_path, "constants.pkl")
print(f"constants_thermodb_file: {constants_thermodb_file}")

# SECTION: load thermodb
constants_thermodb = ptdb.load_thermodb(
    thermodb_file=constants_thermodb_file
)
print(type(constants_thermodb))

# NOTE: metadata
# ! build version
print("ThermoDB Build Version:", constants_thermodb.build_version)
# ! build date
print("ThermoDB Build Date:", constants_thermodb.build_date)
# ! python version
print("ThermoDB Build Python Version:", constants_thermodb.build_python)
# ! build type
print("ThermoDB Build Type:", constants_thermodb.build_type)

# SECTION: check all properties and constants registered
print("[bold green]ThermoDB Check:[/bold green]")
print(constants_thermodb.check())

# SECTION: check constants sources
constants_sources = constants_thermodb.check_constants()
print("[bold green]Constants Sources:[/bold green]")
print(constants_sources)

if not constants_sources:
    raise ValueError("No constants sources found in constants thermodb.")

# SECTION: get constants details
print("[bold green]Constants Details:[/bold green]")
print(constants_thermodb.all_constants_details())

# SECTION: get constants identifiers
print("[bold green]Constants Identifiers:[/bold green]")
print(constants_thermodb.all_constants_identifiers())

# SECTION: get constants labels
print("[bold green]Constants Labels:[/bold green]")
print(constants_thermodb.all_constants_id_labels())

# SECTION: select constants sources and retrieve constants
constant_names = [
    "R",
    "Universal Gas Constant",
    "dH_rxn",
    "dG_rxn",
]

for source_name in constants_sources:
    print(f"[bold green]Constants Source: {source_name}[/bold green]")

    constants_source = constants_thermodb.select_constant(source_name)
    if not isinstance(constants_source, TableConstants):
        raise TypeError(
            f"Constants source '{source_name}' is not an instance of TableConstants."
        )

    # NOTE: source data structure
    constants_data = constants_source.data_structure()
    print(constants_data)

    # NOTE: serialized size, similar to load-thermodb-1.py
    size_bytes = len(pickle.dumps(constants_source.table_values))
    print(size_bytes, "bytes")
    print(size_bytes / 1024, "KB")
    print(size_bytes / (1024 ** 2), "MB")

    # NOTE: retrieve constants by name or symbol
    for constant_name in constant_names:
        constant_data = constants_source.get_constant(
            constant_name,
            strict=False
        )
        if constant_data is None:
            continue

        print(f"[bold white]Constant '{constant_name}':[/bold white]")
        print(constant_data)
