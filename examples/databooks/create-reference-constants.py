from rich import print

from pyThermoDB.references import ThermoDatabook, ThermoReference


constants_csv = """
No.,Name,Symbol,State,Value,Unit,Description
1,Universal Gas Constant,R,g,8.314,J/mol.K,The universal gas constant
2,enthalpy of reaction,dH_rxn,g,"{R1: -42, R2: -50, R3: -62}",kJ/mol,Reaction enthalpy
3,custom constants,X,-,"[1, 2, 3]",,List constant
"""

databook = ThermoDatabook("CUSTOM-REF-1")
databook.add_constants_table(
    table_name="Custom-Constants",
    data=constants_csv,
    description="This table provides custom constants."
)

reference = ThermoReference()
reference.add_databook(databook)
reference.build_references()

print(reference.get_references(res_format="yml"))
