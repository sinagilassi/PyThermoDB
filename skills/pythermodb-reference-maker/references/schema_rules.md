# Schema rules

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
