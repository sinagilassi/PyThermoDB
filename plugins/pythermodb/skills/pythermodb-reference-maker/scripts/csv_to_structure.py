"""Convert a project-style CSV header into YAML structure arrays.

Assumes:
- row 1 = COLUMNS
- row 2 = SYMBOL
- row 3 = UNIT
- remaining rows = VALUES

Usage:
    python csv_to_structure.py path/to/file.csv
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python csv_to_structure.py path/to/file.csv")
        return 2

    path = Path(sys.argv[1])
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))

    if len(rows) < 3:
        print("CSV must contain at least 3 rows: COLUMNS, SYMBOL, UNIT")
        return 1

    columns = rows[0]
    symbols = rows[1]
    units = rows[2]
    values = rows[3:]

    print("COLUMNS:", json.dumps(columns, ensure_ascii=False))
    print("SYMBOL:", json.dumps(symbols, ensure_ascii=False))
    print("UNIT:", json.dumps(units, ensure_ascii=False))
    print("VALUES:")
    for row in values:
        print("-", json.dumps(row, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
