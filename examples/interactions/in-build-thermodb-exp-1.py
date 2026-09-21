"""Build ThermoDB objects from scalar interaction-data tables."""

from rich import print
from pythermodb_settings.models import Component
from pyThermoDB.core import TableInteractionData
import pyThermoDB as ptdb
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


EXAMPLE_DIR = Path(__file__).resolve().parent
REFERENCE_PATH = EXAMPLE_DIR / "interaction-format-1.yaml"
REFERENCE = {"reference": [str(REFERENCE_PATH)]}

sodium = Component(name="sodium-ion", formula="Na{+}", state="aq")
potassium = Component(name="potassium-ion", formula="K{+}", state="aq")
chloride = Component(name="chloride-ion", formula="Cl{-}", state="aq")
components = [sodium, potassium, chloride]

# Source order is potassium|sodium|chloride, while the requested components
# are sodium, potassium, chloride. The builder matches the exact set regardless
# of order and retains the source order for later scalar lookup.
interaction_config = {
    "pitzer-interactions": {
        "databook": "PITZER-EXAMPLE",
        "table": "Pitzer ternary interaction parameters",
    }
}
built = ptdb.build_interaction_thermodb(
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
