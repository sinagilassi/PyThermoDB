from pathlib import Path

from pyThermoDB import (
    ConstantsThermoDB,
    build_constants_thermodb_from_reference,
)
from pyThermoDB.core import TableConstants


def _reference_path() -> str:
    return str(
        Path(__file__).resolve().parents[1]
        / "examples"
        / "external-ref"
        / "source-ref-1.yml"
    )


def test_build_constants_thermodb_from_reference_builds_all_tables():
    result = build_constants_thermodb_from_reference(_reference_path())

    assert isinstance(result, ConstantsThermoDB)
    constants = result.thermodb.check_constants()
    assert set(constants) == {"Custom-Constants", "Custom-Constants-2"}
    assert all(isinstance(value, TableConstants) for value in constants.values())
    assert constants["Custom-Constants"].get_constant("R")["value"] == 8.314
    assert constants["Custom-Constants"].get_constant("dH_rxn")["value"] == {
        "R1": -42,
        "R2": -50,
        "R3": -62,
    }
    assert result.reference_thermodb is not None
    assert result.reference_thermodb.rules["CONSTANTS"]["Universal Gas Constant"] == "R"


def test_build_constants_thermodb_from_reference_filters_by_constant_symbol():
    result = build_constants_thermodb_from_reference(
        _reference_path(),
        constants="dG_rxn",
    )

    assert isinstance(result, ConstantsThermoDB)
    constants = result.thermodb.check_constants()
    assert set(constants) == {"Custom-Constants-2"}
    assert constants["Custom-Constants-2"].get_constant("dG_rxn")["value"] == {
        "R1": -420,
        "R2": -500,
        "R3": -602,
    }


def test_build_constants_thermodb_from_reference_returns_none_for_missing_constant():
    result = build_constants_thermodb_from_reference(
        _reference_path(),
        constants="missing",
    )

    assert result is None
