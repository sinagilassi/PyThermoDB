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
    COLUMNS: [No.,Name,Formula,State,C1,C2,C3,C4,C5]
    SYMBOL: [None,None,None,None,C1,C2,C3,C4,VaPr]
    UNIT: [None,None,None,None,1,1,1,1,Pa]
  VALUES:
    - [1,'water','H2O','l',73.649,-7258.2,-7.3037,4.1653E-6,2]
```

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
