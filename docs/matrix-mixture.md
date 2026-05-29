# 🧪 Matrix & Mixture Data

Matrix workflows are typically used for mixture interaction parameters.

## 🧱 Build a Matrix Property

```python
import pyThermoDB as ptdb
from pythermodb_settings.models import Component

tdb = ptdb.init(custom_reference={"reference": ["path/to/matrix-format-2.yml"]})

methanol = Component(name="methanol", formula="CH3OH", state="l")
ethanol = Component(name="ethanol", formula="C2H5OH", state="l")

nrtl_alpha = tdb.build_components_thermo_property(
    [methanol, ethanol],
    databook="NRTL",
    table="Non-randomness parameters of the NRTL equation-3",
    component_key="Name-State",
    ignore_component_state=True
)
print(nrtl_alpha.matrix_data_structure())
```

## ✅ Mixture Availability Checks

```python
print(tdb.is_binary_mixture_available(
    components=[methanol, ethanol],
    databook="NRTL",
    table="Non-randomness parameters of the NRTL equation-3",
    ignore_component_state=True
))

print(tdb.check_mixtures_availability(
    components=[methanol, ethanol],
    databook="NRTL",
    table="Non-randomness parameters of the NRTL equation-3",
    component_key="Name-State",
    mixture_key="Name",
    delimiter="|",
    ignore_component_state=True
))
```

## 🔢 Access Matrix Values

```python
comp1, comp2 = "methanol", "ethanol"
mixture_name = f"{comp1} | {comp2}"

print(nrtl_alpha.get_matrix_property("a_i_j", [comp1, comp2]))
print(nrtl_alpha.ij(f"a_{comp1}_{comp2}", mixture_name=mixture_name))
print(nrtl_alpha.mat("a", [comp1, comp2]))
```

## ⚠️ Gotchas

!!! warning "Component keys"
    Mixture methods commonly require `Name-State` or `Formula-State`, while
    older single-component methods may use plain `Name` or `Formula`.

!!! warning "Delimiter and naming"
    Mixture matching depends on exact delimiter and normalized names (for example
    `"methanol | ethanol"` when delimiter is `"|"`).
