# Reference Table Guidance

Use this file as the format contract for custom `REFERENCE_CONTENT` blocks used
to build `pyThermoDB` sources for activity models. The examples in
`examples/configs` and `examples/matrix-1` show that activity-model reference
data is provided as YAML under:

```yaml
REFERENCES:
  <reference-name>:
    DATABOOK-ID: <integer>
    TABLES:
      <table title>:
        TABLE-ID: <integer>
        DESCRIPTION: <text>
        MATRIX-SYMBOL:
          - <description>: <base symbol>
        STRUCTURE:
          COLUMNS: [...]
          SYMBOL: [...]
          UNIT: [...]
        VALUES:
          - [...]
```

## Matrix Table Rules

- Activity interaction parameters must be encoded as mixture matrix tables.
- Each row represents one component in the mixture.
- `Mixture` must contain all component names joined by `|`, for example
  `ethanol|butyl-methyl-ether`, when `mixture_key='Name'`. If the builder call
  uses `mixture_key='Formula'`, `Mixture` must contain formulas instead.
- `Name`, `Formula`, and `State` identify the row component.
- Discovery can match row components by `Name-State` or `Formula-State`.
- Matrix entries use the column pattern `<symbol>_i_<j>`, where `j` is the
  one-based component index in the mixture order.
- For a binary mixture, include two rows and two columns per matrix symbol:
  `<symbol>_i_1` and `<symbol>_i_2`.
- Every matrix cell defined by the table schema must be populated in `VALUES`,
  including diagonal cells such as `<symbol>_i_1` for component 1 in row 1.
  Use `0` only when the source data or model definition explicitly defines
  that cell as zero; do not assume diagonal cells are zero in the general case.
- `COLUMNS`, `SYMBOL`, `UNIT`, and each `VALUES` row must have the same length.
- Use `None` in `SYMBOL` and `UNIT` for metadata columns such as `No.`,
  `Mixture`, `Name`, `Formula`, and `State`.
- Do not include `DATA` or `CONVERSION` in matrix tables.
- After building, `TableMatrixData` retrieval methods such as `mat`, `ij`, and
  `ijs` use component names, not formulas.

For a binary mixture with components `component-1` and `component-2`, each
matrix parameter is represented as:

```text
parameter = [
  [parameter_1_1, parameter_1_2],
  [parameter_2_1, parameter_2_2],
]
```

and encoded into rows as:

```text
row for component-1: parameter_i_1 = parameter_1_1, parameter_i_2 = parameter_1_2
row for component-2: parameter_i_1 = parameter_2_1, parameter_i_2 = parameter_2_2
```

If more than one parameter is stored in the same table, repeat the complete
matrix-column set for each parameter.

## Examples

The following NRTL and UNIQUAC sections are examples of the general matrix-table
format. Do not treat model-specific values such as diagonal zeros as global
reference-table rules.

## Example: NRTL

The NRTL model consumes mixture-level matrix data with these symbols:

- `alpha`: non-randomness parameter, dimensionless.
- `dg`: interaction energy parameter, used to calculate `tau`.
- `tau`: optional direct binary interaction parameter.
- `a`, `b`, `c`, `d`: optional coefficient matrices used when `dg` is not
  supplied.

The common inline-source format in `examples/activity-models` supplies `alpha`
and `dg` directly:

```text
components = [ethanol, butyl-methyl-ether]

alpha = [
  [0,        0.680715],
  [0.680715, 0       ],
]

dg = [
  [0,           3268.884433],
  [1768.662389, 0          ],
]
```

The corresponding table has one complete matrix-column set for `alpha` and one
complete matrix-column set for `dg`:

```yaml
REFERENCES:
  NRTL:
    DATABOOK-ID: 1
    TABLES:
      Non-randomness parameters of the NRTL equation:
        TABLE-ID: 1
        DESCRIPTION:
          This table provides the NRTL non-randomness parameters and
          interaction energy parameters.
        MATRIX-SYMBOL:
          - alpha constant: alpha
          - binary interaction parameter: dg
        STRUCTURE:
          COLUMNS: [No.,Mixture,Name,Formula,State,alpha_i_1,alpha_i_2,dg_i_1,dg_i_2]
          SYMBOL: [None,None,None,None,None,alpha_i_1,alpha_i_2,dg_i_1,dg_i_2]
          UNIT: [None,None,None,None,None,1,1,J/mol,J/mol]
        VALUES:
          - [1,ethanol|butyl-methyl-ether,ethanol,C2H5OH,l,0,0.680715,0,3268.884433]
          - [2,ethanol|butyl-methyl-ether,butyl-methyl-ether,C5H12O,l,0.680715,0,1768.662389,0]
```

If using the coefficient method instead of direct `dg`, provide `a`, `b`, `c`,
and `d` matrix columns in the same pattern:

```text
a = [[a_1_1, a_1_2], [a_2_1, a_2_2]]
b = [[b_1_1, b_1_2], [b_2_1, b_2_2]]
c = [[c_1_1, c_1_2], [c_2_1, c_2_2]]
d = [[d_1_1, d_1_2], [d_2_1, d_2_2]]
alpha = [[alpha_1_1, alpha_1_2], [alpha_2_1, alpha_2_2]]
```

```yaml
COLUMNS: [No.,Mixture,Name,Formula,State,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,d_i_1,d_i_2,alpha_i_1,alpha_i_2]
SYMBOL: [None,None,None,None,None,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,d_i_1,d_i_2,alpha_i_1,alpha_i_2]
```

For `pyThermoLinkDB` config, map NRTL data symbols directly:

```yaml
NRTL:
  DATA:
    alpha: alpha
    dg: dg
    tau: tau
  EQUATIONS:
    None
```

## Example: UNIQUAC

The UNIQUAC model needs both mixture interaction data and pure component
parameters:

- Mixture matrix data: `dU` or `tau`, or coefficient matrices `a`, `b`, `c`,
  and `d`.
- Component data: `r` volume parameter and `q` surface-area parameter.

The examples may store the UNIQUAC interaction-energy matrix under a table
symbol named `dg` and map it to model symbol `dU` in `thermodb_config_link.yml`.
Prefer naming the matrix symbol `dU` in new references when possible; if using
`dg`, the link config must map `dg: dU`.

Mixture interaction table format:

```text
components = [methanol, ethanol]

a = [
  [0,           0.300492719],
  [0.380229054, 0          ],
]

b = [
  [0,            1.564200272],
  [-20.63243601, 0          ],
]

c = [
  [0,           35.05450323],
  [0.059982839, 0         ],
]

d = [
  [0, 0],
  [0, 0],
]
```

The corresponding mixture table has one complete matrix-column set for each
parameter:

```yaml
REFERENCES:
  CUSTOM-REFERENCE-1:
    DATABOOK-ID: 1
    TABLES:
      Interaction parameters of the UNIQUAC equation:
        TABLE-ID: 1
        DESCRIPTION:
          This table provides UNIQUAC binary interaction parameters.
        MATRIX-SYMBOL:
          - a constant: a
          - b constant: b
          - c constant: c
          - d constant: d
        STRUCTURE:
          COLUMNS: [No.,Mixture,Name,Formula,State,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,d_i_1,d_i_2]
          SYMBOL: [None,None,None,None,None,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,d_i_1,d_i_2]
          UNIT: [None,None,None,None,None,1,1,1,1,1,1,1,1]
        VALUES:
          - [1,methanol|ethanol,methanol,CH3OH,l,0,0.300492719,0,1.564200272,0,35.05450323,0,0]
          - [2,methanol|ethanol,ethanol,C2H5OH,l,0.380229054,0,-20.63243601,0,0.059982839,0,0,0]
```

Pure component data for UNIQUAC must include `r` and `q` in a normal component
data table. The examples place them in `general-data` as
`Volume-Parameter` and `Surface-Area-Parameter`:

```text
r = {
  methanol: 1.4311,
  ethanol: 2.1055,
}

q = {
  methanol: 1.4320,
  ethanol: 1.8920,
}
```

```yaml
general-data:
  TABLE-ID: 2
  DESCRIPTION:
    Pure component data used by UNIQUAC.
  STRUCTURE:
    COLUMNS: [No.,Name,Formula,State,Volume-Parameter,Surface-Area-Parameter]
    SYMBOL: [None,None,None,None,r,q]
    UNIT: [None,None,None,None,1,1]
    CONVERSION: [None,None,None,None,1,1]
  VALUES:
    - [1,methanol,CH3OH,l,1.4311,1.4320]
    - [2,ethanol,C2H5OH,l,2.1055,1.8920]
```

For `pyThermoLinkDB` config, include `r` and `q`; map the stored interaction
symbol to `dU` when needed:

```yaml
uniquac:
  DATA:
    r: r
    q: q
    dU: dU
    tau: tau
  EQUATIONS:
    None
```

If the reference table stores UNIQUAC interaction energy as `dg`, use:

```yaml
uniquac:
  DATA:
    r: r
    q: q
    dg: dU
    tau: tau
  EQUATIONS:
    None
```
