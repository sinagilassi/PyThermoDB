"""Build a dataset ThermoDB from an explicit reference configuration."""

from __future__ import annotations

from pathlib import Path
import sys

# SECTION: resolve the local development package
# NOTE: Direct execution should use this checkout, not an older installation.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rich import print

from pyThermoDB import CompBuilder, TableDataset, build_dataset_thermodb


# SECTION: configure the CSV-backed dataset reference
EXAMPLE_DIR = Path(__file__).resolve().parent
REFERENCE_PATH = EXAMPLE_DIR / "table-dataset-source.yaml"
TABLE_PATHS = [
    EXAMPLE_DIR / "VLE-DATASET.csv",
    EXAMPLE_DIR / "DENSITY-DATASET.csv",
    EXAMPLE_DIR / "KINETIC-DATASET.csv",
    EXAMPLE_DIR / "ADSORPTION-DATASET.csv",
    EXAMPLE_DIR / "MEMBRANE-DATASET.csv",
]
CUSTOM_REFERENCE = {
    "reference": [str(REFERENCE_PATH)],
    "tables": [str(path) for path in TABLE_PATHS],
}

# NOTE: Source names become the property names stored in CompBuilder.
DATASET_CONFIG = {
    "density-observations": {
        "databook": "DATASET-EXAMPLE",
        "table": "DENSITY-DATASET",
    },
    "kinetic-observations": {
        "databook": "DATASET-EXAMPLE",
        "table": "KINETIC-DATASET",
    },
}


# SECTION: build selected datasets into one ThermoDB
built: CompBuilder | None = build_dataset_thermodb(
    reference_config=DATASET_CONFIG,
    custom_reference=CUSTOM_REFERENCE,
    thermodb_name="engineering-datasets",
    message="Selected density and reaction-kinetics observations.",
)
if built is None:
    raise RuntimeError("No dataset tables were built.")

print("Build details:")
print(built.build_details())
print("Dataset sources:", list(built.check_properties()))


# SECTION: retrieve and query a stored TableDataset
density = built.check_property("density-observations")
if not isinstance(density, TableDataset):
    raise TypeError("Expected density-observations to be a TableDataset.")

print("Density dataset:")
print(density.dataframe)
print("Water observations:")
print(density.get_dataset("water"))
print("Model array [T, P, rho]:")
print(density.to_numpy(["T", "P", "rho"]))
