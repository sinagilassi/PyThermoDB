from pathlib import Path

import pyThermoDB as ptdb
from pyThermoDB import DatasetThermoDB
from pyThermoDB.core import TableDataset


INLINE_REFERENCE = """
REFERENCES:
  DATASETS:
    DATABOOK-ID: 1
    TABLES:
      Density:
        TABLE-ID: 1
        DESCRIPTION: Experimental density data.
        DATASET-IDS:
          - water: 1
        STRUCTURE:
          COLUMNS: [No., Id, Temperature, Density]
          SYMBOL: [null, null, T, rho]
          UNIT: [null, null, K, kg/m^3]
          ROLE: [null, null, input, output]
        VALUES:
          - [1, water, 298.15, 997.05]
      Ordinary:
        TABLE-ID: 2
        DESCRIPTION: An ordinary data table.
        STRUCTURE:
          COLUMNS: [No., Name, Value]
          SYMBOL: [null, null, v]
          UNIT: [null, null, K]
          CONVERSION: [null, null, 1]
        DATA:
          COLUMNS: [No., Name, Value]
          SYMBOL: [null, null, v]
          UNIT: [null, null, K]
          CONVERSION: [null, null, 1]
        VALUES:
          - [1, sample, 1]
"""


def test_build_dataset_thermodb_from_explicit_config():
    result = ptdb.build_dataset_thermodb(
        reference_config={
            "density": {"databook": "DATASETS", "table": "Density"}
        },
        custom_reference={"reference": [INLINE_REFERENCE]},
    )

    assert result is not None
    assert result.build_type == "dataset"
    assert isinstance(result.list_data()["density"], TableDataset)
    assert result.build_details()["dataset_count"] == 1


def test_build_dataset_thermodb_from_reference_discovers_only_datasets():
    result = ptdb.build_dataset_thermodb_from_reference(INLINE_REFERENCE)

    assert isinstance(result, DatasetThermoDB)
    assert list(result.thermodb.list_data()) == ["DATASETS::Density"]
    assert isinstance(
        result.thermodb.list_data()["DATASETS::Density"],
        TableDataset,
    )


def test_build_dataset_thermodb_from_csv_reference():
    root = Path(__file__).resolve().parents[1] / "examples" / "datasets"
    reference_path = root / "table-dataset-source.yaml"
    table_paths = sorted(str(path) for path in root.glob("*.csv"))

    result = ptdb.build_dataset_thermodb_from_reference(
        str(reference_path),
        table_name="VLE-DATASET",
        custom_reference={"reference": [], "tables": table_paths},
    )

    assert isinstance(result, DatasetThermoDB)
    dataset = result.thermodb.list_data()["DATASET-EXAMPLE::VLE-DATASET"]
    assert dataset.shape == (6, 8)
    assert dataset.get_dataset_positions("methanol|water") == (1, 2)
