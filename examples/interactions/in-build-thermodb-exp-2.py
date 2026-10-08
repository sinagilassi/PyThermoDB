"""Build ThermoDB objects from scalar interaction-data tables."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rich import print
from pythermodb_settings.models import Component

from pyThermoDB import (
    CompBuilder,
    MixtureThermoDB,
    build_interaction_thermodb,
    build_interaction_thermodb_from_reference,
)
from pyThermoDB.core import TableInteractionData

# ----------------------------------------------
# SECTION: Load reference and define components
# ----------------------------------------------
EXAMPLE_DIR = Path(__file__).resolve().parent
REFERENCE_PATH = EXAMPLE_DIR / "interaction-format-1.yaml"
REFERENCE = {"reference": [str(REFERENCE_PATH)]}

# NOTE: Define components using pythermodb_settings models
sodium = Component(name="sodium-ion", formula="Na{+}", state="aq")
potassium = Component(name="potassium-ion", formula="K{+}", state="aq")
chloride = Component(name="chloride-ion", formula="Cl{-}", state="aq")
components = [sodium, potassium, chloride]

# Source order is potassium|sodium|chloride, while the requested components
# are sodium, potassium, chloride. The builder matches the exact set regardless
# of order and retains the source order for later scalar lookup.

# NOTE: reference config
interaction_config = {
    "pitzer-interactions": {
        "databook": "PITZER-EXAMPLE",
        "table": "Pitzer ternary interaction parameters",
    }
}

# NOTE: build interaction thermodb from the reference config
built: CompBuilder | None = build_interaction_thermodb(
    components=components,
    reference_config=interaction_config,
    custom_reference=REFERENCE,
)
if built is None:
    raise RuntimeError("No interaction records were selected.")

selected = built.list_data()["pitzer-interactions"]
if not isinstance(selected, TableInteractionData):
    raise TypeError("Expected selected interaction data.")

source_mixture = "potassium-ion|sodium-ion|chloride-ion"
print("Selected ordered mixtures:", selected.mixtures)
print("psi using the retained source order:",
      selected.get("psi", source_mixture))
print(
    "psi using request order (no implicit symmetry):",
    selected.get("psi", "sodium-ion|potassium-ion|chloride-ion"),
)

# This variant discovers every Interaction-Data table in the YAML reference
# and keeps the same exact-set, order-insensitive build-time selection rule.
built_from_reference: MixtureThermoDB | None = build_interaction_thermodb_from_reference(
    components=components,
    reference_content=REFERENCE_PATH.read_text(encoding="utf-8"),
)
if built_from_reference is None:
    raise RuntimeError("No interaction table was selected from the reference.")

interaction_builder = built_from_reference.thermodb
if not interaction_builder.build():
    raise RuntimeError("The discovered interaction ThermoDB could not be built.")

print(
    "Auto-discovered interaction sources:",
    list(interaction_builder.check_interaction_data()),
)
print(
    "Interaction source details:",
    interaction_builder.all_interaction_data_details(),
)
print(
    "Interaction symbols:",
    interaction_builder.all_interaction_data_identifiers(),
)
print(
    "Interaction symbol labels:",
    interaction_builder.all_interaction_data_id_labels(),
)

print("Built from reference:")
print(built_from_reference)
