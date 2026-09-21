"""Exercise every public TableInteractionData access and inspection API."""

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


# SECTION: load an interaction table
EXAMPLE_DIR = Path(__file__).resolve().parent
REFERENCE = {"reference": [str(EXAMPLE_DIR / "interaction-format-1.yaml")]}
thermo_db = ptdb.init(custom_reference=REFERENCE)
interaction_data = thermo_db.interaction_data_load(
    databook="PITZER-EXAMPLE",
    table="Pitzer ternary interaction parameters",
)
if not isinstance(interaction_data, TableInteractionData):
    raise TypeError("Expected a TableInteractionData object.")

source_mixture = "potassium-ion|sodium-ion|chloride-ion"
binary_mixture = "sodium-ion|chloride-ion"
null_mixture = "sodium-ion|calcium-ion|chloride-ion"

sodium = Component(name="sodium-ion", formula="Na{+}", state="aq")
potassium = Component(name="potassium-ion", formula="K{+}", state="aq")
chloride = Component(name="chloride-ion", formula="Cl{-}", state="aq")
source_components = [potassium, sodium, chloride]


# SECTION: structural properties
print(f"[blue]Structural Properties[/blue]")
print("interaction_symbol:", interaction_data.interaction_symbol)
print("table_structure:", interaction_data.table_structure)
print("mixtures:", interaction_data.mixtures)
print("mixture_count:", interaction_data.mixture_count)
print("interaction_orders:", interaction_data.interaction_orders)


# SECTION: scalar and row access
print(f"[yellow]Scalar and Row Access[/yellow]")
# NOTE: Whitespace is trimmed, while participant order remains significant.
print("get string:", interaction_data.get("psi", source_mixture))
print(
    "get sequence:",
    interaction_data.get(
        "psi", ["potassium-ion", " sodium-ion ", "chloride-ion"]),
)
print("get default:", interaction_data.get(
    "psi", "unknown|mixture", default="not found"))
print("require:", interaction_data.require("zeta", source_mixture))
print("has value:", interaction_data.has("zeta", source_mixture))
print("has null value:", interaction_data.has("zeta", null_mixture))
print(
    "has declared null:",
    interaction_data.has("zeta", null_mixture, require_value=False),
)
print("get_mixture:", interaction_data.get_mixture(null_mixture))
print(
    "get_mixture without null:",
    interaction_data.get_mixture(null_mixture, include_null=False),
)
print("get_property:", interaction_data.get_property("psi"))
print("get_property with null:",
      interaction_data.get_property("zeta", include_null=True))
print("explicit zero:", interaction_data.get("psi", binary_mixture))


# SECTION: filtered interaction access
print(f"[green]Filtered Interaction Access[/green]")
print("select all:", interaction_data.select())
print("select property:", interaction_data.select(property_name="psi"))
print(
    "select contains sodium:",
    interaction_data.select(contains=["sodium-ion"], include_null=True),
)
print("select ternary:", interaction_data.select(order=3, include_null=True))
print(
    "select ternary zeta:",
    interaction_data.select(property_name="zeta", order=3, include_null=True),
)
print("interaction_order:", interaction_data.interaction_order(source_mixture))


# SECTION: compact i and iis accessors
print(f"[magenta]Compact i and iis Accessors[/magenta]")
# NOTE: ``i`` accepts the same compact property-and-participants style as ``ij``.
print(
    "i compact query:",
    interaction_data.i("psi | potassium-ion | sodium-ion | chloride-ion"),
)
print(
    "i explicit mixture:",
    interaction_data.i("zeta", source_mixture, message="Pitzer zeta value"),
)
# ! ``iis`` retrieves scalar interaction records only; it does not expand pairs.
print(
    "iis requested mixtures:",
    interaction_data.iis("psi", [source_mixture, binary_mixture]),
)
print("iis all zeta values:", interaction_data.iis("zeta", include_null=True))

# SECTION: Component-object access
print(f"[cyan]Component-object Access[/cyan]")

# ! Component lookup uses source sequence; it does not sort runtime keys.
print(
    "get_from_components automatic:",
    interaction_data.get_from_components("psi", source_components),
)
print(
    "get_from_components explicit:",
    interaction_data.get_from_components(
        "psi", source_components, component_key="Name"
    ),
)
print(
    "get_mixture_from_components:",
    interaction_data.get_mixture_from_components(
        source_components, component_key="Name"
    ),
)


# SECTION: table, metadata, and serialization access
print(f"[red]Table, Metadata, and Serialization Access[/red]")
print("get_interaction_table all:")
print(interaction_data.get_interaction_table(mode="all"))
print("get_interaction_table available:")
print(interaction_data.get_interaction_table(mode="available"))
print("interaction_data_structure:")
print(interaction_data.interaction_data_structure())
print("get_interaction_data_info:", interaction_data.get_interaction_data_info())
print("to_dict:", interaction_data.to_dict())

# ? The returned DataFrames and dictionaries are copies; callers may inspect them safely.
