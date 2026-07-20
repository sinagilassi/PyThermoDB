# Examples

## Example 1: Data table

```yaml
general-data:
  TABLE-ID: 2
  DESCRIPTION:
    General thermodynamic and physical data for selected compounds.
  DATA: []
  STRUCTURE:
    COLUMNS: [No.,Name,Formula,State,critical-temperature,critical-pressure]
    SYMBOL: [None,None,None,None,Tc,Pc]
    UNIT: [None,None,None,None,K,bar]
    CONVERSION: [None,None,None,None,1,1]
  VALUES:
    - [1,'water','H2O','l',647.096,220.640]
```

## Example 2: Equation table

```yaml
vapor-pressure:
  TABLE-ID: 3
  DESCRIPTION:
    Vapor pressure correlation.
  EQUATIONS:
    EQ-1:
      BODY:
        - parms['C1 | C1 | 1'] = parms['C1 | C1 | 1']/1
        - parms['C2 | C2 | 1'] = parms['C2 | C2 | 1']/1
        - parms['C3 | C3 | 1'] = parms['C3 | C3 | 1']/1
        - parms['C4 | C4 | 1'] = parms['C4 | C4 | 1']/1
        - parms['C5 | C5 | 1'] = parms['C5 | C5 | 1']/1
        - res['vapor-pressure | VaPr | Pa'] = math.exp(parms['C1 | C1 | 1'] + parms['C2 | C2 | 1']/args['temperature | T | K'] + parms['C3 | C3 | 1']*math.log(args['temperature | T | K']) + parms['C4 | C4 | 1']*(args['temperature | T | K']**parms['C5 | C5 | 1']))
      BODY-INTEGRAL:
        None
      BODY-FIRST-DERIVATIVE:
        None
      BODY-SECOND-DERIVATIVE:
        None
  STRUCTURE:
    COLUMNS: [No.,Name,Formula,State,C1,C2,C3,C4,C5,Tmin,Tmax,Eq]
    SYMBOL: [None,None,None,None,C1,C2,C3,C4,C5,Tmin,Tmax,VaPr]
    UNIT: [None,None,None,None,1,1,1,1,1,K,K,Pa]
  VALUES:
    - [1,'water','H2O','l',73.649,-7258.2,-7.3037,4.1653E-6,2,273.16,647.096,1]
```

Do not add a second `water`/`H2O`/`l` row in this table for another range, equation selector, or
source note. Merge component-state-specific values into the same row; if the source values
conflict, flag the conflict in notes. A separate `water`/`H2O`/`g` row is valid because the state is
different.

## Example 3: Equation table with scaled coefficients and derivatives

```yaml
ideal-gas-heat-capacity:
  TABLE-ID: 1
  DESCRIPTION:
    Ideal gas heat capacity polynomial.
  EQUATIONS:
    EQ-1:
      BODY:
        - res['heat capacity of ideal gas | Cp_IG | J/mol.K'] = (parms['a0 | a0 | 1'] + parms['a1 | a1 | 1E3']*args['temperature | T | K'] + parms['a2 | a2 | 1E5']*(args['temperature | T | K']**2) + parms['a3 | a3 | 1E8']*(args['temperature | T | K']**3) + parms['a4 | a4 | 1E11']*(args['temperature | T | K']**4))*parms['Universal-Gas-Constant | R | J/mol.K']
      BODY-INTEGRAL:
        - A1 = parms['a0 | a0 | 1']*args['temperature | T1 | K']
        - B1 = (parms['a1 | a1 | 1E3']/2)*(args['temperature | T1 | K']**2)
        - C1 = (parms['a2 | a2 | 1E5']/3)*(args['temperature | T1 | K']**3)
        - D1 = (parms['a3 | a3 | 1E8']/4)*(args['temperature | T1 | K']**4)
        - E1 = (parms['a4 | a4 | 1E11']/5)*(args['temperature | T1 | K']**5)
        - res1 = A1 + B1 + C1 + D1 + E1
        - A2 = parms['a0 | a0 | 1']*args['temperature | T2 | K']
        - B2 = (parms['a1 | a1 | 1E3']/2)*(args['temperature | T2 | K']**2)
        - C2 = (parms['a2 | a2 | 1E5']/3)*(args['temperature | T2 | K']**3)
        - D2 = (parms['a3 | a3 | 1E8']/4)*(args['temperature | T2 | K']**4)
        - E2 = (parms['a4 | a4 | 1E11']/5)*(args['temperature | T2 | K']**5)
        - res2 = A2 + B2 + C2 + D2 + E2
        - res = parms['Universal-Gas-Constant | R | J/mol.K']*(res2 - res1)
      BODY-FIRST-DERIVATIVE:
        - res = parms['Universal-Gas-Constant | R | J/mol.K']*(parms['a1 | a1 | 1E3'] + 2*parms['a2 | a2 | 1E5']*args['temperature | T | K'] + 3*parms['a3 | a3 | 1E8']*(args['temperature | T | K']**2) + 4*parms['a4 | a4 | 1E11']*(args['temperature | T | K']**3))
      BODY-SECOND-DERIVATIVE:
        - res = parms['Universal-Gas-Constant | R | J/mol.K']*(2*parms['a2 | a2 | 1E5'] + 6*parms['a3 | a3 | 1E8']*args['temperature | T | K'] + 12*parms['a4 | a4 | 1E11']*(args['temperature | T | K']**2))
  STRUCTURE:
    COLUMNS: [No.,Name,Formula,State,a0,a1,a2,a3,a4,R,Eq]
    SYMBOL: [None,None,None,None,a0,a1,a2,a3,a4,R,Cp_IG]
    UNIT: [None,None,None,None,1,1E3,1E5,1E8,1E11,1,J/mol.K]
  VALUES:
    - [1,'argon','Ar','g',2.500,0.000,0.000,0.000,0.000,8.314,1]
```

## Example 4: Reference-style vapor pressure equation

Use this pattern for correlations that depend on reduced temperature and critical pressure.

```yaml
vapor-pressure:
  TABLE-ID: 3
  DESCRIPTION:
    Vapor pressure in bar as a function of temperature in K.
  EQUATIONS:
    EQ-1:
      BODY:
        - Tr = args['temperature | T | K'] / parms['critical-temperature | Tc | K']
        - tau = 1 - Tr
        - expo = (1 / Tr) * (
            parms['A | A | 1'] * tau +
            parms['B | B | 1'] * math.pow(tau, 1.5) +
            parms['C | C | 1'] * math.pow(tau, 2.5) +
            parms['D | D | 1'] * math.pow(tau, 5)
          )
        - ps_bar = parms['critical-pressure | Pc | bar'] * math.exp(expo)
        - res['vapor-pressure | VaPr | bar'] = ps_bar
      BODY-INTEGRAL:
        None
      BODY-FIRST-DERIVATIVE:
        None
      BODY-SECOND-DERIVATIVE:
        None
  STRUCTURE:
    COLUMNS: [No.,Name,Formula,State,A,B,C,D,critical-temperature,critical-pressure,Eq]
    SYMBOL: [None,None,None,None,A,B,C,D,Tc,Pc,VaPr]
    UNIT: [None,None,None,None,1,1,1,1,K,bar,bar]
  VALUES:
    - [1,'water','H2O','g',-7.870154,1.906774,-2.310330,-2.063390,647.096,220.640,1]
```

## Example 5: Constants table

```yaml
Custom-Constants:
  TABLE-ID: 4
  DESCRIPTION:
    Custom constants used by downstream calculations.
  CONSTANTS: []
  STRUCTURE:
    COLUMNS: [No.,Name,Symbol,State,Value,Unit,Description]
  VALUES:
    - [1,'Universal Gas Constant','R','g',8.314,'J/mol.K','Universal gas constant.']
    - [2,'enthalpy of reaction','dH_rxn','g',{"R1": -42, "R2": -50},'kJ/mol','Reaction enthalpy by reaction id.']
```

## Example 6: Matrix parameter table

```yaml
NRTL Non-randomness parameters:
  TABLE-ID: 5
  DESCRIPTION:
    Binary NRTL matrix parameters.
  MATRIX-SYMBOL:
    - a constant: a
    - b constant: b
    - c constant: c
    - non-randomness parameter: alpha
  STRUCTURE:
    COLUMNS: [No.,Mixture,Name,Formula,State,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
    SYMBOL: [None,None,None,None,None,a_i_1,a_i_2,b_i_1,b_i_2,c_i_1,c_i_2,alpha_i_1,alpha_i_2]
    UNIT: [None,None,None,None,None,1,1,1,1,1,1,1,1]
  VALUES:
    - [1,methanol|ethanol,methanol,CH3OH,l,0,0.300492719,0,1.564200272,0,35.05450323,0,4.481683583]
    - [2,methanol|ethanol,ethanol,C2H5OH,l,0.380229054,0,-20.63243601,0,0.059982839,0,4.481683583,0]
```

For this binary pair, the first row stores values from methanol to each column
component, and the second row stores values from ethanol to each column
component. For example, `a_i_2` in the methanol row is `a_methanol_ethanol`,
while `a_i_1` in the ethanol row is `a_ethanol_methanol`.

Additional binary pairs can be stored in the same table by adding another pair
of rows with a different `Mixture` value:

```yaml
  VALUES:
    - [1,methanol|ethanol,methanol,CH3OH,l,0,0.300492719,0,1.564200272,0,35.05450323,0,4.481683583]
    - [2,methanol|ethanol,ethanol,C2H5OH,l,0.380229054,0,-20.63243601,0,0.059982839,0,4.481683583,0]
    - [1,methane|ethanol,methane,CH4,g,0,0.300492719,0,1.564200272,0,35.05450323,0,4.481683583]
    - [2,methane|ethanol,ethanol,C2H5OH,l,0.380229054,0,-20.63243601,0,0.059982839,0,4.481683583,0]
```

For a ternary build such as:

```python
multi_component_mixture = [methanol, ethanol, butyl_methyl_ether]
```

store all required binary pairs unless the build call passes `mixture_names`.
This ternary case has three binary pairs and therefore six `VALUES` rows:

```yaml
  VALUES:
    - [1,methanol|ethanol,methanol,CH3OH,l,0,0.300492719,0,1.564200272,0,35.05450323,0,4.481683583]
    - [2,methanol|ethanol,ethanol,C2H5OH,l,0.380229054,0,-20.63243601,0,0.059982839,0,4.481683583,0]
    - [1,methanol|butyl-methyl-ether,methanol,CH3OH,l,0,0.1201,0,2.25,0,18.4,0,0.680715]
    - [2,methanol|butyl-methyl-ether,butyl-methyl-ether,C5H12O,l,0.2152,0,-8.75,0,0.041,0,0.680715,0]
    - [1,ethanol|butyl-methyl-ether,ethanol,C2H5OH,l,0,0.1803,0,3.268,0,22.6,0,0.680715]
    - [2,ethanol|butyl-methyl-ether,butyl-methyl-ether,C5H12O,l,0.2457,0,-12.48,0,0.052,0,0.680715,0]
```

Do not encode this as `methanol|ethanol|butyl-methyl-ether`, and do not add
`a_i_3`, `b_i_3`, `c_i_3`, or `alpha_i_3` columns for this builder workflow.

## Example 7: Full reference wrapper with mixed tables

Use this format when creating a loadable reference file or a `REFERENCE_CONTENT` block.

```yaml
REFERENCES:
  CUSTOM-REF-1:
    DATABOOK-ID: 1
    TABLES:
      general-data:
        TABLE-ID: 1
        DESCRIPTION:
          General data.
        DATA: []
        STRUCTURE:
          COLUMNS: [No.,Name,Formula,State,critical-temperature]
          SYMBOL: [None,None,None,None,Tc]
          UNIT: [None,None,None,None,K]
          CONVERSION: [None,None,None,None,1]
        VALUES:
          - [1,'water','H2O','l',647.096]
      Custom-Constants:
        TABLE-ID: 2
        DESCRIPTION:
          Constants used by equations.
        CONSTANTS: []
        STRUCTURE:
          COLUMNS: [No.,Name,Symbol,State,Value,Unit,Description]
        VALUES:
          - [1,'Universal Gas Constant','R','g',8.314,'J/mol.K','Scalar constant.']
```
