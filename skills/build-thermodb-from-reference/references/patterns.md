# pyThermoDB Reference Build Patterns

Use `../scripts/validate_reference_build.py` for repeatable smoke tests before or after adapting these patterns in project code.

## Component Builds

Import the builder and optional return type from `pyThermoDB`:

```python
from pyThermoDB import build_component_thermodb_from_reference, ComponentThermoDB
```

Call with a component identity and reference YAML content or path:

```python
thermodb_component: ComponentThermoDB | None = build_component_thermodb_from_reference(
    component_name="carbon dioxide",
    component_formula="CO2",
    component_state="g",
    reference_content=REFERENCE_CONTENT,
    mode="log",
)
```

For mismatched states on selected properties, pass symbols in `ignore_state_props`, for example `["Cp_IG"]` or `["Cp_IG", "VaPr"]`.

Save by adding:

```python
thermodb_save=True,
thermodb_save_path=parent_path,
thermodb_name="CO2_thermodb",
```

Use the built object through `thermodb_component.thermodb`. Validate with `thermodb_component.thermodb.check()`.

## Mixture Builds

Import `Component` from `pythermodb_settings.models` and create the mixture list explicitly:

```python
from pyThermoDB import build_mixture_thermodb_from_reference, MixtureThermoDB
from pythermodb_settings.models import Component

methanol = Component(name="methanol", formula="CH3OH", state="l")
ethanol = Component(name="ethanol", formula="C2H5OH", state="l")
mixture = [methanol, ethanol]
```

Build a binary mixture:

```python
thermodb_mixture: MixtureThermoDB | None = build_mixture_thermodb_from_reference(
    components=mixture,
    reference_content=REFERENCE_CONTENT,
)
```

For multi-component references with pair-specific matrix tables, pass `mixture_names`:

```python
thermodb_mixture = build_mixture_thermodb_from_reference(
    components=[methanol, ethanol, methane],
    reference_content=REFERENCE_CONTENT,
    mixture_names=["methanol | ethanol", "methane | ethanol"],
    verbose=True,
)
```

For matrix properties whose state should be ignored, pass symbols such as `ignore_state_props=["a"]`.

## Constants Builds

Import:

```python
from pyThermoDB import build_constants_thermodb_from_reference, ConstantsThermoDB
from pyThermoDB.core import TableConstants
```

Build all constants tables from inline YAML or a file path:

```python
thermodb_constants: ConstantsThermoDB | None = build_constants_thermodb_from_reference(
    reference_content=external_ref_path,
)
```

Select by table:

```python
thermodb_constants = build_constants_thermodb_from_reference(
    reference_content=external_ref_path,
    databook_name="CUSTOM-REF-1",
    table_name="Custom-Constants",
)
```

Select by one or more constant symbols:

```python
thermodb_constants = build_constants_thermodb_from_reference(
    reference_content=external_ref_path,
    constants=["R", "dH_rxn", "dG_rxn"],
    verbose=True,
)
```

Retrieve constants:

```python
custom_constants: TableConstants = thermodb_constants.thermodb.select_constant(
    "CUSTOM-REF-1::Custom-Constants"
)
R = custom_constants.get_constant("R", message="gas constant")
dH = custom_constants.get_constant("dH_rxn", message="enthalpy of reaction")
```

## Equation and Data Usage

Use `.select(...)` with the full key when a specific equation or data table is required.

For `TableData`, select a data table and retrieve properties by column name or symbol:

```python
from pyThermoDB.core import TableData

general_data = thermodb.select("CUSTOM-REF-1::general-data")
if not isinstance(general_data, TableData):
    raise TypeError("Expected TableData")

print(general_data.prop_data)
enthalpy = general_data.get_property("EnFo", message="enthalpy of formation")
mw = general_data.get_property("MW", message="molecular weight")
```

Use `thermodb.retrieve(...)` for the compact source-string form:

```python
enthalpy = thermodb.retrieve(
    "CUSTOM-REF-1::general-data | EnFo",
    message="enthalpy of formation",
)
```

For `TableEquation`, select an equation table and calculate values:

```python
from pyThermoDB.core import TableEquation

cp_table = thermodb.select("CUSTOM-REF-1::ideal-gas-heat-capacity")
if not isinstance(cp_table, TableEquation):
    raise TypeError("Expected TableEquation")

print(cp_table.summary)
value = cp_table.cal(T=300)
```

Use `.select_function(function_name=...)` for function lookup by table/function name when available.

## Matrix Data Usage

Load saved ThermoDB files with `pyThermoDB.load_thermodb(path)`.

Use `check_properties()` to list available properties and `check_property(full_key)` to load one:

```python
import pyThermoDB as ptdb
from pyThermoDB.core import TableMatrixData

thermodb = ptdb.load_thermodb(thermodb_path)
matrix = thermodb.check_property("CUSTOM-REF-1::NRTL Non-randomness parameters-2")
if not isinstance(matrix, TableMatrixData):
    raise TypeError("Expected TableMatrixData")
```

Supported matrix lookup patterns from `examples/configs`:

```python
matrix.mat("a", ["ethanol", "methanol"])
matrix.ij("a | ethanol | methanol")
matrix.ijs("a | ethanol | methanol")

thermodb.retrieve(
    "CUSTOM-REF-1::NRTL Non-randomness parameters-2 | a_i_j | ethanol | methanol",
    message="NRTL a value ethanol-methanol",
)
thermodb.retrieve(
    "CUSTOM-REF-1::NRTL Non-randomness parameters-2 | a_ethanol_methanol",
    message="NRTL a value ethanol-methanol",
)
```

## Mapper Workflows

Use mapper workflows when reference matching needs to be inspected, customized, or split into mapping and build phases.

Component mapper imports:

```python
from pyThermoDB import check_and_build_component_thermodb
from pyThermoDB.references import component_reference_mapper
from pythermodb_settings.models import Component, ComponentReferenceThermoDB
```

Mixture mapper imports:

```python
from pyThermoDB import check_and_build_mixture_thermodb
from pyThermoDB.references import mixture_reference_mapper
from pythermodb_settings.models import Component, MixtureReferenceThermoDB
```

Mapper builders expect `custom_reference = {"reference": [REFERENCE_CONTENT]}` and `reference_config` from `mapped.reference_thermodb.configs`. Forward `mapped.reference_thermodb.ignore_labels` into `ignore_state_props`.
