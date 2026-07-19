# Schema rules

pyThermoDB references may be full files:

```yaml
REFERENCES:
  CUSTOM-REF-1:
    DATABOOK-ID: 1
    TABLES:
      table-name:
        TABLE-ID: 1
        ...
```

They may also be direct table snippets when drafting or validating a single table.

Use the full wrapper when the output will be loaded as a reference file or embedded as
`REFERENCE_CONTENT` in examples such as `examples/configs/reference_2.py`. Use a direct table
snippet only when the user asks for one table or when copying from the table-specific assets.

Full reference files can mix table types under one `TABLES` mapping:

- data tables marked by `DATA`
- equation tables marked by `EQUATIONS`
- constants tables marked by `CONSTANTS`
- matrix tables marked by `MATRIX-SYMBOL`

## Data table

Required fields:

- `TABLE-ID`
- `DESCRIPTION`
- `DATA: []`
- `STRUCTURE`
- `VALUES`

`STRUCTURE` must contain:

- `COLUMNS`
- `SYMBOL`
- `UNIT`
- `CONVERSION`

Some existing references store detailed data-table metadata under `DATA:` and only repeat
`COLUMNS`, `SYMBOL`, and `UNIT` under `STRUCTURE`. Treat either location as valid when
checking `CONVERSION`, but prefer the `DATA: []` plus `STRUCTURE.CONVERSION` style for new
tables unless a source file already uses the alternate style.

## Equation table

Required fields:

- `TABLE-ID`
- `DESCRIPTION`
- `EQUATIONS`
- `STRUCTURE`
- `VALUES`

`STRUCTURE` must contain:

- `COLUMNS`
- `SYMBOL`
- `UNIT`

For references intended for `build_mixture_thermodb_from_reference`, prefer the
item-row matrix format:

```yaml
MATRIX-SYMBOL:
  - a constant: a
  - b constant: b
STRUCTURE:
  COLUMNS: [No.,Mixture,Name,Formula,State,a_i_1,a_i_2,b_i_1,b_i_2]
  SYMBOL: [None,None,None,None,None,a_i_1,a_i_2,b_i_1,b_i_2]
  UNIT: [None,None,None,None,None,1,1,1,1]
VALUES:
  - [1,methanol|ethanol,methanol,CH3OH,l,0,0.300492719,0,1.564200272]
  - [2,methanol|ethanol,ethanol,C2H5OH,l,0.380229054,0,-20.63243601,0]
```

Matrix-specific rules:

- `MATRIX-SYMBOL` must be a list. Plain string items map to themselves, while
  one-key mappings map description to base symbol. Use one-key mappings when the
  symbol meaning is not obvious.
- `Mixture` stores the binary mixture id using the active delimiter, normally
  `|`. Matching normalizes case, trims whitespace, and sorts mixture members, so
  row values such as `ethanol|methanol` still match components
  `[methanol, ethanol]`.
- For each base symbol, provide a complete set of directional columns
  `<symbol>_i_1`, `<symbol>_i_2` for binary pairs. For larger matrix tables,
  continue through `<symbol>_i_N`.
- A binary item table has two rows per `Mixture`: one for each row component.
  The row for component `i` stores values to column components `j`.
- Every declared matrix cell must be populated. Use `0` only when the source or
  model definition defines that cell as zero.
- Do not add `DATA` or `CONVERSION` to matrix tables.

Do not add `DATA` or `CONVERSION` to equation tables.

Equation bodies may be one-line assignments or multiline executable steps. The
`reference_2.py` style uses temporary variables such as `Tr`, `tau`, `expo`, and `ps_bar`
before assigning to `res[...]`; keep that form when it improves readability or mirrors the
source correlation.

Each equation block should include these keys, even when not available:

- `BODY`
- `BODY-INTEGRAL`
- `BODY-FIRST-DERIVATIVE`
- `BODY-SECOND-DERIVATIVE`

Set unavailable integral or derivative blocks to `None`.

Equation tables may also include variable range columns such as `Tmin` and `Tmax`.
These columns belong in `STRUCTURE.COLUMNS`, `STRUCTURE.SYMBOL`, `STRUCTURE.UNIT`, and each
`VALUES` row. They are not separate top-level blocks and do not require `CONVERSION`.

Runtime range detection is symbol-based. For an equation argument symbol `T`, valid range symbols
include `Tmin`, `Tmax`, `Tlow`, `Thigh`, `T(min)`, `T(max)`, `T[min]`, `T[max]`, `T{min}`, and
`T{max}`. Prefer `Tmin` and `Tmax` when representing source temperature limits.

## Constants table

Required fields:

- `TABLE-ID`
- `DESCRIPTION`
- `CONSTANTS: []`
- `STRUCTURE`
- `VALUES`

`STRUCTURE` must contain `COLUMNS`. Constants tables commonly use:

```yaml
COLUMNS: [No.,Name,Symbol,State,Value,Unit,Description]
```

The `Value` column may contain scalar values, dictionaries keyed by reaction or case id,
lists, strings, or `None`. Preserve those values as YAML-native values.

Do not require `SYMBOL`, `UNIT`, or `CONVERSION` arrays for constants tables unless the
surrounding reference file already uses them.

## Matrix data table

Required fields:

- `TABLE-ID`
- `DESCRIPTION`
- `MATRIX-SYMBOL`
- `STRUCTURE`
- `VALUES`

`STRUCTURE` must contain:

- `COLUMNS`
- `SYMBOL`
- `UNIT`

## Fixed width rule

Each row in `VALUES` must exactly match the number of entries in `COLUMNS`.
Use `0` instead of `None` when the active project convention says to use `0`.

## Component record uniqueness rule

For component-style data and equation tables, `VALUES` must contain only one row per component
identity and state in the same table. Use the component metadata columns to identify duplicates,
normally `Name`, `Formula`, and `State` when present.

Different states are valid separate records. For example, `Methane`/`CH4`/`g` and
`Methane`/`CH4`/`l` may both appear in the same table. Do not create a second row for the same
`Name`/`Formula`/`State` identity, such as another methane gas row, to hold another property range,
alternate equation selector, source note, or leftover coefficient group. Merge all columns for that
component-state identity into the same row. If duplicate source rows for the same component-state
identity have conflicting values, report the conflict in notes and do not fabricate a merged value.

This rule applies to component data tables and component equation tables. It does not apply to
matrix tables, pairwise mixture rows, or constants tables, because those table types use different
row identities.

Matrix table row identity is the `Mixture` id plus the row component identity.
For state-aware matching, that row component identity is `Name` plus `State` or
`Formula` plus `State`; for state-ignored matching, it is `Name` or `Formula`.
Do not merge the two component rows of a binary pair into one row.

## Metadata rule

Keep these when the project requires them:

- `No.`
- `Name`
- `Formula`
- `State`

## Formula style rule

Prefer compact formulas:

- `C2H4`
- `C7H8`
- `C3H6O2`

Avoid source-display formulas unless explicitly requested.
