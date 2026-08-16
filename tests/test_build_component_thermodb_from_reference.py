from pyThermoDB import (
    ComponentThermoDB,
    build_component_thermodb_from_reference,
)
from pyThermoDB.core import TableData


def test_build_component_thermodb_from_reference_accepts_data_table_marker():
    reference_content = """
REFERENCES:
  CUSTOM-REF-1:
    DATABOOK-ID: 1
    TABLES:
      General-Data:
        TABLE-ID: 1
        DESCRIPTION: General component data.
        DATA: []
        STRUCTURE:
          COLUMNS: [No., Name, Formula, State, Molecular-Weight]
          SYMBOL: [None, None, None, None, MW]
          UNIT: [None, None, None, None, g/mol]
          CONVERSION: [None, None, None, None, 1]
        VALUES:
          - [1, carbon dioxide, CO2, g, 44.01]
"""

    result = build_component_thermodb_from_reference(
        component_name="carbon dioxide",
        component_formula="CO2",
        component_state="g",
        reference_content=reference_content,
        component_key="Name-State",
        include_data=True,
        mode="silent",
    )

    assert isinstance(result, ComponentThermoDB)

    properties = result.thermodb.check_properties()
    assert set(properties) == {"CUSTOM-REF-1::General-Data"}

    general_data = properties["CUSTOM-REF-1::General-Data"]
    assert isinstance(general_data, TableData)
    assert general_data.table_columns == [
        "No.",
        "Name",
        "Formula",
        "State",
        "Molecular-Weight",
    ]
    assert general_data.table_values == [
        [1, "carbon dioxide", "CO2", "g", 44.01],
    ]
    assert general_data.get_property("Molecular-Weight")["value"] == "44.01"
