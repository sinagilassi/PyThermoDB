"""Basic validator for the thermo-table YAML schema.

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
    if not isinstance(symbols, list):
        errors.append(f"{name}: STRUCTURE.SYMBOL must be a list")
    if not isinstance(units, list):
        errors.append(f"{name}: STRUCTURE.UNIT must be a list")

    if isinstance(columns, list) and isinstance(symbols, list) and len(columns) != len(symbols):
        errors.append(f"{name}: SYMBOL length does not match COLUMNS length")
    if isinstance(columns, list) and isinstance(units, list) and len(columns) != len(units):
        errors.append(f"{name}: UNIT length does not match COLUMNS length")

    if _is_data_table(block):
        conversion = structure.get("CONVERSION")
        if not isinstance(conversion, list):
            errors.append(f"{name}: data table must include STRUCTURE.CONVERSION list")
        elif isinstance(columns, list) and len(columns) != len(conversion):
            errors.append(f"{name}: CONVERSION length does not match COLUMNS length")
    elif _is_equation_table(block):
        if "CONVERSION" in structure:
            errors.append(f"{name}: equation table must not include CONVERSION")
    else:
        errors.append(f"{name}: table must include either DATA or EQUATIONS")

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
    for table_name, table_block in data.items():
        if not isinstance(table_block, dict):
            errors.append(f"{table_name}: table block must be a mapping")
            continue
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
