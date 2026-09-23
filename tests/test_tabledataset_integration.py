from pathlib import Path
import tempfile

import pandas as pd

import pyThermoDB as ptdb
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
          - ethanol: 1
        STRUCTURE:
          COLUMNS: [No., Id, Temperature, Pressure, Density]
          SYMBOL: [null, null, T, P, rho]
          UNIT: [null, null, K, Pa, kg/m^3]
          ROLE: [null, null, input, input, output]
        VALUES:
          - [1, water, 298.15, 101325, 997.05]
          - [2, water, 323.15, 101325, 988.05]
          - [1, ethanol, 298.15, 101325, 785.0]
      General:
        TABLE-ID: 2
        DESCRIPTION: Ordinary property data.
        STRUCTURE:
          COLUMNS: [No., Name, Value]
          SYMBOL: [null, null, v]
          UNIT: [null, null, K]
          CONVERSION: [null, null, 1]
          ROLE: [null, null, output]
        DATA:
          COLUMNS: [No., Name, Value]
          SYMBOL: [null, null, v]
          UNIT: [null, null, K]
          CONVERSION: [null, null, 1]
"""


def test_inline_dataset_detection_loading_building_and_exports():
    with tempfile.TemporaryDirectory() as directory:
        reference_path = Path(directory) / "datasets.yml"
        reference_path.write_text(INLINE_REFERENCE, encoding="utf-8")
        database = ptdb.init(
            custom_reference={"reference": [str(reference_path)]}
        )
        info = database.table_info("DATASETS", "Density", res_format="dict")
        dataset_record = database.select_table("DATASETS", "Density")
        general_record = database.select_table("DATASETS", "General")
        loaded = database.dataset_load("DATASETS", "Density")
        built = database.build_dataset("DATASETS", "Density")

    assert ptdb.TableDataset is TableDataset
    assert info["Type"] == "Dataset"
    assert info["Dataset"] == 1
    assert dataset_record["role"] == [None, None, "input", "input", "output"]
    assert general_record["role"] is None
    assert general_record["table_type"] == "data"
    assert isinstance(loaded, TableDataset)
    assert isinstance(built, TableDataset)
    assert loaded.shape == (3, 5)
    assert loaded.get_dataset_positions("water") == (1,)


def test_csv_backed_dataset_uses_metadata_rows_and_numeric_roles():
    reference = """
REFERENCES:
  DATASETS:
    DATABOOK-ID: 1
    TABLES:
      Density:
        TABLE-ID: 1
        DESCRIPTION: CSV density data.
        DATASET-IDS:
          - water: 1
        STRUCTURE:
          COLUMNS: [No., Id, Temperature, Pressure, Density]
          SYMBOL: [null, null, T, P, rho]
          UNIT: [null, null, K, Pa, kg/m^3]
          ROLE: [null, null, input, input, output]
"""
    csv = """No.,Id,Temperature,Pressure,Density
-,-,T,P,rho
-,-,K,Pa,kg/m^3
1,water,298.15,101325,997.05
2,water,323.15,101325,-
"""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        reference_path = root / "reference.yml"
        table_path = root / "Density.csv"
        reference_path.write_text(reference, encoding="utf-8")
        table_path.write_text(csv, encoding="utf-8")
        database = ptdb.init(
            custom_reference={
                "reference": [str(reference_path)],
                "tables": [str(table_path)],
            }
        )
        dataset = database.dataset_load("DATASETS", "Density")

    assert dataset.shape == (2, 5)
    assert dataset.get("T").tolist() == [298.15, 323.15]
    assert dataset.get("P").tolist() == [101325, 101325]
    assert pd.isna(dataset.get("rho").iloc[1])
