from pathlib import Path

from pyThermoDB.references import constants_reference_mapper


def _reference_path() -> str:
    return str(
        Path(__file__).resolve().parents[1]
        / "examples"
        / "external-ref"
        / "source-ref-1.yml"
    )


def test_constants_reference_mapper_builds_all_constants_rules():
    reference_thermodb = constants_reference_mapper(_reference_path())

    assert reference_thermodb is not None
    assert set(reference_thermodb.configs) == {
        "Custom-Constants",
        "Custom-Constants-2",
    }
    assert reference_thermodb.configs["Custom-Constants"]["mode"] == "CONSTANTS"
    assert reference_thermodb.configs["Custom-Constants"]["databook"] == "CUSTOM-REF-1"
    assert reference_thermodb.configs["Custom-Constants"]["table"] == "Custom-Constants"
    assert (
        reference_thermodb.rules["CONSTANTS"]["Universal Gas Constant"] == "R"
    )
    assert reference_thermodb.rules["CONSTANTS"]["enthalpy of reaction"] == "dG_rxn"
    assert "R" in reference_thermodb.labels
    assert "dH_rxn" in reference_thermodb.labels
    assert "dG_rxn" in reference_thermodb.labels


def test_constants_reference_mapper_filters_by_constant_symbol():
    reference_thermodb = constants_reference_mapper(
        _reference_path(),
        constants="dG_rxn",
    )

    assert reference_thermodb is not None
    assert set(reference_thermodb.configs) == {"Custom-Constants-2"}
    assert reference_thermodb.rules["CONSTANTS"]["enthalpy of reaction"] == "dG_rxn"


def test_constants_reference_mapper_returns_none_for_missing_constant():
    reference_thermodb = constants_reference_mapper(
        _reference_path(),
        constants="missing",
    )

    assert reference_thermodb is None
