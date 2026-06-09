# import libs
import os
from rich import print
from pyThermoDB import (
    build_constants_thermodb_from_reference,
    ConstantsThermoDB
)
from pyThermoDB.core import TableConstants
# ! reference
from examples.configs.reference_2 import REFERENCE_CONTENT

# NOTE: current file path
parent_path = os.path.dirname(os.path.abspath(__file__))
print(parent_path)


# SECTION: reference content
# Use the reference content defined in the reference_2.py file.
# NOTE: normal build, all constants tables
thermodb_constants_: ConstantsThermoDB | None = build_constants_thermodb_from_reference(
    reference_content=REFERENCE_CONTENT,
)
print(f"thermodb_constants_: {type(thermodb_constants_)}")

# SECTION: reference content
# Use the external reference YAML that contains Custom-Constants and
# Custom-Constants-2 tables.
external_ref_path = os.path.join(
    os.path.dirname(parent_path),
    'external-ref',
    'source-ref-1.yml'
)
print(external_ref_path)

# SECTION: build constants thermodb
# NOTE: normal build, all constants tables
thermodb_constants_: ConstantsThermoDB | None = build_constants_thermodb_from_reference(
    reference_content=external_ref_path,
)
print(f"thermodb_constants_: {type(thermodb_constants_)}")

# >> thermodb
if thermodb_constants_ is not None:
    # check
    print(f"thermodb constants checks: {thermodb_constants_.thermodb.check()}")

    # constants sources
    constants_sources = thermodb_constants_.thermodb.check_constants()
    print(f"constants sources: {list(constants_sources.keys())}")

    # select constants table
    custom_constants: TableConstants = thermodb_constants_.thermodb.select_constant(
        'Custom-Constants'
    )
    print(custom_constants.table_columns)
    print(custom_constants.table_values)

    # retrieve constants by symbol/name
    print(custom_constants.get_constant('R', message='gas constant'))
    print(custom_constants.get_constant(
        'dH_rxn',
        message='enthalpy of reaction'
    ))
    print(custom_constants.get_constant('X', message='custom list constant'))

# NOTE: build and save
thermodb_constants_save_: ConstantsThermoDB | None = build_constants_thermodb_from_reference(
    reference_content=external_ref_path,
    thermodb_save=True,
    thermodb_save_path=parent_path,
    thermodb_name='custom constants from reference',
)
print(f"thermodb_constants_save_: {type(thermodb_constants_save_)}")

# >> thermodb
if thermodb_constants_save_ is not None:
    # check
    print(
        f"thermodb_constants_save_ checks: {thermodb_constants_save_.thermodb.check()}")

# SECTION: build constants thermodb from a specific table
# NOTE: table-specific build
thermodb_constants_table_: ConstantsThermoDB | None = build_constants_thermodb_from_reference(
    reference_content=external_ref_path,
    databook_name='CUSTOM-REF-1',
    table_name='Custom-Constants',
)
print(f"thermodb_constants_table_: {type(thermodb_constants_table_)}")

# >> thermodb
if thermodb_constants_table_ is not None:
    # check
    print(
        f"thermodb_constants_table_ checks: {thermodb_constants_table_.thermodb.check()}")

    custom_constants = thermodb_constants_table_.thermodb.select_constant(
        'Custom-Constants'
    )
    print(custom_constants.get_constant(
        'Universal Gas Constant',
        message='gas constant by name'
    ))

# SECTION: build constants thermodb by constant symbol
# NOTE: this should select only Custom-Constants-2 because dG_rxn is in that table.
thermodb_constants_symbol_: ConstantsThermoDB | None = build_constants_thermodb_from_reference(
    reference_content=external_ref_path,
    constants='dG_rxn',
)
print(f"thermodb_constants_symbol_: {type(thermodb_constants_symbol_)}")

# >> thermodb
if thermodb_constants_symbol_ is not None:
    # check
    print(
        f"thermodb_constants_symbol_ checks: {thermodb_constants_symbol_.thermodb.check()}")

    custom_constants_2 = thermodb_constants_symbol_.thermodb.select_constant(
        'Custom-Constants-2'
    )
    print(custom_constants_2.get_constant(
        'dG_rxn',
        message='Gibbs free energy of reaction'
    ))

# SECTION: build constants thermodb by several constants
# NOTE: matching tables are included when at least one requested constant is found.
constants = ['R', 'dH_rxn', 'dG_rxn']
thermodb_constants_multi_: ConstantsThermoDB | None = build_constants_thermodb_from_reference(
    reference_content=external_ref_path,
    constants=constants,
    verbose=True,
)
print(f"thermodb_constants_multi_: {type(thermodb_constants_multi_)}")

# >> thermodb
if thermodb_constants_multi_ is not None:
    # check
    print(
        f"thermodb_constants_multi_ checks: {thermodb_constants_multi_.thermodb.check()}")

    # reference metadata
    print(
        f"reference rules: {thermodb_constants_multi_.reference_thermodb.rules if thermodb_constants_multi_.reference_thermodb else None}")
