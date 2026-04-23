# =======================================
# ! LOAD THERMODB INLINE SOURCE
# =======================================
# SECTION: reference content
# NOTE: used for eos
REFERENCE_CONTENT = """
REFERENCES:
    CUSTOM-REF-1:
      DATABOOK-ID: 1
      TABLES:
        ideal-gas-heat-capacity:
          TABLE-ID: 1
          DESCRIPTION:
            This table provides the heat capacity at constant pressure of ideal gas (Cp_IG) in J/mol.K as a function of temperature (T) in K.
          EQUATIONS:
            EQ-1:
              BODY:
                - res['ideal-gas-heat-capacity | Cp_IG | J/mol.K'] = (parms['a0 | a0 | 1'] + parms['a1 | a1 | 1E3']*args['temperature | T | K'] + parms['a2 | a2 | 1E5']*(args['temperature | T | K']**2) + parms['a3 | a3 | 1E8']*(args['temperature | T | K']**3) + parms['a4 | a4 | 1E11']*(args['temperature | T | K']**4))*parms['Universal-Gas-Constant | R | J/mol.K']
              BODY-INTEGRAL:
                  - A1 = parms['a0 | a0 | 1']*args['temperature | T1 | K']
                  - B1 = (parms['a1 | a1 | 1E3']/2)*(args['temperature | T1 | K']**2)
                  - C1 = (parms['a2 | a2 | 1E5']/3)*(args['temperature | T1 | K']**3)
                  - D1 = (parms['a3 | a3 | 1E8']/4)*(args['temperature | T1 | K']**4)
                  - E1 = (parms['a4 | a4 | 1E11']/5)*(args['temperature | T1 | K']**5)
                  - res1 =  A1 + B1 + C1 + D1 + E1
                  - A2 = parms['a0 | a0 | 1']*args['temperature | T2 | K']
                  - B2 = (parms['a1 | a1 | 1E3']/2)*(args['temperature | T2 | K']**2)
                  - C2 = (parms['a2 | a2 | 1E5']/3)*(args['temperature | T2 | K']**3)
                  - D2 = (parms['a3 | a3 | 1E8']/4)*(args['temperature | T2 | K']**4)
                  - E2 = (parms['a4 | a4 | 1E11']/5)*(args['temperature | T2 | K']**5)
                  - res2 =  A2 + B2 + C2 + D2 + E2
                  - res = parms['Universal-Gas-Constant | R | J/mol.K']*(res2 - res1)
              BODY-FIRST-DERIVATIVE:
                  - res = parms['Universal-Gas-Constant | R | J/mol.K']*(parms['a1 | a1 | 1E3'] + 2*parms['a2 | a2 | 1E5']*args['temperature | T | K'] + 3*parms['3 | a3 | 1E8']*(args['temperature | T | K']**2) + 4*parms['a4 | a4 | 1E11']*(args['temperature | T | K']**3))
              BODY-SECOND-DERIVATIVE:
                  - res = parms['Universal-Gas-Constant | R | J/mol.K']*(2*parms['a2 | a2 | 1E5'] + 6*parms['3 | a3 | 1E8']*args['temperature | T | K'] + 12*parms['a4 | a4 | 1E11']*(args['temperature | T | K']**2))
          STRUCTURE:
            COLUMNS: [No.,Name,Formula,State,a0,a1,a2,a3,a4,R,Eq]
            SYMBOL: [None,None,None,None,a0,a1,a2,a3,a4,R,Cp_IG]
            UNIT: [None,None,None,None,1,1E3,1E5,1E8,1E11,1,J/mol.K]
          VALUES:
            None
        general-data:
          TABLE-ID: 2
          DESCRIPTION:
            This table provides the general data of different chemical species participating in the CO2 hydrogenation reaction and includes molecular weight (MW) in g/mol, critical temperature (Tc) in K, critical pressure (Pc) in MPa, and critical molar volume (Vc) in m3/kmol. The table also includes the critical compressibility factor (Zc), acentric factor (AcFa), enthalpy of formation (EnFo) in kJ/mol, and Gibbs energy of formation (GiEnFo) in kJ/mol. The chemical state of the species is also provided in the table and hence the enthalpy of formation and Gibbs energy of formation are provided for the ideal gas and liquid state are designated as EnFo_IG, GiEnFo_IG, EnFo_LIQ, and GiEnFo_LIQ, respectively.
          DATA: []
          STRUCTURE:
            COLUMNS: [No.,Name,Formula,State,Molecular-Weight,Critical-Temperature,Critical-Pressure,Critical-Molar-Volume,Critical-Compressibility-Factor,Acentric-Factor,Enthalpy-of-Formation,Gibbs-Energy-of-Formation]
            SYMBOL: [None,None,None,None,MW,Tc,Pc,Vc,Zc,AcFa,EnFo_IG,GiEnFo_IG]
            UNIT: [None,None,None,None,g/mol,K,MPa,m3/kmol,None,None,kJ/mol,kJ/mol]
            CONVERSION: [None,None,None,None,1,1,1,1,1,1,1,1]
          VALUES:
            None
        vapor-pressure:
          TABLE-ID: 3
          DESCRIPTION:
            This table provides the vapor pressure (P) in Pa as a function of temperature (T) in K.
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
            COLUMNS: [No.,Name,Formula,State,C1,C2,C3,C4,C5,Tmin,P(Tmin),Tmax,P(Tmax),Eq]
            SYMBOL: [None,None,None,None,C1,C2,C3,C4,C5,Tmin,P(Tmin),Tmax,P(Tmax),VaPr]
            UNIT: [None,None,None,None,1,1,1,1,1,K,Pa,K,Pa,Pa]
          VALUES:
            None
        liquid-heat-capacity:
          TABLE-ID: 4
          DESCRIPTION:
            This table provides the heat capacity at constant pressure of liquid (Cp_LIQ) in J/mol.K as a function of temperature (T) in K.
          EQUATIONS:
            EQ-1:
              BODY:
                - res['liquid-heat-capacity | Cp_LIQ | J/mol.K'] = (parms['a0 | a0 | 1'] + parms['a1 | a1 | 1E3']*args['temperature | T | K'] + parms['a2 | a2 | 1E5']*(args['temperature | T | K']**2) + parms['a3 | a3 | 1E8']*(args['temperature | T | K']**3) + parms['a4 | a4 | 1E11']*(args['temperature | T | K']**4))*parms['Universal-Gas-Constant | R | J/mol.K']
              BODY-INTEGRAL:
                  - A1 = parms['a0 | a0 | 1']*args['temperature | T1 | K']
                  - B1 = (parms['a1 | a1 | 1E3']/2)*(args['temperature | T1 | K']**2)
                  - C1 = (parms['a2 | a2 | 1E5']/3)*(args['temperature | T1 | K']**3)
                  - D1 = (parms['a3 | a3 | 1E8']/4)*(args['temperature | T1 | K']**4)
                  - E1 = (parms['a4 | a4 | 1E11']/5)*(args['temperature | T1 | K']**5)
                  - res1 =  A1 + B1 + C1 + D1 + E1
                  - A2 = parms['a0 | a0 | 1']*args['temperature | T2 | K']
                  - B2 = (parms['a1 | a1 | 1E3']/2)*(args['temperature | T2 | K']**2)
                  - C2 = (parms['a2 | a2 | 1E5']/3)*(args['temperature | T2 | K']**3)
                  - D2 = (parms['a3 | a3 | 1E8']/4)*(args['temperature | T2 | K']**4)
                  - E2 = (parms['a4 | a4 | 1E11']/5)*(args['temperature | T2 | K']**5)
                  - res2 =  A2 + B2 + C2 + D2 + E2
                  - res = parms['Universal-Gas-Constant | R | J/mol.K']*(res2 - res1)
              BODY-FIRST-DERIVATIVE:
                  None
              BODY-SECOND-DERIVATIVE:
                  None
          STRUCTURE:
            COLUMNS: [No.,Name,Formula,State,a0,a1,a2,a3,a4,R,Eq]
            SYMBOL: [None,None,None,None,a0,a1,a2,a3,a4,R,Cp_LIQ]
            UNIT: [None,None,None,None,1,1E3,1E5,1E8,1E11,1,J/mol.K]
          VALUES:
            None
        enthalpy-of-vaporization:
          TABLE-ID: 5
          DESCRIPTION:
            This table provides the enthalpy of vaporization (EnVap) in J/mol as a function of temperature (T) in K.
          EQUATIONS:
            EQ-1:
              BODY:
                - t = 1 - args['temperature | T | K']/parms['critical-temperature | Tc | K']
                - parms['A | A | 1'] = parms['A | A | 1'] * math.pow(t, 1/3)
                - parms['B | B | 1'] = parms['B | B | 1'] * math.pow(t, 2/3)
                - parms['C | C | 1'] = parms['C | C | 1'] * math.pow(t, 1)
                - parms['D | D | 1'] = parms['D | D | 1'] * math.pow(t, 2)
                - parms['E | E | 1'] = parms['E | E | 1'] * math.pow(t, 6)
                - parms['F | F | 1'] = parms['universal-gas-constant | R | J/mol.K'] * parms['critical-temperature | Tc | K']
                - res['enthalpy-of-vaporization | EnVap | J/mol'] = parms['F | F | 1'] * (parms['A | A | 1'] + parms['B | B | 1'] + parms['C | C | 1'] + parms['D | D | 1'] + parms['E | E | 1'])
              BODY-INTEGRAL:
                  None
              BODY-FIRST-DERIVATIVE:
                  None
              BODY-SECOND-DERIVATIVE:
                  None
          STRUCTURE:
            COLUMNS: [No.,Name,Formula,State,A,B,C,D,E,critical-temperature,universal-gas-constant,Eq]
            SYMBOL: [None,None,None,None,A,B,C,D,E,Tc,R,EnVap]
            UNIT: [None,None,None,None,1,1,1,1,1,K,J/mol.K,J/mol]
          VALUES:
            None
"""
