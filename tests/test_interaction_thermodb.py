import tempfile
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

import pyThermoDB as ptdb
from pythermodb_settings.models import Component

from pyThermoDB.core import TableInteractionData
from pyThermoDB.references import ReferenceChecker
from pyThermoDB.thermodb import MixtureThermoDB


FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "interactions"
    / "interaction-format-1.yaml"
)


class TestInteractionThermoDBBuilders(unittest.TestCase):
    def setUp(self):
        self.components = [
            Component(name="sodium-ion", formula="Na{+}", state="aq"),
            Component(name="potassium-ion", formula="K{+}", state="aq"),
            Component(name="chloride-ion", formula="Cl{-}", state="aq"),
        ]
        self.config = {
            "pitzer": {
                "databook": "PITZER-EXAMPLE",
                "table": "Pitzer ternary interaction parameters",
            }
        }

    def test_build_interaction_thermodb_selects_exact_unordered_set(self):
        result = ptdb.build_interaction_thermodb(
            components=self.components,
            reference_config=self.config,
            custom_reference={"reference": [str(FIXTURE_PATH)]},
        )

        self.assertIsNotNone(result)
        selected = result.list_data()["pitzer"]
        self.assertIsInstance(selected, TableInteractionData)
        self.assertEqual(
            selected.mixtures,
            [("potassium-ion", "sodium-ion", "chloride-ion")],
        )
        self.assertEqual(
            selected.get("psi", "potassium-ion|sodium-ion|chloride-ion"),
            -0.0018,
        )
        self.assertIsNone(
            selected.get("psi", "sodium-ion|potassium-ion|chloride-ion")
        )

    def test_builder_preserves_all_differently_ordered_matching_rows(self):
        reference = """
REFERENCES:
  TEST:
    DATABOOK-ID: 1
    TABLES:
      Interactions:
        TABLE-ID: 1
        INTERACTION-SYMBOL: [psi]
        STRUCTURE:
          COLUMNS: [Mixture, psi]
          SYMBOL: [None, psi]
          UNIT: [None, 1]
        VALUES:
          - ["A|B|C", 1.0]
          - ["C|B|A", 2.0]
          - ["A|B", 3.0]
          - ["A|B|C|D", 4.0]
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "interactions.yaml"
            path.write_text(reference, encoding="utf-8")
            components = [
                Component(name="A", formula="A", state="aq"),
                Component(name="B", formula="B", state="aq"),
                Component(name="C", formula="C", state="aq"),
            ]
            result = ptdb.build_interaction_thermodb(
                components=components,
                reference_config={
                    "interaction": {"databook": "TEST", "table": "Interactions"}
                },
                custom_reference={"reference": [str(path)]},
            )

        self.assertIsNotNone(result)
        selected = result.list_data()["interaction"]
        self.assertEqual(selected.mixtures, [("A", "B", "C"), ("C", "B", "A")])
        self.assertEqual(selected.get("psi", "A|B|C"), 1.0)
        self.assertEqual(selected.get("psi", "C|B|A"), 2.0)

    def test_checker_builds_interaction_reference_config(self):
        checker = ReferenceChecker(FIXTURE_PATH.read_text(encoding="utf-8"))
        config = checker.get_interaction_reference_configs(
            components=self.components,
        )

        self.assertIsNotNone(config)
        entry = config[
            "PITZER-EXAMPLE::Pitzer ternary interaction parameters"
        ]
        self.assertEqual(entry["databook"], "PITZER-EXAMPLE")
        self.assertEqual(entry["mode"], "INTERACTION-DATA")
        self.assertEqual(entry["labels"], {"psi": "psi", "zeta": "zeta"})
    def test_build_from_reference(self):
        result = ptdb.build_interaction_thermodb_from_reference(
            components=self.components,
            reference_content=FIXTURE_PATH.read_text(encoding="utf-8"),
        )

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.reference_thermodb)
        self.assertEqual(len(result.thermodb.list_data()), 1)

    def test_non_interaction_and_unavailable_tables_are_rejected(self):
        source = MagicMock()
        source.table_info.return_value = {"Type": "Data"}
        with patch("pyThermoDB.thermodb.init", return_value=source):
            self.assertIsNone(
                ptdb.build_interaction_thermodb(
                    components=self.components,
                    reference_config={
                        "general": {"databook": "TEST", "table": "General"}
                    },
                )
            )

        with self.assertRaises(Exception):
            ptdb.build_interaction_thermodb(
                components=self.components,
                reference_config={
                    "missing": {
                        "databook": "PITZER-EXAMPLE",
                        "table": "Missing",
                    }
                },
                custom_reference={"reference": [str(FIXTURE_PATH)]},
            )
    def test_no_exact_match_returns_none_and_invalid_components_fail(self):
        unmatched = [
            Component(name="sodium-ion", formula="Na{+}", state="aq"),
            Component(name="calcium-ion", formula="Ca{2+}", state="aq"),
            Component(name="chloride-ion", formula="Cl{-}", state="aq"),
            Component(name="carbon-dioxide", formula="CO2", state="aq"),
        ]
        self.assertIsNone(
            ptdb.build_interaction_thermodb(
                components=unmatched,
                reference_config=self.config,
                custom_reference={"reference": [str(FIXTURE_PATH)]},
            )
        )
        with self.assertRaises(ValueError):
            ptdb.build_interaction_thermodb(
                components=self.components[:1],
                reference_config=self.config,
                custom_reference={"reference": [str(FIXTURE_PATH)]},
            )


if __name__ == "__main__":
    unittest.main()
