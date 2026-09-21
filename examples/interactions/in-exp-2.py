"""Build interaction data through ThermoDB's component-object dispatch."""

from __future__ import annotations

from pathlib import Path
import sys

# SECTION: resolve the local development package
# NOTE: Direct example execution otherwise can import an older installed package.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pyThermoDB as ptdb
from pyThermoDB.core import TableInteractionData
from pythermodb_settings.models import Component


# SECTION: initialize the interaction reference
EXAMPLE_DIR = Path(__file__).resolve().parent
REFERENCE = {"reference": [str(EXAMPLE_DIR / "interaction-format-1.yaml")]}
thermo_db = ptdb.init(custom_reference=REFERENCE)

print(thermo_db.list_databooks())
print(thermo_db.list_tables("PITZER-EXAMPLE"))


# SECTION: declare the requested interaction participants
# NOTE: This request intentionally differs from the source row order.
sodium = Component(name="sodium-ion", formula="Na{+}", state="aq")
potassium = Component(name="potassium-ion", formula="K{+}", state="aq")
chloride = Component(name="chloride-ion", formula="Cl{-}", state="aq")
components = [sodium, potassium, chloride]


# SECTION: build through the high-level component dispatcher
# ! Default interaction discovery ignores source order but requires the exact set.
interaction_data = thermo_db.build_components_thermo_property(
    components=components,
    databook="PITZER-EXAMPLE",
    table="Pitzer ternary interaction parameters",
    interaction_component_key="Name",
    interaction_respect_order=False,
)
if not isinstance(interaction_data, TableInteractionData):
    raise TypeError("Expected build_components_thermo_property() to return TableInteractionData.")

print("Interaction symbols:", interaction_data.interaction_symbol)
print("Interaction orders:", interaction_data.interaction_orders)
print(interaction_data.interaction_data_structure())


# SECTION: access values with the stored, order-preserving mixture key
source_mixture = "potassium-ion|sodium-ion|chloride-ion"
print("psi:", interaction_data.get("psi", source_mixture))
print("zeta:", interaction_data.get("zeta", source_mixture))
print("Complete row:", interaction_data.get_mixture(source_mixture))

# NOTE: Runtime Component lookup preserves the passed participant sequence.
print(
    "psi from source-order Components:",
    interaction_data.get_from_components("psi", [potassium, sodium, chloride]),
)


# SECTION: preserve explicit zero and null values
print("Binary psi zero:", interaction_data.get("psi", "sodium-ion|chloride-ion"))
print(
    "Ternary zeta null:",
    interaction_data.get("zeta", "sodium-ion|calcium-ion|chloride-ion"),
)

# ? A model may consume these scalar interaction values without matrix expansion.

# SECTION: build and persist a ThermoDB payload
# ! Interaction data is registered as a scalar property, never as matrix data.
built_thermodb = ptdb.build_thermodb(
    thermodb_name="thermodb_pitzer_interactions",
    message="Pitzer scalar interaction-data example",
)
if not built_thermodb.add_data("pitzer_interactions", interaction_data):
    raise RuntimeError("Could not register interaction data in the ThermoDB builder.")
if not built_thermodb.build():
    raise RuntimeError("Could not build the ThermoDB interaction-data payload.")

print("Registered properties:", built_thermodb.check_properties())
print("Build details:", built_thermodb.build_details())

# NOTE: Save beside the example, then verify the runtime type survives loading.
THERMODB_FILE = "thermodb_pitzer_interactions.pkl"
built_thermodb.save(THERMODB_FILE, file_path=str(EXAMPLE_DIR))
loaded_thermodb = ptdb.load_thermodb(str(EXAMPLE_DIR / THERMODB_FILE))
loaded_interaction_data = loaded_thermodb.select_property("pitzer_interactions")
if not isinstance(loaded_interaction_data, TableInteractionData):
    raise TypeError("Loaded ThermoDB did not retain TableInteractionData.")

print("Reloaded psi:", loaded_interaction_data.get("psi", source_mixture))