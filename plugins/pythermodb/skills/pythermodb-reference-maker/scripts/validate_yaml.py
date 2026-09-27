"""Basic validator for pyThermoDB reference/table YAML.

Usage:
    python validate_yaml.py path/to/file.yaml
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc


def _is_data_table(block: dict[str, Any]) -> bool:
    return "DATA" in block


def _is_equation_table(block: dict[str, Any]) -> bool:
    return "EQUATIONS" in block


def _is_constants_table(block: dict[str, Any]) -> bool:
    return "CONSTANTS" in block


def _is_interaction_table(block: dict[str, Any]) -> bool:
    return 'INTERACTION-SYMBOL' in block


def _is_dataset_table(block: dict[str, Any]) -> bool:
    return 'DATASET-IDS' in block


def _is_matrix_table(block: dict[str, Any]) -> bool:
    return "MATRIX-SYMBOL" in block


def _has_conversion(block: dict[str, Any], structure: dict[str, Any]) -> bool:
    data = block.get("DATA")
    return isinstance(structure.get("CONVERSION"), list) or (
        isinstance(data, dict) and isinstance(data.get("CONVERSION"), list)
    )


def _validate_equations(name: str, equations: Any) -> list[str]:
    errors: list[str] = []
    required_blocks = [
        "BODY",
        "BODY-INTEGRAL",
        "BODY-FIRST-DERIVATIVE",
        "BODY-SECOND-DERIVATIVE",
    ]

    if not isinstance(equations, dict):
        return [f"{name}: EQUATIONS must be a mapping"]

    for eq_name, eq_block in equations.items():
        if not isinstance(eq_block, dict):
            errors.append(f"{name}: {eq_name} must be a mapping")
            continue
        for key in required_blocks:
            if key not in eq_block:
                errors.append(f"{name}: {eq_name} missing {key}")
        body = eq_block.get("BODY")
        if body is not None and not isinstance(body, list):
            errors.append(f"{name}: {eq_name}.BODY must be a list or None")

    return errors


def _validate_interaction_table(
    name: str,
    block: dict[str, Any],
    structure: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    raw_symbols = block.get('INTERACTION-SYMBOL')
    if not isinstance(raw_symbols, list) or not raw_symbols:
        return [f'{name}: INTERACTION-SYMBOL must be a non-empty list']

    declared_symbols: list[str] = []
    for index, item in enumerate(raw_symbols, start=1):
        if isinstance(item, str):
            symbol = item
        elif isinstance(item, dict) and len(item) == 1:
            symbol = next(iter(item.values()))
        else:
            errors.append(
                f'{name}: INTERACTION-SYMBOL item {index} must be a string '
                'or one-key mapping'
            )
            continue

        if not isinstance(symbol, str) or not symbol.strip():
            errors.append(
                f'{name}: INTERACTION-SYMBOL item {index} must resolve to a '
                'non-empty string'
            )
            continue
        symbol = symbol.strip()
        if symbol in declared_symbols:
            errors.append(f'{name}: duplicate interaction symbol {symbol!r}')
            continue
        declared_symbols.append(symbol)

    columns = structure.get('COLUMNS')
    symbols = structure.get('SYMBOL')
    if not isinstance(columns, list) or not isinstance(symbols, list):
        return errors
    if 'Mixture' not in columns:
        errors.append(f'{name}: interaction table must include a Mixture column')
        return errors

    for property_name in declared_symbols:
        matching_columns = [
            columns[index]
            for index, symbol in enumerate(symbols)
            if index < len(columns) and symbol == property_name
        ]
        if property_name in columns:
            matching_columns.append(property_name)
        if len(list(dict.fromkeys(matching_columns))) != 1:
            errors.append(
                f'{name}: interaction symbol {property_name!r} must resolve '
                'to exactly one column'
            )

    values = block.get('VALUES')
    if not isinstance(values, list):
        return errors

    mixture_index = columns.index('Mixture')
    seen_mixtures: set[tuple[str, ...]] = set()
    for row_index, row in enumerate(values, start=1):
        if not isinstance(row, list) or mixture_index >= len(row):
            continue
        mixture = row[mixture_index]
        if not isinstance(mixture, str):
            errors.append(
                f'{name}: row {row_index} Mixture must be a pipe-delimited string'
            )
            continue
        normalized = tuple(part.strip() for part in mixture.split('|'))
        if len(normalized) < 2 or any(not part for part in normalized):
            errors.append(
                f'{name}: row {row_index} Mixture must contain at least two '
                'non-empty participants'
            )
            continue
        if normalized in seen_mixtures:
            errors.append(
                f'{name}: row {row_index} duplicates ordered mixture {mixture!r}'
            )
        seen_mixtures.add(normalized)

    return errors


def _validate_dataset_table(
    name: str,
    block: dict[str, Any],
    structure: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    dataset_ids = block.get('DATASET-IDS')
    declared_ids: set[str] = set()

    if not isinstance(dataset_ids, list):
        errors.append(f'{name}: DATASET-IDS must be a list of one-key mappings')
    else:
        for index, item in enumerate(dataset_ids, start=1):
            if not isinstance(item, dict) or len(item) != 1:
                errors.append(
                    f'{name}: DATASET-IDS item {index} must be a one-key mapping'
                )
                continue
            dataset_id, raw_positions = next(iter(item.items()))
            if not isinstance(dataset_id, str) or not dataset_id.strip():
                errors.append(
                    f'{name}: DATASET-IDS item {index} must use a non-empty string id'
                )
                continue
            if dataset_id in declared_ids:
                errors.append(f'{name}: duplicate dataset id {dataset_id!r}')
            declared_ids.add(dataset_id)

            if isinstance(raw_positions, bool):
                raw_values: list[Any] = []
            elif isinstance(raw_positions, int):
                raw_values = [raw_positions]
            elif isinstance(raw_positions, str):
                raw_values = [part.strip() for part in raw_positions.split('|')]
            else:
                raw_values = []
            try:
                positions = [
                    int(value) for value in raw_values if value != ''
                ]
            except (TypeError, ValueError):
                positions = []
            if (
                not positions
                or len(positions) != len(raw_values)
                or any(position <= 0 for position in positions)
            ):
                errors.append(
                    f'{name}: DATASET-IDS item {index} positions must be '
                    'pipe-delimited positive integers'
                )
            elif len(set(positions)) != len(positions):
                errors.append(
                    f'{name}: DATASET-IDS item {index} positions must be unique'
                )

    columns = structure.get('COLUMNS')
    symbols = structure.get('SYMBOL')
    units = structure.get('UNIT')
    roles = structure.get('ROLE')
    if not isinstance(roles, list):
        errors.append(f'{name}: STRUCTURE.ROLE must be a list')
    elif isinstance(columns, list) and len(roles) != len(columns):
        errors.append(f'{name}: ROLE length does not match COLUMNS length')
    else:
        invalid_roles = [
            role for role in roles if role not in ('input', 'output', None)
        ]
        if invalid_roles:
            errors.append(
                f'{name}: ROLE entries must be input, output, or None; '
                f'found {invalid_roles!r}'
            )

    if isinstance(columns, list):
        if not all(
            isinstance(column, str) and bool(column) for column in columns
        ):
            errors.append(
                f'{name}: dataset column names must be non-empty strings'
            )
        elif len(set(columns)) != len(columns):
            errors.append(f'{name}: dataset column names must be unique')
    if isinstance(symbols, list):
        non_null_symbols = [symbol for symbol in symbols if symbol is not None]
        if not all(
            isinstance(symbol, str) and bool(symbol)
            for symbol in non_null_symbols
        ):
            errors.append(f'{name}: non-null dataset symbols must be strings')
        elif len(set(non_null_symbols)) != len(non_null_symbols):
            errors.append(f'{name}: non-null dataset symbols must be unique')
    if isinstance(units, list) and not all(
        unit is None or isinstance(unit, str) for unit in units
    ):
        errors.append(f'{name}: dataset units must be strings or None')

    values = block.get('VALUES')
    if (
        isinstance(columns, list)
        and 'Id' in columns
        and isinstance(values, list)
        and isinstance(dataset_ids, list)
    ):
        id_index = columns.index('Id')
        for row_index, row in enumerate(values, start=1):
            if not isinstance(row, list) or id_index >= len(row):
                continue
            dataset_id = row[id_index]
            if (
                not isinstance(dataset_id, str)
                or dataset_id in {None, '-', 'None'}
                or dataset_id not in declared_ids
            ):
                errors.append(
                    f'{name}: row {row_index} contains unknown dataset id '
                    f'{dataset_id!r}'
                )

    return errors


def _iter_tables(data: dict[str, Any]) -> tuple[list[tuple[str, dict[str, Any]]], list[str]]:
    """Return table blocks from either a full REFERENCES file or direct table YAML."""
    errors: list[str] = []

    if "REFERENCES" not in data:
        tables = []
        for table_name, table_block in data.items():
            if not isinstance(table_block, dict):
                errors.append(f"{table_name}: table block must be a mapping")
                continue
            tables.append((table_name, table_block))
        return tables, errors

    references = data.get("REFERENCES")
    if not isinstance(references, dict):
        return [], ["REFERENCES must be a mapping"]

    tables = []
    for databook_name, databook_block in references.items():
        if not isinstance(databook_block, dict):
            errors.append(f"REFERENCES.{databook_name}: databook block must be a mapping")
            continue
        if "DATABOOK-ID" not in databook_block:
            errors.append(f"REFERENCES.{databook_name}: missing DATABOOK-ID")
        table_map = databook_block.get("TABLES")
        if not isinstance(table_map, dict):
            errors.append(f"REFERENCES.{databook_name}: TABLES must be a mapping")
            continue
        for table_name, table_block in table_map.items():
            if not isinstance(table_block, dict):
                errors.append(f"{databook_name}::{table_name}: table block must be a mapping")
                continue
            tables.append((f"{databook_name}::{table_name}", table_block))

    return tables, errors


def validate_table(name: str, block: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for key in ['TABLE-ID', 'DESCRIPTION', 'STRUCTURE', 'VALUES']:
        if key not in block:
            errors.append(f'{name}: missing required key {key}')

    structure = block.get('STRUCTURE', {})
    if not isinstance(structure, dict):
        errors.append(f'{name}: STRUCTURE must be a mapping')
        structure = {}
    columns = structure.get('COLUMNS')
    symbols = structure.get('SYMBOL')
    units = structure.get('UNIT')

    if not isinstance(columns, list):
        errors.append(f'{name}: STRUCTURE.COLUMNS must be a list')

    needs_symbol_unit = not _is_constants_table(block)
    if needs_symbol_unit and not isinstance(symbols, list):
        errors.append(f'{name}: STRUCTURE.SYMBOL must be a list')
    if needs_symbol_unit and not isinstance(units, list):
        errors.append(f'{name}: STRUCTURE.UNIT must be a list')

    if (
        isinstance(columns, list)
        and isinstance(symbols, list)
        and len(columns) != len(symbols)
    ):
        errors.append(f'{name}: SYMBOL length does not match COLUMNS length')
    if (
        isinstance(columns, list)
        and isinstance(units, list)
        and len(columns) != len(units)
    ):
        errors.append(f'{name}: UNIT length does not match COLUMNS length')

    markers = [
        marker
        for marker in [
            'DATA',
            'EQUATIONS',
            'CONSTANTS',
            'MATRIX-SYMBOL',
            'INTERACTION-SYMBOL',
            'DATASET-IDS',
        ]
        if marker in block
    ]
    if len(markers) > 1:
        errors.append(f'{name}: table mixes type markers {markers!r}')

    if _is_interaction_table(block):
        if 'CONVERSION' in structure:
            errors.append(f'{name}: interaction table must not include CONVERSION')
        errors.extend(_validate_interaction_table(name, block, structure))
    elif _is_dataset_table(block):
        if 'CONVERSION' in structure:
            errors.append(f'{name}: dataset table must not include CONVERSION')
        errors.extend(_validate_dataset_table(name, block, structure))
    elif _is_data_table(block):
        if not _has_conversion(block, structure):
            errors.append(
                f'{name}: data table must include CONVERSION in STRUCTURE or DATA'
            )
        conversion = structure.get('CONVERSION')
        if (
            isinstance(columns, list)
            and isinstance(conversion, list)
            and len(columns) != len(conversion)
        ):
            errors.append(
                f'{name}: CONVERSION length does not match COLUMNS length'
            )
    elif _is_equation_table(block):
        if 'CONVERSION' in structure:
            errors.append(f'{name}: equation table must not include CONVERSION')
        errors.extend(_validate_equations(name, block.get('EQUATIONS')))
    elif _is_constants_table(block):
        if not isinstance(columns, list):
            errors.append(
                f'{name}: constants table must include STRUCTURE.COLUMNS'
            )
    elif _is_matrix_table(block):
        if not isinstance(block.get('MATRIX-SYMBOL'), list):
            errors.append(f'{name}: MATRIX-SYMBOL must be a list')
    else:
        errors.append(
            f'{name}: table must include DATA, EQUATIONS, CONSTANTS, '
            'MATRIX-SYMBOL, INTERACTION-SYMBOL, or DATASET-IDS'
        )

    values = block.get('VALUES', [])
    if not isinstance(values, list):
        errors.append(f'{name}: VALUES must be a list')
    elif isinstance(columns, list):
        for index, row in enumerate(values, start=1):
            if not isinstance(row, list):
                errors.append(f'{name}: row {index} in VALUES is not a list')
            elif len(row) != len(columns):
                errors.append(
                    f'{name}: row {index} length {len(row)} does not match '
                    f'COLUMNS length {len(columns)}'
                )

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python validate_yaml.py path/to/file.yaml")
        return 2

    path = Path(sys.argv[1])
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print("Top-level YAML must be a mapping")
        return 1

    errors: list[str] = []
    tables, table_errors = _iter_tables(data)
    errors.extend(table_errors)
    for table_name, table_block in tables:
        errors.extend(validate_table(table_name, table_block))

    if errors:
        print("Validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
