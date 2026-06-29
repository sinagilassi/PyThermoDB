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
