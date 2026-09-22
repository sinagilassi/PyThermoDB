"""Build and query a scalar multi-component interaction-data table."""

from __future__ import annotations

from pathlib import Path
import sys

# SECTION: resolve the local development package
# NOTE: Running an example by filename prepends its own directory to
# ``sys.path``. Prefer this checkout so an older installed distribution cannot
# shadow the interaction-data implementation used by the example.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pythermodb_settings.models import Component
from pyThermoDB.core import TableInteractionData
import pyThermoDB as ptdb
from rich import print
from typing import Any, Dict


# SECTION: initialize the example reference
EXAMPLE_DIR = Path(__file__).resolve().parent

# ! yaml
YAML_PATH = EXAMPLE_DIR / "interaction-format-source-1.yaml"
# ! csv
CSV_PATH = EXAMPLE_DIR / "interaction-format-1.csv"

# custom reference
REFERENCE: Dict[str, Any] = {
    'reference': [YAML_PATH],
    'tables': [CSV_PATH]
}

thermo_db = ptdb.init(custom_reference=REFERENCE)
print(thermo_db.table_info(
    "PITZER-EXAMPLE",
    "Pitzer ternary interaction parameters",
    res_format="dict",
))


# SECTION: declare the mixture components
sodium = Component(name="sodium-ion", formula="Na{+}", state="aq")
potassium = Component(name="potassium-ion", formula="K{+}", state="aq")
chloride = Component(name="chloride-ion", formula="Cl{-}", state="aq")

requested_components = [sodium, potassium, chloride]
source_order_components = [potassium, sodium, chloride]


# SECTION: discover a mixture before building the table
# NOTE: Default discovery ignores participant order but requires the exact set.
availability = thermo_db.check_interaction_availability(
    components=requested_components,
    databook="PITZER-EXAMPLE",
    table="Pitzer ternary interaction parameters",
)
print("Unordered availability:", availability)
assert availability["availability"] is True

# ! Strict discovery rejects the request because the reference uses K|Na|Cl.
strict_availability = thermo_db.check_interaction_availability(
    components=requested_components,
    databook="PITZER-EXAMPLE",
    table="Pitzer ternary interaction parameters",
    respect_order=True,
)
print("Strict-order availability:", strict_availability)
assert strict_availability["availability"] is False


# SECTION: build the full interaction-data runtime object
interaction_data = thermo_db.build_interaction_data(
    components=requested_components,
    databook="PITZER-EXAMPLE",
    table="Pitzer ternary interaction parameters",
)
if not isinstance(interaction_data, TableInteractionData):
    raise TypeError("Expected a TableInteractionData object.")

print("Interaction symbols:", interaction_data.interaction_symbol)
print("Interaction orders:", interaction_data.interaction_orders)
print(interaction_data.interaction_data_structure())


# SECTION: access scalar values by stored ordered Mixture IDs
source_mixture = "potassium-ion|sodium-ion|chloride-ion"
print("psi:", interaction_data.get("psi", source_mixture))
print("zeta:", interaction_data.get("zeta", source_mixture))
print("Complete row:", interaction_data.get_mixture(source_mixture))

# NOTE: Core lookup preserves source order, so Component lookup uses K|Na|Cl here.
print(
    "psi from Components:",
    interaction_data.get_from_components("psi", source_order_components),
)


# SECTION: demonstrate null and explicit-zero semantics
binary_mixture = "sodium-ion|chloride-ion"
ternary_with_null = "sodium-ion|calcium-ion|chloride-ion"
print("Explicit binary psi zero:", interaction_data.get("psi", binary_mixture))
print("Unavailable ternary zeta:", interaction_data.get("zeta", ternary_with_null))
print(
    "Ternary row without nulls:",
    interaction_data.get_mixture(ternary_with_null, include_null=False),
)


# SECTION: select and inspect records
print("Available psi records:", interaction_data.get_property("psi"))
print(
    "All records containing sodium-ion:",
    interaction_data.select(contains=["sodium-ion"], include_null=True),
)
print("All ternary psi values:", interaction_data.select(
    property_name="psi", order=3))

# ? A downstream Pitzer model may convert these scalar records for its own needs.
# ! TableInteractionData itself never materializes a matrix or tensor.
