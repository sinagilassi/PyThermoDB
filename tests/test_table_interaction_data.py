import unittest
from itertools import permutations

from pyThermoDB.core import TableInteractionData
from pyThermoDB.handlers import (
    TableInteractionDataDefinitionError,
    TableInteractionDataFormatError,
    TableInteractionDataLookupError,
)


TABLE_DATA = {
    "INTERACTION-SYMBOL": ["psi", "zeta"],
    "STRUCTURE": {
        "COLUMNS": ["No.", "Mixture", "psi", "zeta"],
        "SYMBOL": [None, None, "psi", "zeta"],
        "UNIT": [None, None, 1, 1],
    },
    "VALUES": [
        [1, "Na{+}|K{+}|Cl{-}", -0.0018, 0.25],
        [2, "Na{+}|Ca{2+}|Cl{-}", 0, None],
        [3, "Na{+}|Cl{-}|CO2", None, 0.0045],
        [4, "Na{+}|Cl{-}", 1.2, 0.0],
    ],
}


class DummyComponent:
    def __init__(self, name, formula, state="aq"):
        self.name, self.formula, self.state = name, formula, state


class TestTableInteractionData(unittest.TestCase):
    def setUp(self):
        self.data = TableInteractionData("PITZER", "interaction", TABLE_DATA)

    def test_scalar_lookup_and_null_zero_semantics(self):
        self.assertEqual(self.data.get("psi", "Na{+}|K{+}|Cl{-}"), -0.0018)
        self.assertEqual(self.data.get("zeta", ["Na{+}", "K{+}", "Cl{-}"]), 0.25)
        self.assertIsNone(self.data.get("psi", "Na{+}|Cl{-}|CO2"))
        self.assertEqual(self.data.get("psi", "Na{+}|Ca{2+}|Cl{-}"), 0)
        self.assertTrue(self.data.has("psi", "Na{+}|Ca{2+}|Cl{-}"))
        self.assertFalse(self.data.has("zeta", "Na{+}|Ca{2+}|Cl{-}"))
        self.assertTrue(self.data.has("zeta", "Na{+}|Ca{2+}|Cl{-}", require_value=False))

    def test_order_filtering_and_properties(self):
        self.assertEqual(self.data.interaction_orders, {2, 3})
        self.assertEqual(self.data.interaction_order("Na{+}|Cl{-}"), 2)
        self.assertEqual(self.data.get_mixture("Na{+}|Ca{2+}|Cl{-}", include_null=False), {"psi": 0})
        self.assertEqual(set(self.data.select(property_name="psi", contains=["Na{+}" ])), {
            ("Na{+}", "K{+}", "Cl{-}"), ("Na{+}", "Ca{2+}", "Cl{-}"), ("Na{+}", "Cl{-}"),
        })

    def test_validation_and_strict_lookup(self):
        with self.assertRaises(TableInteractionDataFormatError):
            self.data.interaction_order("Na{+}||Cl{-}")
        with self.assertRaises(TableInteractionDataLookupError):
            self.data.require("zeta", "Na{+}|Ca{2+}|Cl{-}")
        duplicate = {**TABLE_DATA, "VALUES": TABLE_DATA["VALUES"] + [[5, " Na{+} | K{+} | Cl{-} ", 1, 2]]}
        with self.assertRaises(TableInteractionDataDefinitionError):
            TableInteractionData("PITZER", "duplicate", duplicate)

    def test_component_lookup(self):
        components = [DummyComponent("sodium-ion", "Na{+}"), DummyComponent("potassium-ion", "K{+}"), DummyComponent("chloride-ion", "Cl{-}")]
        self.assertEqual(self.data.get_from_components("psi", components), -0.0018)
        self.assertEqual(self.data.get_from_components("psi", components, component_key="Formula"), -0.0018)


    def test_positional_symmetry_lookup_and_convenience_apis(self):
        self.assertIsNone(self.data.get("psi", "K{+}|Na{+}|Cl{-}"))
        self.assertEqual(
            self.data.get("psi", "K{+}|Na{+}|Cl{-}", symmetric_groups=[(0, 1)]),
            -0.0018,
        )
        self.assertIsNone(
            self.data.get("psi", "Cl{-}|Na{+}|K{+}", symmetric_groups=[(0, 1)])
        )
        self.assertEqual(
            self.data.i("psi", "K{+}|Na{+}|Cl{-}", symmetric_groups=[(0, 1)])["value"],
            -0.0018,
        )
        self.assertEqual(
            self.data.iis("psi", ["K{+}|Na{+}|Cl{-}"], symmetric_groups=[(0, 1)]),
            {("K{+}", "Na{+}", "Cl{-}"): -0.0018},
        )
        components = [
            DummyComponent("potassium-ion", "K{+}"),
            DummyComponent("sodium-ion", "Na{+}"),
            DummyComponent("chloride-ion", "Cl{-}"),
        ]
        self.assertEqual(
            self.data.get_from_components(
                "psi", components, component_key="Formula", symmetric_groups=[(0, 1)]
            ),
            -0.0018,
        )

    def test_symmetric_lookup_priority_permutations_and_validation(self):
        symmetry_data = {
            "INTERACTION-SYMBOL": ["psi"],
            "STRUCTURE": {
                "COLUMNS": ["Mixture", "psi"],
                "SYMBOL": [None, "psi"],
                "UNIT": [None, 1],
            },
            "VALUES": [
                ["A|B|C", None],
                ["B|A|C", 2.0],
                ["A|B|C|D", 3.0],
            ],
        }
        data = TableInteractionData("test", "symmetry", symmetry_data)
        self.assertIsNone(data.get("psi", "A|B|C", symmetric_groups=[(0, 1)]))
        self.assertEqual(data.get("psi", "B|A|C", symmetric_groups=[(0, 1)]), 2.0)
        self.assertEqual(
            data.get("psi", "B|A|D|C", symmetric_groups=[(0, 1), (2, 3)]),
            3.0,
        )
        all_symmetric = TableInteractionData(
            "test", "all-symmetric",
            {
                "INTERACTION-SYMBOL": ["phi3"],
                "STRUCTURE": {
                    "COLUMNS": ["Mixture", "phi3"],
                    "SYMBOL": [None, "phi3"],
                    "UNIT": [None, 1],
                },
                "VALUES": [["A|B|C", 4.0]],
            },
        )
        for mixture in permutations(("A", "B", "C")):
            self.assertEqual(
                all_symmetric.get("phi3", mixture, symmetric_groups=[(0, 1, 2)]),
                4.0,
            )
        with self.assertRaises(TableInteractionDataFormatError):
            data.get("psi", "A|B|C", symmetric_groups=[(0, 3)])
        with self.assertRaises(TableInteractionDataFormatError):
            data.get("psi", "A|B|C", symmetric_groups=[(-1, 0)])
        with self.assertRaises(TableInteractionDataFormatError):
            data.get("psi", "A|B|C", symmetric_groups=[(0, 0, 1)])
        with self.assertRaises(TableInteractionDataDefinitionError):
            data.get("psi", "A|B|C", symmetric_groups=[(0, 1), (1, 2)])


if __name__ == "__main__":
    unittest.main()
