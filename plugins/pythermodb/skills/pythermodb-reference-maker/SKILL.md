---
name: pythermodb-reference-maker
description: Extract thermodynamic tables and correlations from references (CSV, PDF, images, or text) and convert them into the project's structured pyThermoDB YAML schema. Supports data tables, constants tables, matrix-parameter tables, and equation-based correlations (e.g., Cp, vapor pressure, density, enthalpy of vaporization), including coefficient parsing and transformation into executable project notation (parms, args, res). Trigger when working with thermodynamic tables, coefficients, correlations, constants, matrix parameters, or YAML formatting. Ensures unit-consistent, schema-compliant, and solver-ready thermodynamic definitions for downstream modeling tools.
---

# Thermodynamic Table to YAML Extractor

## Purpose

Convert thermodynamic tables into the structured YAML format used by pyThermoDB references.

Support:
- Data tables such as general component properties.
- Constants tables such as custom constants or reaction constants.
- Matrix-parameter tables such as binary NRTL parameters.
- Equation tables such as Cp, vapor pressure, density, and enthalpy of vaporization.
- Multi-equation systems.
- Optional integral and derivative expressions.
- Optional variable range columns such as `Tmin`, `Tmax`, `Pmin`, or `Pmax`.

## Step 0: Interpret the task

Before processing:

1. Identify input type:
   - CSV
   - PDF/image
   - raw text
   - existing YAML
   - online source or database page
   - article, paper, report, or handbook excerpt
2. Identify table type:
   - data table: component or mixture scalar properties
   - constants table: named constants and scalar/list/dict constant values
   - matrix table: pairwise or matrix-parameter data
   - equation table: coefficients plus formula
3. Identify container format:
   - full reference: `REFERENCES -> reference id -> DATABOOK-ID -> TABLES`
   - direct table snippet: one or more table names at the top level
4. Identify complexity:
   - single equation
   - multiple equations
   - mixed table patterns
5. Check for:
   - scaled coefficients
   - variable range columns such as `Tmin`/`Tmax`
   - duplicate component records in `VALUES`
   - missing metadata columns
   - special-case rows

## Step 0a: Resolve source policy

Before extracting values, determine whether the user supplied or constrained the source.

Source modes:

- user-supplied source: a file, image, pasted text, URL, DOI, article, report, or database page
- user-constrained source: the user says to use only a specific source, such as NIST, DIPPR,
  Perry's, a named article, or an attached file
- open source search: the user asks for thermodynamic data without naming the source

Rules:

- If the user constrains the source, use only that source unless it is incomplete or internally
  inconsistent. If another source is needed to resolve a missing formula, unit, equation form, or
  coefficient definition, ask or clearly label the additional source as supplemental.
- If the user supplies an article, report, PDF, image, or excerpt, extract from that material first.
  Preserve the article's equation form, coefficient definitions, units, ranges, and stated validity
  limits before translating into executable pyThermoDB notation.
- If the user asks for NIST or another online thermodynamic database, retrieve the relevant table
  or page when browsing is available. Record the database name, page/table title, component names,
  property, equation form, units, and access date in notes or the table description when useful.
- If the user does not name a source, prefer authoritative thermodynamic references and databases.
  Use exact source attribution in notes so coefficients are traceable.
- Do not blend coefficients from multiple sources into one row unless the output explicitly includes
  source-disambiguating columns or notes. Report conflicts instead of silently choosing one value.
- Do not invent missing coefficients, ranges, or equation identifiers. Mark missing values as
  unresolved in notes and produce only the YAML that can be supported by the source.
- Respect source terms and access limits. Summarize copyrighted source text and extract only the
  factual coefficients, equations, units, and metadata needed for the YAML.

## Step 1: Classify table type

### Data table

A data table contains component or mixture scalar properties and no evaluable correlation equation.

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

An equation table contains coefficients tied to one or more equations.

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

Equation bodies may contain multiple executable steps before assigning to `res[...]`, such as
`Tr`, `tau`, `expo`, and a final converted result. Keep intermediate variables when the source
formula is complex or when the project examples use that style.

Equation tables may include variable range columns. Store them as normal columns in
`STRUCTURE.COLUMNS`, `STRUCTURE.SYMBOL`, `STRUCTURE.UNIT`, and every `VALUES` row. Do not put
range limits inside `EQUATIONS`.

### Constants table

A constants table contains named constants rather than component rows or evaluable correlations.

```yaml
table-name:
  TABLE-ID: <int>
  DESCRIPTION:
    <text>
  CONSTANTS: []
  STRUCTURE:
    COLUMNS: [No.,Name,Symbol,State,Value,Unit,Description]
  VALUES:
    - [...]
```

The `Value` column may be a scalar, string, dictionary, list, or `None`.

### Matrix table

A matrix table defines pairwise or matrix symbols, such as NRTL `a`, `b`, `c`, or `alpha`.

```yaml
table-name:
  TABLE-ID: <int>
  DESCRIPTION:
    <text>
  MATRIX-SYMBOL:
    - a
    - b
  STRUCTURE:
    COLUMNS: [...]
    SYMBOL: [...]
    UNIT: [...]
  VALUES:
    - [...]
```

## Step 2: Interpret CSV

When the source is a CSV in the project style:
- row 1 = `COLUMNS`
- row 2 = `SYMBOL`
- row 3 = `UNIT`
- rows 4+ = `VALUES`

For data tables, also generate `CONVERSION`.

## Step 3: Transform equations

Do not copy equations symbolically. Convert them into executable YAML using the current project
notation from `examples/reference/str-ref-1.md`:
- coefficients -> inline typed `parms['name | symbol | unit']` keys
- variables -> inline typed `args['name | symbol | unit']` keys
- result -> inline typed `res['name | symbol | unit']` keys

Do not add legacy equation metadata blocks:
- no `ARGS`
- no `PARMS`
- no `RETURNS`

The name, symbol, and unit metadata must live inside each `parms[...]`, `args[...]`, and
`res[...]` key string, and the table-level `STRUCTURE` must still define the row columns,
symbols, and units.

Example source:

```text
ln P = C1 + C2/T + C3 ln T + C4 T^C5
```

Executable YAML body:

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

## Step 4: Preserve coefficient scaling

If a source table shows scaled headers such as `a1 x 10^3`, `a2 x 10^5`, `a3 x 10^8`, or `a4 x 10^11`, preserve the scale in `UNIT`, not in `SYMBOL`.

Correct pattern:

```yaml
STRUCTURE:
  COLUMNS: [No.,Name,Formula,State,a0,a1,a2,a3,a4,R,Eq]
  SYMBOL: [None,None,None,None,a0,a1,a2,a3,a4,R,Cp_IG]
  UNIT: [None,None,None,None,1,1E3,1E5,1E8,1E11,1,J/mol.K]
```

## Step 5: Keep extended equation blocks

Equation tables may include:
- `BODY`
- `BODY-INTEGRAL`
- `BODY-FIRST-DERIVATIVE`
- `BODY-SECOND-DERIVATIVE`

If the source or project template includes integral or derivative forms, keep all of them.

## Step 5a: Preserve equation variable ranges

If a source gives valid ranges for an equation variable, preserve them in the equation table.
The runtime detects ranges from `STRUCTURE.SYMBOL` by matching equation argument symbols.

For an argument symbol such as `T`, valid range symbols include:
- `Tmin`, `Tmax`, `Tlow`, `Thigh`
- `T(min)`, `T(max)`, `T(low)`, `T(high)`
- `T[min]`, `T[max]`, `T[low]`, `T[high]`
- `T{min}`, `T{max}`, `T{low}`, `T{high}`

Prefer `Tmin` and `Tmax` for temperature limits. Use the same unit as the variable, such as `K`
for `Tmin`/`Tmax`. Related source columns such as `P(Tmin)` or `P(Tmax)` may be preserved as
ordinary metadata columns, but they are not temperature range bounds.

## Step 6: Fixed schema rules

- Every row must have exactly the same number of values as the number of columns.
- Never shift columns.
- In component-style data and equation tables, define only one `VALUES` row per component record.
- Use `0` for unused coefficients if that is the active project convention.
- Keep mandatory metadata columns when the project requires them: `No.`, `Name`, `Formula`, `State`.
- For `State`, use default project codes unless the user explicitly requests another format:
  - `g` = gas
  - `l` = liquid
  - `s` = solid
  - `aq` = aqueous

Component record uniqueness means one row for each component identity in a table, normally
`Name` plus `Formula` plus `State` when those columns exist. Different states are different
component identities, so `Methane`/`CH4`/`g` and `Methane`/`CH4`/`l` are both valid rows in the
same table. Do not create a second row for the same `Name`/`Formula`/`State` identity, such as
another methane gas row, to hold extra coefficients, ranges, or alternate metadata. Merge all
columns for that component-state identity into the same row. If the source gives conflicting
values for the same component-state identity and table, flag the conflict in notes instead of
silently adding a duplicate row.

## Step 7: Unit and conversion rules

For data tables, use `CONVERSION` with `internal = stored * conversion`.

Use:
- `1` for numeric columns already in target internal units
- `None` for text columns

For equation tables, do not use `CONVERSION`; handle scaling and unit adjustments inside the equation body.

## Step 8: Formula style

Use the compact formula style used by the project's main reference files.

Prefer:
- `C2H4`
- `C7H8`
- `C3H6O2`

Avoid source-display formulas such as `CH2=CH2` or `C6H5-CH3` unless the user explicitly asks for source-faithful display formulas.

## Step 9: Use bundled resources

Read or run these when needed:

- `references/schema_rules.md`: table-type schema rules for data, equation, constants, and matrix tables.
- `references/equation_patterns.md`: equation transformation patterns and math-module rules.
- `references/examples.md`: examples for valid data, equation, constants, and matrix tables.
- `assets/reference_file_template.yaml`: starting template for a full `REFERENCES:` file with mixed table types.
- `assets/data_table_template.yaml`: starting template for direct data-table snippets.
- `assets/equation_table_template.yaml`: starting template for direct equation-table snippets.
- `assets/constants_table_template.yaml`: starting template for direct constants-table snippets.
- `assets/matrix_table_template.yaml`: starting template for direct matrix-parameter table snippets.
- `scripts/csv_to_structure.py`: convert project-style CSV headers into YAML arrays.
- `scripts/validate_yaml.py`: validate YAML shape. It accepts full `REFERENCES:` files and direct table snippets.
- `scripts/check_reference.py`: validate that YAML can be loaded by pyThermoDB itself.

Prefer `.venv/Scripts/python.exe` on Windows when running pyThermoDB-aware scripts inside this repository.

Example validation flow:

```bash
.venv/Scripts/python.exe skills/pythermodb-reference-maker/scripts/validate_yaml.py examples/external-ref/source-ref-1.yml
.venv/Scripts/python.exe skills/pythermodb-reference-maker/scripts/check_reference.py examples/external-ref/source-ref-1.yml CUSTOM-REF-1 Custom-Constants
```

## Validation checklist

Before finalizing:
- table type is correct
- `DATA` exists for data tables
- `CONVERSION` exists for data tables
- `EQUATIONS` exists for equation tables
- `CONSTANTS` exists for constants tables
- `MATRIX-SYMBOL` exists for matrix tables
- row width matches column count
- component-style `VALUES` contain only one row per component identity and state
- symbols, units, and values align exactly
- scaling is handled correctly
- variable range columns are preserved when present in the source
- formulas are normalized to project style unless instructed otherwise
- state values use `g`, `l`, `s`, or `aq` unless another format was explicitly requested
- no guessed coefficients are presented as exact

## Output format

Return:
1. table type
2. notes on corrections or dependencies
3. final YAML block

## Strict rules

- Do not guess coefficients.
- Do not drop columns required by the project schema.
- Do not mix table formats.
- Do not duplicate component-state rows in one component-style data or equation table.
- Do not ignore coefficient scaling shown in the source.
- Do not expand or change `State` values away from `g`, `l`, `s`, or `aq` unless explicitly requested.

## Definition of done

The task is complete only when:
- YAML matches the project schema
- equations are executable in project notation
- units and scales are represented in the correct layer
- data integrity is preserved
