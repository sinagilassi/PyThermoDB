from pyThermoDB.builder import CompBuilder
from pyThermoDB.config.deps import AppConfig, set_config
from pyThermoDB.core import TableConstants, TableMatrixData, TableMatrixEquation


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


def test_all_constants_helpers_return_details_identifiers_and_labels():
    builder = CompBuilder()
    constants = _constants()

    assert builder.add_data('Physical Constants', constants)
    assert builder.build()

    const_id = 'reference::constants'

    assert builder.all_constants_details() == {
        const_id: {
            'columns': [
                'No.',
                'Name',
                'Symbol',
                'State',
                'Value',
                'Unit',
                'Description',
            ],
            'names': ['Universal Gas Constant'],
            'symbols': ['R'],
        }
    }
    assert builder.all_constants_identifiers() == [{const_id: ['R']}]
    assert builder.all_constants_id_labels() == [
        {'R': 'Universal Gas Constant'}
    ]


def test_matrix_helpers_return_explicit_matrix_metadata():
    builder = CompBuilder()
    matrix_data = TableMatrixData(
        databook_name='reference',
        table_name='matrix-data',
        table_data={
            'COLUMNS': ['No.', 'Name', 'Formula'],
            'MATRIX-SYMBOL': ['alpha'],
        },
    )
    matrix_equation = TableMatrixEquation(
        databook_name='reference',
        table_name='matrix-equation',
        equations=[],
    )
    matrix_equation.returns = {
        '1': {'name': 'Interaction Parameter', 'symbol': 'alpha', 'unit': 'K'}
    }
    matrix_equation.return_symbols = {
        'alpha': {'name': 'Interaction Parameter', 'unit': 'K'}
    }
    matrix_equation.args = {
        '1': {'name': 'Temperature', 'symbol': 'T', 'unit': 'K'}
    }
    matrix_equation.arg_symbols = {
        'T': {'name': 'Temperature', 'unit': 'K'}
    }
    matrix_equation.body = 'res = args["T"]'
    matrix_equation.body_integral = None
    matrix_equation.body_first_derivative = None
    matrix_equation.body_second_derivative = None
    matrix_equation.matrix_elements = ['water', 'ethanol']

    assert builder.add_data('matrix-data', matrix_data)
    assert builder.add_data('matrix-equation', matrix_equation)
    assert builder.build()

    matrix_data_id = 'reference::matrix-data'
    matrix_function_id = 'reference::matrix-equation'

    assert builder.all_matrix_data_details() == {
        matrix_data_id: {
            'matrix_symbol': ['alpha'],
            'matrix_mode': 'VALUES',
            'matrix_item_keys': None,
            'table_structure': {'COLUMNS': ['No.', 'Name', 'Formula']},
        }
    }
    assert builder.all_matrix_data_identifiers() == [
        {matrix_data_id: ['alpha']}
    ]
    assert builder.all_matrix_data_id_labels() == [
        {'alpha': 'non_randomness_parameter_alpha_i_j'}
    ]

    matrix_function_details = builder.all_matrix_function_details()
    assert matrix_function_details[matrix_function_id]['returns'] == {
        '1': {'name': 'Interaction Parameter', 'symbol': 'alpha', 'unit': 'K'}
    }
    assert matrix_function_details[matrix_function_id]['return_symbols'] == {
        'alpha': {'name': 'Interaction Parameter', 'unit': 'K'}
    }
    assert matrix_function_details[matrix_function_id]['args'] == {
        '1': {'name': 'Temperature', 'symbol': 'T', 'unit': 'K'}
    }
    assert matrix_function_details[matrix_function_id]['matrix_elements'] == [
        'water',
        'ethanol',
    ]
    assert builder.all_matrix_function_identifiers() == [
        {matrix_function_id: ['alpha']}
    ]


def test_build_details_includes_build_metadata_and_registered_counts():
    set_config(AppConfig(
        build_type='single',
        component_name='water',
        component_formula='H2O',
        component_state='l',
    ))
    try:
        builder = CompBuilder(thermodb_name='water-db', message='ready')
        constants = _constants()

        assert builder.add_data('Physical Constants', constants)
        assert builder.build()

        details = builder.build_details()

        assert details['thermodb_name'] == 'water-db'
        assert details['message'] == 'ready'
        assert details['build_type'] == 'single'
        assert details['component_name'] == 'water'
        assert details['component_formula'] == 'H2O'
        assert details['component_state'] == 'l'
        assert details['properties_count'] == 1
        assert details['functions_count'] == 0
        assert details['constants_count'] == 1
        assert details['data_count'] == 0
        assert details['matrix_data_count'] == 0
        assert details['equations_count'] == 0
        assert details['matrix_equations_count'] == 0
        assert 'build_version' in details
        assert 'build_date' in details
        assert 'build_timestamp' in details
        assert 'build_python' in details
    finally:
        set_config(AppConfig())
