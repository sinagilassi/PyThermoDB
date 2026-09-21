"""Use explicit positional symmetry when looking up interaction data.

The source row remains ordered. Symmetry is a caller-declared lookup rule,
not a change to the stored table.
"""

from __future__ import annotations
from pythermodb_settings.models import Component
from pyThermoDB.core import TableInteractionData
import pyThermoDB as ptdb

from pathlib import Path
import sys
from rich import print

# SECTION: resolve the local development package
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# SECTION: load the ordered source table
EXAMPLE_DIR = Path(__file__).resolve().parent
REFERENCE = {"reference": [str(EXAMPLE_DIR / "interaction-format-1.yaml")]}
thermo_db = ptdb.init(custom_reference=REFERENCE)
interaction_data = thermo_db.interaction_data_load(
    databook="PITZER-EXAMPLE",
    table="Pitzer ternary interaction parameters",
)
if not isinstance(interaction_data, TableInteractionData):
    raise TypeError("Expected a TableInteractionData object.")

# The source row is potassium | sodium | chloride. The consuming model may
# declare the two cation-like positions (0 and 1) interchangeable for psi.
source_mixture = "potassium-ion|sodium-ion|chloride-ion"
reversed_first_group = "sodium-ion|potassium-ion|chloride-ion"


# SECTION: strict versus explicitly symmetric lookup
print("Stored psi:", interaction_data.get("psi", source_mixture))
print(
    "Strict reversed lookup:",
    interaction_data.get("psi", reversed_first_group),
)
print(
    "Symmetric first-two-positions lookup:",
    interaction_data.get(
        "psi",
        reversed_first_group,
        symmetric_groups=[(0, 1)],
    ),
)

# Position 2 is not symmetric, so this must not resolve to the source row.
print(
    "Changing the fixed position:",
    interaction_data.get(
        "psi",
        "chloride-ion|potassium-ion|sodium-ion",
        symmetric_groups=[(0, 1)],
        default="not found",
    ),
)


# SECTION: the same option is available on convenience APIs
print(
    "i() symmetric lookup:",
    interaction_data.i(
        "psi",
        reversed_first_group,
        symmetric_groups=[(0, 1)],
    )["value"],
)
print(
    "iis() symmetric lookup:",
    interaction_data.iis(
        "psi",
        [reversed_first_group],
        symmetric_groups=[(0, 1)],
    ),
)


# SECTION: Component objects retain their supplied sequence
sodium = Component(name="sodium-ion", formula="Na{+}", state="aq")
potassium = Component(name="potassium-ion", formula="K{+}", state="aq")
chloride = Component(name="chloride-ion", formula="Cl{-}", state="aq")
print(
    "Component symmetric lookup:",
    interaction_data.get_from_components(
        "psi",
        [sodium, potassium, chloride],
        component_key="Name",
        symmetric_groups=[(0, 1)],
    ),
)

# Symmetry is runtime-only: interaction_data.to_dict() still contains only
# the original potassium | sodium | chloride source row.
