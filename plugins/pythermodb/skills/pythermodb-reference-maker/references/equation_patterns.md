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
