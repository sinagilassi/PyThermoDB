---
name: build-thermodb-from-reference
description: Build pyThermoDB component, mixture, and constants ThermoDB objects from inline or file-based reference YAML. Use when Codex needs to write, update, or debug examples or application code using build_component_thermodb_from_reference, build_mixture_thermodb_from_reference, build_constants_thermodb_from_reference, mapped reference builders, saved .pkl ThermoDB files, constants tables, equations, or matrix property retrieval from examples/configs-style reference content.
---

# Build ThermoDB From Reference

## Workflow

1. Identify the target object:
   - Component: a single chemical species with `name`, `formula`, and `state`.
   - Mixture: a list of `pythermodb_settings.models.Component` objects.
   - Constants: one or more constants tables from a reference.
2. Inspect the reference source. Accept either inline YAML text or a YAML file path as `reference_content`.
3. Prefer the high-level builders unless the task specifically needs mapper-level control:
   - `build_component_thermodb_from_reference`
   - `build_mixture_thermodb_from_reference`
   - `build_constants_thermodb_from_reference`
4. Validate every successful build with `.thermodb.check()` for wrapper objects or `.check()` for directly returned ThermoDB instances.
5. When saving, pass `thermodb_save=True`, `thermodb_save_path=...`, and a clear `thermodb_name` when the default filename would be ambiguous.
6. For a repeatable smoke test, run `scripts/validate_reference_build.py` instead of writing a temporary validation script.

Read [references/patterns.md](references/patterns.md) when writing concrete pyThermoDB code for component, mixture, constants, or matrix-table workflows.

## Validation Script

Use `scripts/validate_reference_build.py` to verify that a reference can build a component, mixture, or constants ThermoDB and print the resulting `.check()` output.

Examples:

```bash
./.venv/Scripts/python.exe skills/build-thermodb-from-reference/scripts/validate_reference_build.py constants --reference examples/external-ref/source-ref-1.yml --constants R dH_rxn
python skills/build-thermodb-from-reference/scripts/validate_reference_build.py component --reference examples/external-ref/source-ref-1.yml --name "carbon dioxide" --formula CO2 --state g
python skills/build-thermodb-from-reference/scripts/validate_reference_build.py constants --reference examples/external-ref/source-ref-1.yml --constants R dH_rxn
python skills/build-thermodb-from-reference/scripts/validate_reference_build.py mixture --reference ref.yml --components components.json --mixture-names "methanol | ethanol"
```

Prefer the repo virtualenv (`.venv/Scripts/python.exe` on Windows) when validating inside this repository, because global Python may import incompatible installed pyThermoDB dependencies.

For `--components`, pass either a JSON string or a JSON file containing a list of objects with `name`, `formula`, and `state`.

## Builder Patterns

Use `ComponentThermoDB`, `MixtureThermoDB`, or `ConstantsThermoDB` annotations as optional clarity, but always handle `None` because build helpers return `None` on failed construction.

Use `ignore_state_props` when a property should match by name/formula even when the reference row state differs from the requested component or mixture member. Use `ignore_component_state=True` only in mapper workflows or when all state checks should be relaxed.

For multi-component mixture references, the builder works with binary pair
matrix rows. If `mixture_names` is omitted, all binary combinations from the
component list must be available in the reference table. For
`[methanol, ethanol, butyl_methyl_ether]`, that means `methanol|ethanol`,
`methanol|butyl-methyl-ether`, and `ethanol|butyl-methyl-ether`.

Use `mixture_names` when the build should include only selected binary pairs,
for example `["methanol | ethanol", "ethanol | butyl-methyl-ether"]`.
Each entry is split on `delimiter`, trimmed, sorted, and compared
case-insensitively, so whitespace and member order do not matter. The names
must still use the same identity basis as `mixture_key`: component names when
`mixture_key="Name"` and formulas when `mixture_key="Formula"`.

For mixture builds, the reference table must be a matrix `DATA` table marked by
`MATRIX-SYMBOL` and should use item rows with `Mixture`, `Name`, `Formula`, and
`State` columns. Discovery can match row components by `component_key="Name-State"`
or `component_key="Formula-State"`. After the table is built as `TableMatrixData`,
matrix value lookup is name-based; pass component names to `mat`, `ij`, and
`ijs`.

Do not encode a ternary mixture as one `Mixture` value such as
`methanol|ethanol|butyl-methyl-ether`, and do not add matrix columns such as
`a_i_3` for this builder workflow. Use additional binary pair row groups
instead.

Use `databook_name`, `table_name`, and `constants` to narrow constants builds:
`databook_name='CUSTOM-REF-1'`, `table_name='Custom-Constants'`, or `constants=['R', 'dH_rxn', 'dG_rxn']`.

## Object Usage

After building, work from the `.thermodb` attribute for high-level wrapper results:

```python
result = build_component_thermodb_from_reference(...)
if result is None:
    raise ValueError("Failed to build component thermodb from reference.")

thermodb = result.thermodb
print(thermodb.check())
```

Select equations and data with the full source key when needed:

```python
table = thermodb.select("CUSTOM-REF-1::ideal-gas-heat-capacity")
cp = thermodb.select_function(function_name="ideal-gas-heat-capacity")
```

For constants, select the constants table before retrieving individual constants:

```python
constants_db = result.thermodb.select_constant("CUSTOM-REF-1::Custom-Constants")
value = constants_db.get_constant("R", message="gas constant")
```

For matrix data, check the selected property type and then use `mat`, `ij`, `ijs`, or `thermodb.retrieve(...)`:

```python
matrix = thermodb.check_property("CUSTOM-REF-1::NRTL Non-randomness parameters-2")
value = matrix.mat("a", ["ethanol", "methanol"])
same_value = matrix.ij("a_ethanol_methanol")
all_values = matrix.ijs("a | ethanol | methanol")
```

For item-row matrix tables with a `Mixture` column, `ij`/`ijs` infer
`mixture_name` from the two component names. Pass `mixture_name="methanol | ethanol"`
when you need to disambiguate or document the selected binary pair.

## Mapper-Level Workflows

Use `component_reference_mapper` or `mixture_reference_mapper` followed by `check_and_build_component_thermodb` or `check_and_build_mixture_thermodb` when the task needs to inspect or reuse generated `reference_config` and `ignore_labels`.

Preserve this data flow:

```python
mapped = component_reference_mapper(...)
reference_config = mapped.reference_thermodb.configs
ignore_labels = mapped.reference_thermodb.ignore_labels
custom_reference = {"reference": [REFERENCE_CONTENT]}

thermodb = check_and_build_component_thermodb(
    component=component,
    reference_config=reference_config,
    custom_reference=custom_reference,
    ignore_state_props=ignore_labels,
)
```

## Local Examples

Use these repo examples as source-of-truth patterns:

- `examples/configs/build component thermodb from reference - 1.py`
- `examples/configs/build constants thermodb from reference - 1.py`
- `examples/configs/build mixture thermodb from reference - 1.py`
- `examples/configs/build mixture thermodb from reference - 3.py`
- `examples/configs/exp-build-thermodb-1.py`
- `examples/configs/exp-build-thermodb-1 - check eq num.py`
- `examples/configs/load matrix thermodb - 1.py`
