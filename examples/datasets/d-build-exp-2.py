"""Discover dataset tables and build a ThermoDB from reference content."""

from __future__ import annotations

from pathlib import Path
import sys

# SECTION: resolve the local development package
# NOTE: Direct execution should use this checkout, not an older installation.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rich import print

from pyThermoDB import (
    DatasetThermoDB,
    TableDataset,
    build_dataset_thermodb_from_reference,
)


# SECTION: load an inline-values reference
EXAMPLE_DIR = Path(__file__).resolve().parent
REFERENCE_PATH = EXAMPLE_DIR / "table-dataset.yaml"
REFERENCE_CONTENT = REFERENCE_PATH.read_text(encoding="utf-8")


# SECTION: discover and build every Dataset table
built: DatasetThermoDB | None = build_dataset_thermodb_from_reference(
    reference_content=REFERENCE_CONTENT,
    thermodb_name="all-engineering-datasets",
)
if built is None:
    raise RuntimeError("No dataset tables were discovered.")

dataset_thermodb = built.thermodb
print("Build details:")
print(dataset_thermodb.build_details())
print("Discovered dataset sources:")
print(list(dataset_thermodb.check_properties()))
print("Reference configurations:")
print(built.reference_thermodb.configs if built.reference_thermodb else {})


# SECTION: select one auto-discovered dataset
source_name = "DATASET-EXAMPLE::VLE-DATASET"
vle = dataset_thermodb.select_property(source_name)
if not isinstance(vle, TableDataset):
    raise TypeError(f"Expected {source_name} to be a TableDataset.")

mixture_id = "methanol|water"
print(f"VLE observations for {mixture_id}:")
print(vle.get_dataset(mixture_id))
print("VLE inputs:")
print(vle.inputs)
print("VLE outputs:")
print(vle.outputs)


# SECTION: restrict discovery to a single table
density_only = build_dataset_thermodb_from_reference(
    reference_content=REFERENCE_CONTENT,
    databook_name="DATASET-EXAMPLE",
    table_name="DENSITY-DATASET",
    thermodb_name="density-dataset",
)
if density_only is None:
    raise RuntimeError("The density dataset was not discovered.")

print("Restricted dataset sources:")
print(list(density_only.thermodb.check_properties()))
