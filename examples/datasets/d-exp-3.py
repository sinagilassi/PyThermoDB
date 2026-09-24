"""Load and query a VLE TableDataset from an inline YAML reference."""

from __future__ import annotations
from pyThermoDB.core import TableDataset
import pyThermoDB as ptdb
from typing import Any, Dict

from pathlib import Path
import sys
from rich import print

# SECTION: resolve the local development package
# NOTE: Direct execution should use this checkout, not an older installation.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# SECTION: initialize the dataset reference
EXAMPLE_DIR = Path(__file__).resolve().parent

# ! yaml
YAML_PATH = EXAMPLE_DIR / "table-dataset-source.yaml"
# ! csv
CSV_PATH_1 = EXAMPLE_DIR / "VLE-DATASET.csv"
CSV_PATH_2 = EXAMPLE_DIR / "DENSITY-DATASET.csv"
CSV_PATH_3 = EXAMPLE_DIR / "KINETIC-DATASET.csv"
CSV_PATH_4 = EXAMPLE_DIR / "ADSORPTION-DATASET.csv"
CSV_PATH_5 = EXAMPLE_DIR / "MEMBRANE-DATASET.csv"

# custom reference
REFERENCE: Dict[str, Any] = {
    'reference': [YAML_PATH],
    'tables': [CSV_PATH_1, CSV_PATH_2, CSV_PATH_3, CSV_PATH_4, CSV_PATH_5]
}

thermo_db = ptdb.init(custom_reference=REFERENCE)

print("Databooks:")
print(thermo_db.list_databooks())
print("Dataset tables:")
print(thermo_db.list_tables("DATASET-EXAMPLE"))
print("VLE table information:")
print(
    thermo_db.table_info(
        databook="DATASET-EXAMPLE",
        table="VLE-DATASET",
        res_format="dict",
    )
)

# SECTION: load the validated runtime dataset
dataset: TableDataset = thermo_db.dataset_load(
    databook="DATASET-EXAMPLE",
    table="VLE-DATASET",
)

print("Shape:", dataset.shape)
print("Columns:", dataset.columns)
print("Symbols:", dataset.symbols)
print("Units:", dataset.units)
print("Roles:", dataset.roles)
print("Dataset identifiers:", dataset.dataset_ids)
print("Input columns:", dataset.input_columns)
print("Output columns:", dataset.output_columns)
print("Complete dataset:")
print(dataset.dataframe)


# SECTION: access columns by exact name or symbol
# NOTE: Both requests resolve to the same Temperature column.
print("Temperature by column name:")
print(dataset.get("Temperature"))
print("Temperature by symbol:")
print(dataset.get("T"))


# SECTION: select one dataset identity and exact conditions
binary_id = "methanol|water"
print(f"Rows for {binary_id}:")
print(dataset.get_dataset(binary_id))
print("Ordered entity positions:", dataset.get_dataset_positions(binary_id))

print("Methanol/water observation at 298.15 K:")
print(dataset.filter(Id=binary_id, T=298.15))


# SECTION: inspect model-oriented views
# ! Structural No. and Id columns are excluded from inputs and outputs.
print("Inputs:")
print(dataset.inputs)
print("Outputs:")
print(dataset.outputs)
