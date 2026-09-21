"""Build interaction data through ThermoDB's component-object dispatch."""

from __future__ import annotations
from pythermodb_settings.models import Component
from pyThermoDB.core import TableInteractionData
import pyThermoDB as ptdb
from rich import print

from pathlib import Path
import sys

# SECTION: resolve the local development package
# NOTE: Direct example execution otherwise can import an older installed package.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# SECTION: initialize the interaction reference
EXAMPLE_DIR = Path(__file__).resolve().parent


# SECTION: declare the requested interaction participants
# NOTE: This request intentionally differs from the source row order.
sodium = Component(name="sodium-ion", formula="Na{+}", state="aq")
potassium = Component(name="potassium-ion", formula="K{+}", state="aq")
chloride = Component(name="chloride-ion", formula="Cl{-}", state="aq")
components = [sodium, potassium, chloride]


# SECTION: access values with the stored, order-preserving mixture key
source_mixture = "potassium-ion|sodium-ion|chloride-ion"

# NOTE: Save beside the example, then verify the runtime type survives loading.
THERMODB_FILE = "thermodb_pitzer_interactions.pkl"

# ! load thermodb from the saved file
loaded_thermodb = ptdb.load_thermodb(str(EXAMPLE_DIR / THERMODB_FILE))


print("Registered properties:", loaded_thermodb.check_properties())
print("Build details:", loaded_thermodb.build_details())

loaded_interaction_data = loaded_thermodb.select_property(
    "pitzer_interactions")
if not isinstance(loaded_interaction_data, TableInteractionData):
    raise TypeError("Loaded ThermoDB did not retain TableInteractionData.")

print("Reloaded psi:", loaded_interaction_data.get("psi", source_mixture))
