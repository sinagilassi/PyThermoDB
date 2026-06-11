from pathlib import Path

from pyThermoDB import (
    build_constants_thermodb,
    check_and_build_constants_thermodb,
)
from pyThermoDB.builder import CompBuilder
from pyThermoDB.core import TableConstants


def _reference_path() -> str:
    return str(
        Path(__file__).resolve().parents[1]
        / "examples"
        / "external-ref"
        / "source-ref-1.yml"
    )


def _custom_reference() -> dict[str, list[str]]:
    return {"reference": [_reference_path()]}


def _reference_config() -> dict[str, dict[str, object]]:
    return {
        "Custom-Constants": {
            "databook": "CUSTOM-REF-1",
            "table": "Custom-Constants",
            "labels": {
                "Universal Gas Constant": "R",
                "enthalpy of reaction": "dH_rxn",
            },
        },
        "Custom-Constants-2": {
            "databook": "CUSTOM-REF-1",
            "table": "Custom-Constants-2",
            "labels": {
                "enthalpy of reaction": "dG_rxn",
            },
        },
    }


def test_build_constant_thermodb_builds_explicit_sources():
    result = build_constants_thermodb(
        reference_config=_reference_config(),
        custom_reference=_custom_reference(),
    )

    assert isinstance(result, CompBuilder)
    constants = result.check_constants()
    assert set(constants) == {"Custom-Constants", "Custom-Constants-2"}
    assert all(isinstance(value, TableConstants)
               for value in constants.values())
    assert constants["Custom-Constants"].get_constant("R")["value"] == 8.314


def test_check_and_build_constant_thermodb_filters_by_requested_constant():
    result = check_and_build_constants_thermodb(
        reference_config=_reference_config(),
        custom_reference=_custom_reference(),
        constants="dG_rxn",
    )

    assert isinstance(result, CompBuilder)
    constants = result.check_constants()
    assert set(constants) == {"Custom-Constants-2"}
    assert constants["Custom-Constants-2"].get_constant("dG_rxn")["value"] == {
        "R1": -420,
        "R2": -500,
        "R3": -602,
    }


def test_check_and_build_constant_thermodb_returns_none_for_missing_constant():
    result = check_and_build_constants_thermodb(
        reference_config=_reference_config(),
        custom_reference=_custom_reference(),
        constants="missing",
    )

    assert result is None


def test_build_constant_thermodb_accepts_wrapped_yaml_config():
    reference_config = """
CONSTANTS:
  Custom-Constants:
    databook: CUSTOM-REF-1
    table: Custom-Constants
    labels:
      Universal Gas Constant: R
"""

    result = build_constants_thermodb(
        reference_config=reference_config,
        custom_reference=_custom_reference(),
    )

    assert isinstance(result, CompBuilder)
    constants = result.check_constants()
    assert set(constants) == {"Custom-Constants"}
    assert constants["Custom-Constants"].get_constant("R")["value"] == 8.314
