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

    for key in ["TABLE-ID", "DESCRIPTION", "STRUCTURE", "VALUES"]:
        if key not in block:
            errors.append(f"{name}: missing required key {key}")

    structure = block.get("STRUCTURE", {})
    columns = structure.get("COLUMNS")
    symbols = structure.get("SYMBOL")
    units = structure.get("UNIT")

    if not isinstance(columns, list):
        errors.append(f"{name}: STRUCTURE.COLUMNS must be a list")

    needs_symbol_unit = not _is_constants_table(block)
    if needs_symbol_unit and not isinstance(symbols, list):
        errors.append(f"{name}: STRUCTURE.SYMBOL must be a list")
    if needs_symbol_unit and not isinstance(units, list):
        errors.append(f"{name}: STRUCTURE.UNIT must be a list")

    if isinstance(columns, list) and isinstance(symbols, list) and len(columns) != len(symbols):
        errors.append(f"{name}: SYMBOL length does not match COLUMNS length")
    if isinstance(columns, list) and isinstance(units, list) and len(columns) != len(units):
        errors.append(f"{name}: UNIT length does not match COLUMNS length")

    if _is_data_table(block):
        if not _has_conversion(block, structure):
            errors.append(f"{name}: data table must include CONVERSION in STRUCTURE or DATA")
        conversion = structure.get("CONVERSION")
        if isinstance(columns, list) and isinstance(conversion, list) and len(columns) != len(conversion):
            errors.append(f"{name}: CONVERSION length does not match COLUMNS length")
    elif _is_equation_table(block):
        if "CONVERSION" in structure:
            errors.append(f"{name}: equation table must not include CONVERSION")
        errors.extend(_validate_equations(name, block.get("EQUATIONS")))
    elif _is_constants_table(block):
        if not isinstance(columns, list):
            errors.append(f"{name}: constants table must include STRUCTURE.COLUMNS")
    elif _is_matrix_table(block):
        if not isinstance(block.get("MATRIX-SYMBOL"), list):
            errors.append(f"{name}: MATRIX-SYMBOL must be a list")
    else:
        errors.append(f"{name}: table must include DATA, EQUATIONS, CONSTANTS, or MATRIX-SYMBOL")

    values = block.get("VALUES", [])
    if isinstance(columns, list) and isinstance(values, list):
        for idx, row in enumerate(values, start=1):
            if not isinstance(row, list):
                errors.append(f"{name}: row {idx} in VALUES is not a list")
                continue
            if len(row) != len(columns):
                errors.append(
                    f"{name}: row {idx} length {len(row)} does not match COLUMNS length {len(columns)}"
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
