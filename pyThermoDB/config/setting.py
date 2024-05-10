# import packages/modules
# internal


# api url
API_URL = "https://script.google.com/macros/s/AKfycbzA78GeYUGfwNq_9aeQyNeP3dG82T5NehqW_SJzWBDFXHQiD7DCQuZlGFmZ9kVuZvdX/exec"

# thermodynamics databook
THERMODYNAMICS_DATABOOK = [
    {
        "id": 1,
        "book": "Perry's Chemical Engineers' Handbook",
        "tables": [
            {
                "id": 1,
                "name": "TABLE 2-8 Vapor Pressure of Inorganic and Organic Liquids",
                "equations": [
                    {
                        "id": 1,
                        "function": "res = math.exp(params['C1'] + params['C2']/vars['T'] + params['C3']*math.log(vars['T']) + params['C4']*(vars['T']**params['C5']))",
                        "args": [
                            {
                                "id": 1,
                                "name": "temperature",
                                "parameter": "T",
                                "unit": "K"
                            }
                        ],
                        "params": [
                            {
                                "id": 1,
                                "name": "C1",
                                "parameter": "C1",
                                "unit": ""
                            },
                            {
                                "id": 2,
                                "name": "C2",
                                "parameter": "C2",
                                "unit": ""
                            },
                            {
                                "id": 3,
                                "name": "C3",
                                "parameter": "C3",
                                "unit": ""
                            },
                            {
                                "id": 4,
                                "name": "C4",
                                "parameter": "C4",
                                "unit": ""
                            },
                            {
                                "id": 5,
                                "name": "C5",
                                "parameter": "C5",
                                "unit": ""
                            }
                        ],
                        "return": [
                            {
                                "id": 1,
                                "name": "vapor pressure",
                                "parameter": "Ps",
                                "unit": "Pa"
                            }
                        ]
                    }
                ]
            },
            {
                "id": 2,
                "name": "TABLE 2-179 Enthalpies and Gibbs Energies of Formation, Entropies, and Net Enthalpies of Combustion",
                "equations": []

            },
            {
                "id": 3,
                "name": "TABLE 2-141 Critical Constants and Acentric Factors of Inorganic and Organic Compounds",
                "equations": []
            },
            {
                "id": 4,
                "name": "TABLE 2-153 Heat Capacities of Inorganic and Organic Liquids",
                "equations": [
                    {
                        "id": 1,
                        "functions": "res = C[0] + C[1]*T + C[2]*(T**2) + C[3]*(T**3) + C[4]*(T**4)",
                        "args": [
                            {
                                "id": 1,
                                "name": "C1",
                                "parameter": "C1",
                                "unit": ""
                            },
                            {
                                "id": 2,
                                "name": "C2",
                                "parameter": "C2",
                                "unit": ""
                            },
                            {
                                "id": 3,
                                "name": "C3",
                                "parameter": "C3",
                                "unit": ""
                            },
                            {
                                "id": 4,
                                "name": "C4",
                                "parameter": "C4",
                                "unit": ""
                            },
                            {
                                "id": 5,
                                "name": "C5",
                                "parameter": "C5",
                                "unit": ""
                            },
                            {
                                "id": 6,
                                "name": "temperature",
                                "parameter": "T",
                                "unit": "K"
                            }
                        ],
                        "return": [
                            {
                                "id": 1,
                                "name": "heat capacity",
                                "parameter": "Cp[l]",
                                "unit": "J/(kmol.K)"
                            }
                        ]
                    },
                    {
                        "id": 2,
                        "function": "Tr = T/Tc \n \
                        t = 1-Tr \n \
                        res = (C[0]**2)/t + C[1] - 2*C[0]*C[2]*t - C[2]*C[3]*(t**2) - (C[2]**2)*(t**3)/3 - (C[2])*(C[3])*(t**4)/2 - (C[3]**2)*(t**5)/5",
                        "args": [
                            {
                                "id": 1,
                                "name": "C1",
                                "parameter": "C1",
                                "unit": ""
                            },
                            {
                                "id": 2,
                                "name": "C2",
                                "parameter": "C2",
                                "unit": ""
                            },
                            {
                                "id": 3,
                                "name": "C3",
                                "parameter": "C3",
                                "unit": ""
                            },
                            {
                                "id": 4,
                                "name": "C4",
                                "parameter": "C4",
                                "unit": ""
                            },
                            {
                                "id": 5,
                                "name": "C5",
                                "parameter": "C5",
                                "unit": ""
                            },
                            {
                                "id": 6,
                                "name": "temperature",
                                "parameter": "T",
                                "unit": "K"
                            },
                            {
                                "id": 7,
                                "name": "critical temperature",
                                "parameter": "Tc",
                                "unit": "K"
                            }
                        ],
                        "return": [
                            {
                                "id": 1,
                                "name": "heat capacity",
                                "parameter": "Cp[l]",
                                "unit": "J/(kmol.K)"
                            }
                        ]
                    }
                ]
            }
        ]
    },
    {
        "id": 2,
        "book": "Chemical Thermodynamics for Process Simulation",
        "tables": [
            {
                "id": 1,
                "name": "Table A.1 General data for selected compounds",
                "equations": ""
            },
            {
                "id": 2,
                "name": "Table A.2 Vapor pressure correlations for selected compounds",
                "equations": ""
            },
            {
                "id": 3,
                "name": "Table A.3 Liquid density correlations for selected compounds"
            },
            {
                "id": 4,
                "name": "Table A.4 Enthalpy of vaporization correlations for selected compounds"
            },
            {
                "id": 5,
                "name": "Table A.5 Liquid heat capacity correlations for selected compounds"
            },
            {
                "id": 6,
                "name": "Table A.6 Ideal gas heat capacity correlations for selected compounds"
            },
            {
                "id": 7,
                "name": "Table A.7 Liquid viscosity correlations for selected compounds"
            },
            {
                "id": 8,
                "name": "Table A.8 Vapor viscosity correlations for selected compounds at low pressures"
            },
            {
                "id": 9,
                "name": "Table A.9 Liquid thermal conductivity correlations for selected compounds"
            },
            {
                "id": 10,
                "name": "Table A.10 Vapor thermal conductivity correlations for selected compounds at low pressures"
            },
            {
                "id": 11,
                "name": "Table A.11 Surface tension correlations for selected compounds"
            },
        ]
    }
]
