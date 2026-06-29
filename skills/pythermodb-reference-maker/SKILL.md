---
name: pythermodb-reference-maker
description: Extract thermodynamic tables and correlations from references (CSV, PDF, images, or text) and convert them into the project's structured YAML schema. Supports data tables and equation-based correlations (e.g., Cp, vapor pressure, density, enthalpy of vaporization), including coefficient parsing and transformation into executable project notation (parms, args, res). Trigger when working with thermodynamic tables, coefficients, correlations, or YAML formatting. Ensures unit-consistent, schema-compliant, and solver-ready thermodynamic definitions for downstream modeling tools.
---

# Thermodynamic Table → YAML Extractor

## Purpose

This skill converts thermodynamic tables into a structured YAML format used by the project.

It supports:
- data tables such as general properties
- equation tables such as Cp, vapor pressure, density, and enthalpy of vaporization
- multi-equation systems
- optional integral and derivative expressions

## Step 0: Task interpretation

Before processing:

1. Identify input type:
  - CSV
  - PDF/image
  - raw text

2. Identify table type:
  - data table → constants only
  - equation table → coefficients + formula

3. Identify complexity:
  - single equation
  - multiple equations
  - mixed patterns

4. Check for:
  - scaled coefficients
  - missing metadata columns
  - special-case rows

## Step 1: Classify table type

### Data table
A table is a data table when it contains only constants and no evaluable correlation equation.

Required structure:

```yaml
table-name:
  TABLE-ID: <int>
  DESCRIPTION:
    <text>
  DATA: []
  STRUCTURE:
    COLUMNS: [...]
    SYMBOL: [...]
    UNIT: [...]
    CONVERSION: [...]
  VALUES:
    - [...]
```

### Equation table
A table is an equation table when it contains coefficients tied to one or more equations.

Required structure:

```yaml
table-name:
  TABLE-ID: <int>
  DESCRIPTION:
    <text>
  EQUATIONS:
    EQ-1:
      BODY:
        - ...
      BODY-INTEGRAL:
        None
      BODY-FIRST-DERIVATIVE:
        None
      BODY-SECOND-DERIVATIVE:
        None
  STRUCTURE:
    COLUMNS: [...]
    SYMBOL: [...]
    UNIT: [...]
  VALUES:
    - [...]
```

Do not include `DATA` or `CONVERSION` for equation tables.

## Step 2: CSV interpretation

When the source is a CSV in the project style:
- row 1 = `COLUMNS`
- row 2 = `SYMBOL`
- row 3 = `UNIT`
- rows 4+ = `VALUES`

For data tables, also generate `CONVERSION`.

## Step 3: Equation transformation rule

Do not copy equations symbolically. Convert them into executable YAML using project notation:
- coefficients → `parms[...]`
- variables → `args[...]`
- result → `res[...]`

Example:

Source:

```text
ln P = C1 + C2/T + C3 ln T + C4 T^C5
```

YAML:

```yaml
EQ-1:
  BODY:
    - parms['C1 | C1 | 1'] = parms['C1 | C1 | 1']/1
    - parms['C2 | C2 | 1'] = parms['C2 | C2 | 1']/1
    - parms['C3 | C3 | 1'] = parms['C3 | C3 | 1']/1
    - parms['C4 | C4 | 1'] = parms['C4 | C4 | 1']/1
    - parms['C5 | C5 | 1'] = parms['C5 | C5 | 1']/1
    - res['vapor-pressure | VaPr | Pa'] = math.exp(parms['C1 | C1 | 1'] + parms['C2 | C2 | 1']/args['temperature | T | K'] + parms['C3 | C3 | 1']*math.log(args['temperature | T | K']) + parms['C4 | C4 | 1']*(args['temperature | T | K']**parms['C5 | C5 | 1']))
```

## Step 4: Scaled coefficient rule

If a source table shows scaled headers such as:
- `a1 × 10^3`
- `a2 × 10^5`
- `a3 × 10^8`
- `a4 × 10^11`

Then preserve the scale in `UNIT`, not in `SYMBOL`.

Correct pattern:

```yaml
STRUCTURE:
  COLUMNS: [No.,Name,Formula,State,a0,a1,a2,a3,a4,R,Eq]
  SYMBOL: [None,None,None,None,a0,a1,a2,a3,a4,R,Cp_IG]
  UNIT: [None,None,None,None,1,1E3,1E5,1E8,1E11,1,J/mol.K]
```

That means:
- `COLUMNS` = plain names
- `SYMBOL` = plain symbols or project result identifier
- `UNIT` = physical unit or scale tag

## Step 5: Extended equation support

Equation tables may include:
- `BODY`
- `BODY-INTEGRAL`
- `BODY-FIRST-DERIVATIVE`
- `BODY-SECOND-DERIVATIVE`

If the source or project template includes integral or derivative forms, keep all of them.

## Step 6: Fixed schema rules

- Every row must have exactly the same number of values as the number of columns.
- Never shift columns.
- Use `0` for unused coefficients if that is the active project convention.
- Keep mandatory metadata columns when the project requires them:
  - `No.`
  - `Name`
  - `Formula`
  - `State`
- For `State`, use the project default state codes unless the user explicitly requests another format:
  - `g` = gas
  - `l` = liquid
  - `s` = solid
  - `aq` = aqueous
- If the user wants expanded labels, uppercase labels, source-faithful labels, or another state format, they must state that in the prompt.

## Step 7: UNIT and CONVERSION rules

### Data tables
Use `CONVERSION`:

`internal = stored × conversion`

Use:
- `1` for numeric columns already in target internal units
- `None` for text columns

### Equation tables
Do not use `CONVERSION`. Handle scaling and unit adjustments inside the equation body.

## Step 8: Formula style

Use the compact formula style used by the project's main reference file.

Prefer:
- `C2H4`
- `C7H8`
- `C3H6O2`

Avoid source-display formulas such as:
- `CH2=CH2`
- `C6H5—CH3`

unless the user explicitly asks for source-faithful display formulas.

## Step 9: Validation checklist

Before finalizing:
- table type is correct
- `DATA: []` exists for data tables
- `CONVERSION` exists for data tables
- `EQUATIONS` exists for equation tables
- row width matches column count
- symbols, units, and values align exactly
- scaling is handled correctly
- formulas are normalized to project style
- state values use the default project codes (`g`, `l`, `s`, `aq`) unless another format was explicitly requested
- no guessed coefficients are presented as exact

## Output format

Return:
1. table type
2. notes on corrections or dependencies
3. final YAML block

## Strict rules

- Do not guess coefficients.
- Do not drop columns required by the project schema.
- Do not mix data-table and equation-table formats.
- Do not ignore coefficient scaling shown in the source.
- Do not expand or change `State` values away from `g`, `l`, `s`, or `aq` unless the user explicitly requests a different state format.

## Definition of done

The task is complete only when:
- YAML matches the project schema
- the equation is executable in the project's notation
- units and scales are represented in the correct layer
- data integrity is preserved
