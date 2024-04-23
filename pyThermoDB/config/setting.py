# import packages/modules
# internal
from pyThermoDB.utils import log2Col

THERMODYNAMICS_DATABOOK = [
    {
        "id": 1,
        "book": "Perry's Chemical Engineers' Handbook",
        "tables": [
            {
                "id": 1,
                "name": "TABLE 2-8 Vapor Pressure of Inorganic and Organic Liquids",
                "equation": [
                    {
                        "id": 1,
                        "function": "res = exp(C[0] + C[1]/T + C[2]*log(T) + C[3]*(T**C[4]))",
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
                "equation": []

            },
            {
                "id": 3,
                "name": "TABLE 2-141 Critical Constants and Acentric Factors of Inorganic and Organic Compounds",
                "equation": []
            },
            {
                "id": 4,
                "name": "TABLE 2-153 Heat Capacities of Inorganic and Organic Liquids",
                "equation": [
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
                "equation": ""
            },
            {
                "id": 2,
                "name": "Table A.2 Vapor pressure correlations for selected compounds",
                "equation": [
                    {
                        "id": 1,
                        "function": ""
                    }
                ]
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


class SettingDatabook():
    '''
    load databook reference
    '''
    # selected databook
    selected_db = None
    # selected table
    selected_tb = None
    def __init__(self):
        self.databook = THERMODYNAMICS_DATABOOK
    
    def get_thermo_databook(self):
        res = [[str(item['id']), item['book'], item['tables']] for item in self.databook]
        
        # find the maximum length of each column
        max_length_book = int(max([len(item[1]) for item in res]))
        max_length = max_length_book + 10
        # column names
        column_names = ['id', 'book']
        data = [column_names, *res]
        dash = '-' * max_length
        # print table
        # table head format
        table_head = f'{{:^5s}} {{:^{max_length_book}s}}'
        for i in range(len(data)):
            if i == 0:
                print(dash)
                print(table_head.format(data[i][0], data[i][1]))
                print(dash)
            else:
                print('{:^5s}{:>0s}'.format(data[i][0], data[i][1]))
        print(dash)
        
        # input
        val = input("Which databook do you want?: ") 
        print(val)
        
        # check val is a number
        if not val.isdigit():
            print("Invalid input. Please enter a number.")
            return
        val = int(val)
        # check val is in range
        if val < 1 or val > len(res):
            print("Invalid input. Please enter a number between 1 and {}".format(len(res)))
            return
        # choose databook tables
        self.selected_db = [item[2] for item in res if item[0] == str(val-1)][0]
        print("The tables in this databook are: ")
        
        selected_tbs = [[str(item['id']), item['name']] for item in self.selected_db]
        column_names2 = ['id', 'table']
        data2 = [column_names2, *selected_tbs]
        # display
        for i in range(len(data2)):
            if i == 0:
                print(dash)
                print(table_head.format(data2[i][0], data2[i][1]))
                print(dash)
            else:
                print('{:^5s}{:>0s}'.format(data2[i][0], data2[i][1]))
        print(dash)
        
        # input
        val = input("Which table do you choose?: ") 
        print(val)
        
        self.selected_tb = selected_tbs[int(val)-1]