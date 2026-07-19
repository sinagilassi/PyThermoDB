# Mixture Table Agent Instruction (Universal NRTL Format)

Use this guide when generating a mixture matrix table in reference YAML for PyThermoDB.

The table `NRTL Non-randomness parameters-1` is the universal pattern and can be reused for any binary or multi-component case, as long as each binary mixture is represented with one row per component.

## Goal

Construct a valid matrix `DATA` table so that:

- `build_mixture_thermodb_from_reference(...)` can discover it.
- `ReferenceChecker` can validate availability.
- Mixture properties can be built through `build_components_thermo_property(...)`.

## Canonical Table Pattern

```yaml
NRTL Non-randomness parameters-1:
  TABLE-ID: 5
  DESCRIPTION:
    This table provides the NRTL non-randomness parameters for the NRTL equation.
  MATRIX-SYMBOL:
    - a constant: a
    - b
    - c
    - alpha
  STRUCTURE:
    COLUMNS: [No.,Mixture,Name,Formula,State,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
    SYMBOL: [None,None,None,None,None,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
    UNIT: [None,None,None,None,None,1,1,1,1,1,1,1,1]
  VALUES:
    - [1,methanol|ethanol,methanol,CH3OH,l,0,0.300492719,0,1.564200272,0,35.05450323,0,4.481683583]
    - [2,methanol|ethanol,ethanol,C2H5OH,l,0.380229054,0,-20.63243601,0,0.059982839,0,4.481683583,0]
```

## How MATRIX-SYMBOL Expands To Columns

For this universal NRTL format, each base symbol in `MATRIX-SYMBOL` becomes two directional parameter columns for a binary pair.

Base symbol to header expansion:

- `a` -> `a_i_1`, `a_i_2`
- `b` -> `b_i_1`, `b_i_2`
- `c` -> `c_i_1`, `c_i_2`
- `alpha` -> `alpha_i_1`, `alpha_i_2`

Meaning of the suffixes:

- `_i_1` is the parameter value used for component row 1 in that binary mixture entry.
- `_i_2` is the parameter value used for component row 2 in that binary mixture entry.

So when you define these matrix symbols:

```yaml
MATRIX-SYMBOL:
  - a constant: a
  - b
  - c
  - alpha
```

you must include these headers in both `STRUCTURE.COLUMNS` and `STRUCTURE.SYMBOL`:

```yaml
a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2
```

Agent rule: do not invent custom suffixes for this format. Keep the exact naming pattern `symbol_i_1` and `symbol_i_2` so downstream mixture availability checks and build logic remain consistent.

## Required Rules

1. Table must be a matrix `DATA` table.
2. `MATRIX-SYMBOL` must exist.
3. `STRUCTURE.COLUMNS` must include identity fields `Mixture`, `Name`, `Formula`, and `State`.
4. `Mixture` value must use one delimiter consistently (default `|`).
5. Mixture IDs are order-insensitive in matching logic, but rows should still be written consistently.
6. For each binary mixture ID, include one row per component participating in that binary pair.
7. `Name` and `Formula` must match the component rows used in build calls.
8. `State` must be present even if some properties later use `ignore_state_props`.
9. Parameter columns in `COLUMNS`, `SYMBOL`, and `UNIT` must align by index.
10. `VALUES` row length must match `COLUMNS` length exactly.

## Universal Construction Algorithm (Agent Workflow)

1. Collect components from the request as tuples: `(name, formula, state)`.
2. Decide `mixture_key` intent: use names for name-keyed mixtures, or formulas for formula-keyed mixtures.
3. Build binary mixture IDs for all needed pairs by trimming and sorting pair members, then joining with delimiter `|`.
4. For each binary mixture ID, write one row per component in that binary pair.
5. Fill NRTL parameter columns (`a_i_1`, `a_i_2`, `b_i_1`, `b_i_2`, `c_i_1`, `c_i_2`, `alpha_i_1`, `alpha_i_2`).
6. Validate row-to-column count and field consistency.
7. Output YAML with only valid scalar/list values.

## Multi-Component Case (How To Encode)

For a component list like `[methanol, ethanol, methane]`, encode the binary pairs as separate mixture IDs:

- `methanol|ethanol` -> 2 rows
- `methane|ethanol` -> 2 rows
- `methane|methanol` -> 2 rows (if needed by use case)

Even in multi-component workflows, the matrix table stores binary interaction rows per mixture ID.

## Validation Checklist For Agent

- Table includes `MATRIX-SYMBOL`.
- Table is treated as matrix `DATA` (not equation table).
- `Mixture` column exists and is populated for every row.
- Every target binary mixture has all expected component rows.
- `Name`, `Formula`, `State` values are not empty.
- No duplicate conflicting rows for the same mixture/component identity.
- Delimiter is consistent across all mixture IDs.
- Symbols are valid strings and map to parameter columns.

## Common Mistakes To Avoid

- Missing `Mixture` column.
- Using inconsistent delimiter (`|` in some rows, `,` in others).
- Writing only one row for a binary mixture.
- Omitting `State` column.
- Mismatch between `COLUMNS` and `VALUES` item count.
- Using different component naming forms than the build input.

## Reusable Prompt Snippet For Agents

Use this instruction when you ask an agent to generate a mixture table:

"Generate a matrix DATA table named `NRTL Non-randomness parameters-1` using the universal PyThermoDB format. Include `MATRIX-SYMBOL`, `STRUCTURE` with `COLUMNS/SYMBOL/UNIT`, and `VALUES`. Ensure identity fields are `Mixture, Name, Formula, State`. For each required binary mixture ID, write one row per component. Use delimiter `|`, keep row lengths aligned with columns, and ensure symbols/units align by index."

## Optional Compatibility Notes

- If state-specific matching is strict, ensure component `State` matches the build input.
- If some properties use ignore-state behavior, still keep `State` populated in the table.
- Prefer lowercase/trim-consistent component names in `Mixture` IDs to reduce formatting errors.
