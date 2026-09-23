from copy import deepcopy

import numpy as np
import pandas as pd
import pytest

from pyThermoDB.core import TableDataset
from pyThermoDB.handlers import (
    TableDatasetDefinitionError,
    TableDatasetFormatError,
    TableDatasetFrameError,
    TableDatasetLookupError,
    TableDatasetStructureError,
)


@pytest.fixture
def dataset_source():
    return {
        "TABLE-ID": 1,
        "DESCRIPTION": "VLE observations",
        "DATASET-IDS": [
            {"methanol|water": "1|2"},
            {"ethanol|benzene": "1|2"},
            {"ethanol|methanol|water": "1|2|3"},
        ],
        "STRUCTURE": {
            "COLUMNS": [
                "No.", "Id", "Temperature", "Pressure",
                "Liquid-Mole-Fraction-1", "Liquid-Mole-Fraction-2",
                "Vapor-Mole-Fraction-1", "Vapor-Mole-Fraction-2",
            ],
            "SYMBOL": [None, None, "T", "P", "x_1", "x_2", "y_1", "y_2"],
            "UNIT": [None, None, "K", "Pa", None, None, None, None],
            "ROLE": [None, None, "input", "input", "input", "input", "output", "output"],
        },
        "VALUES": [
            [1, "methanol|water", 298.15, 101325, 0.5, None, 0.5, None],
            [2, "methanol|water", 308.15, 101325, 0.4, "-", 0.6, "None"],
            [1, "ethanol|benzene", 298.15, 101325, 0.5, None, 0.5, None],
            [2, "ethanol|benzene", 308.15, 101325, 0.4, None, 0.6, None],
            [1, "ethanol|methanol|water", 298.15, 101325, 0.30, 0.20, 0.40, 0.25],
            [2, "ethanol|methanol|water", 308.15, 101325, 0.0, 0.30, 0.35, 0.40],
        ],
    }


def test_construction_metadata_roles_and_defensive_copies(dataset_source):
    dataset = TableDataset("BOOK", "VLE", dataset_source)
    assert dataset.shape == (6, 8)
    assert dataset.columns == dataset_source["STRUCTURE"]["COLUMNS"]
    assert dataset.symbols[2:4] == ["T", "P"]
    assert dataset.units[2:4] == ["K", "Pa"]
    assert dataset.roles[2:4] == ["input", "input"]
    assert dataset.input_columns == [
        "Temperature", "Pressure", "Liquid-Mole-Fraction-1",
        "Liquid-Mole-Fraction-2",
    ]
    assert dataset.output_columns == [
        "Vapor-Mole-Fraction-1", "Vapor-Mole-Fraction-2",
    ]
    assert dataset.inputs.shape == (6, 4)
    assert dataset.outputs.shape == (6, 2)
    assert dataset.dataset_ids["methanol|water"] == (1, 2)

    frame = dataset.dataframe
    frame.loc[0, "Temperature"] = -1
    columns = dataset.columns
    columns.append("bad")
    assert dataset.get("T").iloc[0] == 298.15
    assert "bad" not in dataset.columns


def test_lookup_group_filter_numpy_and_missing_values(dataset_source):
    dataset = TableDataset("BOOK", "VLE", dataset_source)
    pd.testing.assert_series_equal(
        dataset.get("Temperature"), dataset.get("T")
    )
    assert len(dataset.get_dataset("methanol|water")) == 2
    assert dataset.get_dataset_positions("ethanol|methanol|water") == (1, 2, 3)
    assert len(dataset.filter(Id="methanol|water", T=298.15)) == 1
    assert len(dataset.filter(x_2=None)) == 4
    selected = dataset.to_numpy(["T", "P", "x_1"])
    assert selected.shape == (6, 3)
    assert selected[5, 2] == 0
    assert pd.isna(dataset.get("x_2").iloc[0])
    assert dataset.to_numpy().dtype == np.dtype("O")


def test_lookup_failures(dataset_source):
    dataset = TableDataset("BOOK", "VLE", dataset_source)
    with pytest.raises(TableDatasetLookupError):
        dataset.get("temperature")
    with pytest.raises(TableDatasetLookupError):
        dataset.get_dataset("unknown")
    with pytest.raises(TableDatasetLookupError):
        dataset.get_dataset_positions("unknown")

    without_id = deepcopy(dataset_source)
    for key in ("COLUMNS", "SYMBOL", "UNIT", "ROLE"):
        del without_id["STRUCTURE"][key][1]
    without_id["VALUES"] = [row[:1] + row[2:] for row in without_id["VALUES"]]
    with pytest.raises(TableDatasetLookupError):
        TableDataset("BOOK", "NO-ID", without_id).get_dataset("methanol|water")


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        (lambda source: source.update({"STRUCTURE": None}), TableDatasetStructureError),
        (lambda source: source["STRUCTURE"]["COLUMNS"].append("Temperature"), TableDatasetDefinitionError),
        (lambda source: source["STRUCTURE"]["SYMBOL"].append("T"), TableDatasetStructureError),
        (lambda source: source["STRUCTURE"]["SYMBOL"].__setitem__(3, "T"), TableDatasetDefinitionError),
        (lambda source: source["STRUCTURE"]["ROLE"].__setitem__(2, "feature"), TableDatasetDefinitionError),
        (lambda source: source["VALUES"][0].pop(), TableDatasetStructureError),
        (lambda source: source.update({"DATASET-IDS": "bad"}), TableDatasetFormatError),
        (lambda source: source.update({"DATASET-IDS": [{"a": "1|1"}]}), TableDatasetDefinitionError),
        (lambda source: source.update({"DATASET-IDS": [{"a": "1|x"}]}), TableDatasetFormatError),
        (lambda source: source["VALUES"][0].__setitem__(1, "unknown"), TableDatasetDefinitionError),
    ],
)
def test_invalid_definitions(dataset_source, mutation, error):
    source = deepcopy(dataset_source)
    mutation(source)
    with pytest.raises(error):
        TableDataset("BOOK", "INVALID", source)


def test_dataframe_override_and_column_validation(dataset_source):
    source = deepcopy(dataset_source)
    frame = pd.DataFrame(source.pop("VALUES"), columns=source["STRUCTURE"]["COLUMNS"])
    dataset = TableDataset("BOOK", "FRAME", source, dataset_table=frame)
    assert dataset.shape == (6, 8)
    with pytest.raises(TableDatasetFrameError):
        TableDataset("BOOK", "FRAME", source, dataset_table=frame.drop(columns="Pressure"))
