"""Use TableDataset with several domain-neutral engineering datasets."""

from __future__ import annotations
from pyThermoDB.core import TableDataset
import pyThermoDB as ptdb

from pathlib import Path
import sys
from rich import print

# SECTION: resolve the local development package
# NOTE: Direct execution should use this checkout, not an older installation.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# SECTION: initialize the shared dataset reference
EXAMPLE_DIR = Path(__file__).resolve().parent
REFERENCE = {"reference": [str(EXAMPLE_DIR / "table-dataset.yaml")]}
thermo_db = ptdb.init(custom_reference=REFERENCE)


# SECTION: build a pure-fluid density dataset
density = thermo_db.build_dataset(
    databook="DATASET-EXAMPLE",
    table="DENSITY-DATASET",
)
if not isinstance(density, TableDataset):
    raise TypeError("Expected density to be a TableDataset.")

print("Density table:")
print(density.dataframe)
print("Water observations:")
print(density.get_dataset("water"))
print("All observations at 298.15 K:")
print(density.filter(T=298.15))

# NOTE: Symbols can select columns for NumPy export.
density_array = density.to_numpy(columns=["T", "P", "rho"])
print("Density model array [T, P, rho]:")
print(density_array)


# SECTION: build a reaction-kinetics dataset
kinetics = thermo_db.build_dataset(
    databook="DATASET-EXAMPLE",
    table="KINETIC-DATASET",
)
if not isinstance(kinetics, TableDataset):
    raise TypeError("Expected kinetics to be a TableDataset.")

print("Kinetics inputs:")
print(kinetics.inputs)
print("Kinetics outputs:")
print(kinetics.outputs)
print("Reaction-rate series by symbol:")
print(kinetics.get("r"))


# SECTION: build a membrane-performance dataset
membrane = thermo_db.build_dataset(
    databook="DATASET-EXAMPLE",
    table="MEMBRANE-DATASET",
)
if not isinstance(membrane, TableDataset):
    raise TypeError("Expected membrane to be a TableDataset.")

membrane_id = "CO2|CH4|Membrane-A"
print(f"Membrane rows for {membrane_id}:")
print(membrane.get_dataset(membrane_id))
print(
    "Membrane entity positions:",
    membrane.get_dataset_positions(membrane_id),
)
print("Permeability outputs:")
print(membrane.outputs)

# ? TableDataset preserves ordered identities and roles without interpreting
# ? whether an entity is a component, material, reaction, or piece of equipment.
