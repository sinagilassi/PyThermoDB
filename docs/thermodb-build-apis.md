# 🏗️ ThermoDB Build APIs

This page focuses on high-level builders in `pyThermoDB.thermodb`.

## 🧰 Main Build Functions

- `build_component_thermodb(...)`
- `build_components_thermodb(...)`
- `build_component_thermodb_from_reference(...)`
- `check_and_build_component_thermodb(...)`
- `check_and_build_components_thermodb(...)`
- `build_mixture_thermodb_from_reference(...)`
- `check_and_build_mixture_thermodb(...)`
- `build_constant_thermodb(...)`
- `check_and_build_constant_thermodb(...)`
- `build_constants_thermodb_from_reference(...)`

## 🧪 Typical Single-Component Build

```python
import pyThermoDB as ptdb

reference_config = {
    "general": {"databook": "CUSTOM-REF-1", "table": "General-Data"},
    "vapor-pressure": {"databook": "CUSTOM-REF-1", "table": "Vapor-Pressure"},
}

thermodb = ptdb.build_component_thermodb(
    component_name="carbon dioxide",
    reference_config=reference_config,
    component_key="Name",
    thermodb_name="CO2_thermodb"
)
print(thermodb.check())
```

## 📦 Structured Return Models

The module exposes pydantic wrappers for build results:

- `ComponentThermoDB`
- `MixtureThermoDB`
- `ConstantsThermoDB`

Use these when you need metadata plus the built `CompBuilder` object.
