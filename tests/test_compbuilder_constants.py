from pyThermoDB.builder import CompBuilder
from pyThermoDB.core import TableConstants


def _constants() -> TableConstants:
    return TableConstants(
        databook_name='reference',
        table_name='constants',
        table_data={
            'COLUMNS': [
                'No.',
                'Name',
                'Symbol',
                'State',
                'Value',
                'Unit',
                'Description',
            ]
        },
        table_values=[
            [1, 'Universal Gas Constant', 'R', 'g', 8.314, 'J/mol.K', ''],
        ],
    )


def test_constants_specific_accessors_only_return_constants_sources():
    builder = CompBuilder()
    constants = _constants()

    assert builder.add_data('Physical Constants', constants)
    assert builder.add_data('plain-property', {})
    assert builder.build()

    assert builder.check_constants() == {'Physical Constants': constants}
    assert builder.is_constant_available('Physical Constants')
    assert not builder.is_constant_available('plain-property')
    assert builder.check_constant('Physical Constants') is constants


def test_select_constant_matches_source_name_case_insensitively():
    builder = CompBuilder()
    constants = _constants()

    assert builder.add_data('Physical Constants', constants)
    assert builder.build()

    assert builder.select_constant('  physical constants ') is constants
