from pathlib import Path

from pyThermoDB.references import ReferenceChecker


def _checker() -> ReferenceChecker:
    reference_path = (
        Path(__file__).resolve().parents[1]
        / "examples"
        / "external-ref"
        / "source-ref-1.yml"
    )
    return ReferenceChecker(str(reference_path))


def test_constants_tables_are_discovered():
    checker = _checker()

    assert checker.is_constants_table("CUSTOM-REF-1", "Custom-Constants")
    assert checker.get_constants_tables("CUSTOM-REF-1") == [
        {"Databook": "CUSTOM-REF-1", "Table": "Custom-Constants"},
        {"Databook": "CUSTOM-REF-1", "Table": "Custom-Constants-2"},
    ]


def test_constants_table_data_preserves_value_types():
    checker = _checker()

    records = checker.get_constants_table_data(
        "CUSTOM-REF-1",
        "Custom-Constants",
    )

    assert records is not None
    assert records[0]["Value"] == 8.314
    assert records[1]["Unit"] is None
    assert records[3]["Value"] == {"R1": -42, "R2": -50, "R3": -62}
    assert records[5]["Value"] == [1, 2, 3]
    assert list(records[0].keys()) == [
        "No.",
        "Name",
        "Symbol",
        "State",
        "Value",
        "Unit",
        "Description",
    ]


def test_constant_lookup_and_availability():
    checker = _checker()

    by_symbol = checker.get_constant_data(
        "CUSTOM-REF-1",
        "Custom-Constants",
        "R",
    )
    by_name = checker.get_constant_data(
        "CUSTOM-REF-1",
        "Custom-Constants",
        "Universal Gas Constant",
        search_mode="NAME",
    )
    missing = checker.check_constant_availability(
        "CUSTOM-REF-1",
        "Custom-Constants",
        "missing",
    )

    assert by_symbol is not None
    assert by_symbol["Name"] == "Universal Gas Constant"
    assert by_name == by_symbol
    assert missing["available"] is False
    assert missing["data"] is None


def test_constants_do_not_appear_as_component_tables():
    checker = _checker()

    assert checker.get_table_components(
        "CUSTOM-REF-1",
        "Custom-Constants",
    ) is None
    assert checker.check_component_availability(
        component_name="Universal Gas Constant",
        component_formula="R",
        component_state="g",
        databook_name="CUSTOM-REF-1",
        table_name="Custom-Constants",
    ) == {}


def test_constants_mapping_is_available_for_property_mapping():
    checker = _checker()

    constants_mapping = checker.get_constants_mapping(
        "CUSTOM-REF-1",
        "Custom-Constants",
    )
    property_mapping = checker.generate_property_mapping(
        "CUSTOM-REF-1",
        "Custom-Constants",
    )

    assert constants_mapping["Universal Gas Constant"] == "R"
    assert constants_mapping["enthalpy of reaction"] == "dH_rxn"
    assert property_mapping == constants_mapping
