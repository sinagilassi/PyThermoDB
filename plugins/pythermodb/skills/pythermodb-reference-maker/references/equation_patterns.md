# Equation patterns

## Mathematical operation rule

All executable equation blocks MUST use only Python’s built-in `math` module for mathematical operations.

Rules:

- Any function from the `math` module is allowed.
- Standard Python arithmetic operators are allowed: `+`, `-`, `*`, `/`, `**`.
- All expressions must be scalar (no vectorized operations).

Strictly not allowed:

- `numpy`
- `scipy`
- `sympy`
- `pandas`
- any third-party scientific or numerical library

Additional constraints:

- Do not use aliases such as `np.exp` or `sp.log`.
- Do not import or reference external modules inside equation blocks.
- If a required mathematical function is not available in `math`, do NOT substitute from another library — instead, flag the limitation in notes.

## Core transformation principle

All equations MUST be transformed into executable YAML using:

- parms[...] → coefficients
- args[...] → variables
- res[...] → outputs

This transformation is mandatory and defines the project’s computational model.

## Ambiguity handling

If the source is incomplete:

- Missing coefficients → do not fabricate values
- Missing equation → return partial structure with notes
- Unclear scaling → flag explicitly in notes

Always prefer:

- correctness over completeness

## Vapor pressure pattern

Source form:
`ln P = C1 + C2/T + C3 ln T + C4 T^C5`

Executable YAML form:

- map coefficients to `parms[...]`
- map variables to `args[...]`
- map result to `res[...]`
- use `math.log` and `math.exp`
- include explicit normalization lines for each coefficient, even if the divisor is `1`

## Heat-capacity polynomial pattern

Example source form:
`Cp/R = a0 + a1 T + a2 T^2 + a3 T^3 + a4 T^4`

Scaled headers such as `a1 × 10^3`, `a2 × 10^5`, `a3 × 10^8`, `a4 × 10^11` must be represented in `UNIT`, not `SYMBOL`.

## Extended blocks

Equation tables may include:

- `BODY`
- `BODY-INTEGRAL`
- `BODY-FIRST-DERIVATIVE`
- `BODY-SECOND-DERIVATIVE`

If the template or source supports them, keep all blocks.

## Variable range columns

Equation tables may define valid ranges for equation variables in `STRUCTURE` and `VALUES`.
These ranges are table metadata; do not put them inside `EQUATIONS`.

The runtime reads equation argument symbols, then scans `STRUCTURE.SYMBOL` for matching range
symbols. For an argument symbol such as `T`, accepted range-symbol forms include:

- `Tmin`, `Tmax`, `Tlow`, `Thigh`
- `T(min)`, `T(max)`, `T(low)`, `T(high)`
- `T[min]`, `T[max]`, `T[low]`, `T[high]`
- `T{min}`, `T{max}`, `T{low}`, `T{high}`

Use the same entry in `COLUMNS` and `SYMBOL` unless the source requires a more descriptive
column name. Prefer `Tmin` and `Tmax` for temperature ranges because
`get_variable_range_values()` returns them as `min` and `max` bounds for argument `T`.

Example:

```yaml
STRUCTURE:
  COLUMNS: [No.,Name,Formula,State,C1,C2,C3,C4,C5,Tmin,Tmax,Eq]
  SYMBOL: [None,None,None,None,C1,C2,C3,C4,C5,Tmin,Tmax,VaPr]
  UNIT: [None,None,None,None,1,1,1,1,1,K,K,Pa]
VALUES:
  - [1,'water','H2O','l',73.649,-7258.2,-7.3037,4.1653E-6,2,273.16,647.096,1]
```

Related dependent-value columns such as `P(Tmin)` or `P(Tmax)` are allowed when provided by the
source, but they are ordinary metadata columns unless their symbol follows the argument range
pattern for an equation argument.

## Special-case row pattern

If one compound uses a different equation from the rest of the table:

- add another `EQ-n`
- use an equation selector column according to project convention
- do not infer equation choice from missing coefficients alone

## Equation selector column

When an equation table has an `Eq` column, every `VALUES` row must end with a numeric equation selector.

Rules:

- Use `1` for rows that use `EQ-1`.
- Use `2` for rows that use `EQ-2`, and continue sequentially for additional equations.
- The selector must always be a number starting from `1`; never use placeholders such as `X`, equation names, text labels, or empty values.
