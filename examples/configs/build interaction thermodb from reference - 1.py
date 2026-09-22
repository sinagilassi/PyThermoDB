"""Build scalar Pitzer interaction data from an in-memory reference."""

from pythermodb_settings.models import Component
from pyThermoDB import TableInteractionData, build_interaction_thermodb_from_reference
from rich import print
import sys
from pathlib import Path

# Prefer this checkout when the example is run directly from any directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# SECTION: reference content
# Pitzer interaction parameters are scalar records, not matrix parameters.
# The component order in a Mixture row is retained for subsequent lookup.
REFERENCE_CONTENT = """
REFERENCES:
  PITZER-EXAMPLE:
    DATABOOK-ID: 1
    TABLES:
      Pitzer interaction parameters:
        TABLE-ID: 1
        DESCRIPTION: Scalar binary and ternary Pitzer interaction parameters.
        INTERACTION-SYMBOL: [psi, zeta]
        STRUCTURE:
          COLUMNS: [No., Mixture, psi, zeta]
          SYMBOL: [None, None, psi, zeta]
          UNIT: [None, None, 1, 1]
        VALUES:
          # This is the row selected by the components declared below.
          - [1, "potassium-ion|sodium-ion|chloride-ion", -0.0018, 0.25]
          # These rows illustrate that a table may contain other interactions.
          - [2, "sodium-ion|calcium-ion|chloride-ion", 0.0032, null]
          - [3, "sodium-ion|chloride-ion", 0.0, 0.015]
"""

# symmetric interactions may be included here as well.
# - [4, "sodium-ion|potassium-ion|chloride-ion", 0.0018, -0.25]

# SECTION: requested interaction participants
sodium = Component(name="sodium-ion", formula="Na{+}", state="aq")
potassium = Component(name="potassium-ion", formula="K{+}", state="aq")
chloride = Component(name="chloride-ion", formula="Cl{-}", state="aq")
components = [sodium, potassium, chloride]


# SECTION: build every matching Interaction-Data table from the reference
# Matching is based on the component set, so request order need not match source
# order. The selected TableInteractionData still preserves the source order.
interaction_thermodb = build_interaction_thermodb_from_reference(
    components=components,
    reference_content=REFERENCE_CONTENT,
    component_key="Name",
)
if interaction_thermodb is None:
    raise RuntimeError(
        "No Pitzer interaction data was selected from the reference.")

print(f"interaction_thermodb: {type(interaction_thermodb)}")
print("thermodb checks:", interaction_thermodb.thermodb.check())
print("properties:", list(interaction_thermodb.thermodb.list_data()))


# SECTION: retrieve Pitzer scalar interaction data
property_name = "PITZER-EXAMPLE::Pitzer interaction parameters"
interaction_data = interaction_thermodb.thermodb.select_property(property_name)
if not isinstance(interaction_data, TableInteractionData):
    raise TypeError("Expected a TableInteractionData object.")

source_mixture = "potassium-ion|sodium-ion|chloride-ion"
print("selected ordered mixtures:", interaction_data.mixtures)
print("interaction symbols:", interaction_data.interaction_symbol)
print("psi:", interaction_data.get("psi", source_mixture))
print("zeta:", interaction_data.get("zeta", source_mixture))
print("complete Pitzer record:", interaction_data.get_mixture(source_mixture))

# Source order is meaningful during lookup; no symmetry is assumed by default.
request_order = "sodium-ion|potassium-ion|chloride-ion"
print("psi in request order (not stored):",
      interaction_data.get("psi", request_order))

# symmetric order lookup
symmetric_order = "sodium-ion|potassium-ion|chloride-ion"
print("psi in symmetric order:",
      interaction_data.get("psi", source_mixture, symmetric_groups=[[0, 1]]))
print("zeta in symmetric order:",
      interaction_data.get("zeta", symmetric_order))
