"""Build ThermoDB objects from scalar interaction-data tables."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rich import print
from pythermodb_settings.models import Component

import pyThermoDB as ptdb
from pyThermoDB import CompBuilder, build_interaction_thermodb
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

# Register the staged data so the CompBuilder discovery helpers can inspect it.
if not built.build():
    raise RuntimeError("The interaction ThermoDB could not be built.")

print("Interaction sources:", list(built.check_interaction_data()))
print(
    "Pitzer interaction source available:",
    built.is_interaction_data_available("pitzer-interactions"),
)

# Exact-name lookup and case-insensitive selection both return the original
# TableInteractionData object.
selected = built.check_interaction("pitzer-interactions")
if not isinstance(selected, TableInteractionData):
    raise TypeError("Expected selected interaction data.")
selected_case_insensitive = built.select_interaction(
    "  PITZER-INTERACTIONS  "
)
print(
    "Case-insensitive selection found the same source:",
    selected_case_insensitive is selected,
)

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
built_from_reference = ptdb.build_interaction_thermodb_from_reference(
    components=components,
    reference_content=REFERENCE_PATH.read_text(encoding="utf-8"),
)
if built_from_reference is None:
    raise RuntimeError("No interaction table was selected from the reference.")
print(
    "Auto-discovered interaction properties:",
    list(built_from_reference.thermodb.list_data()),
)
