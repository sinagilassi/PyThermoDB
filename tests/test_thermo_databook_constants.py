from pyThermoDB.references import ThermoDatabook


def test_databook_builds_constants_table():
    constants_csv = """
No.,Name,Symbol,State,Value,Unit,Description
1,Universal Gas Constant,R,g,8.314,J/mol.K,Gas constant
2,enthalpy of reaction,dH_rxn,g,"{R1: -42, R2: -50}",kJ/mol,Reaction enthalpy
3,custom constants,X,-,"[1, 2, 3]",,List constant
"""
    databook = ThermoDatabook("CUSTOM-REF-1")

    databook.add_constants_table(
        "Custom-Constants",
        constants_csv,
        description="Custom constants table",
    )
    databook.build()

    contents = databook.get_contents()
    table = contents["TABLES"]["Custom-Constants"]

    assert table["TABLE-ID"] == 1
    assert table["DESCRIPTION"] == "Custom constants table"
    assert table["CONSTANTS"] == []
    assert table["STRUCTURE"] == {
        "COLUMNS": [
            "No.",
            "Name",
            "Symbol",
            "State",
            "Value",
            "Unit",
            "Description",
        ]
    }
    assert table["VALUES"] == [
        [
            1,
            "Universal Gas Constant",
            "R",
            "g",
            8.314,
            "J/mol.K",
            "Gas constant",
        ],
        [
            2,
            "enthalpy of reaction",
            "dH_rxn",
            "g",
            {"R1": -42, "R2": -50},
            "kJ/mol",
            "Reaction enthalpy",
        ],
        [
            3,
            "custom constants",
            "X",
            "-",
            [1, 2, 3],
            None,
            "List constant",
        ],
    ]
