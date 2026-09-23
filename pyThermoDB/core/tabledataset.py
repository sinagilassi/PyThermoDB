"""Validated, domain-neutral observational dataset tables."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any, Optional

import numpy as np
import pandas as pd

from ..handlers import (
    TableDatasetConversionError,
    TableDatasetDefinitionError,
    TableDatasetFormatError,
    TableDatasetFrameError,
    TableDatasetLookupError,
    TableDatasetStructureError,
)


class TableDataset:
    """Store and query a structured observational dataset."""

    # NOTE: Keep allowed roles immutable across instances.
    _allowed_roles = frozenset({"input", "output", None})

    def __init__(
        self,
        databook_name: str | int,
        table_name: str | int,
        table_data: dict[str, Any],
        dataset_table: Optional[pd.DataFrame] = None,
    ) -> None:
        self.databook_name = databook_name
        self.table_name = table_name

        # SECTION: source validation and instance-owned state
        if not isinstance(table_data, Mapping):
            raise TableDatasetStructureError(
                "table_data must be a mapping.", context=self._context()
            )

        self.table_data = deepcopy(dict(table_data))
        self.dataset_table: pd.DataFrame
        self._table_structure: dict[str, Any] = {}
        self._table_columns: list[str] = []
        self._table_symbols: list[str | None] = []
        self._table_units: list[str | None] = []
        self._table_roles: list[str | None] = []
        self._symbol_to_column: dict[str, str] = {}
        self._dataset_ids: dict[str, tuple[int, ...]] | None = None

        self._validate_structure()
        self._dataset_ids = self._normalize_dataset_ids(
            self.table_data.get("DATASET-IDS")
        )
        self._symbol_to_column = {
            symbol: column
            for column, symbol in zip(self._table_columns, self._table_symbols)
            if symbol is not None
        }
        self.dataset_table = self._build_dataframe(dataset_table)
        self._validate_dataset_references()

    # SECTION: validation and normalization helpers
    def _context(self, **context: Any) -> dict[str, Any]:
        result = {
            "databook_name": self.databook_name,
            "table_name": self.table_name,
        }
        result.update(context)
        return result

    @staticmethod
    def _is_missing(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str):
            return value in {"-", "None"}
        if isinstance(value, float):
            return math.isnan(value)
        try:
            missing = pd.isna(value)
        except (TypeError, ValueError):
            return False
        return isinstance(missing, (bool, np.bool_)) and bool(missing)

    @classmethod
    def _normalize_missing_value(cls, value: Any) -> Any:
        return None if cls._is_missing(value) else value

    def _validate_structure(self) -> None:
        structure = self.table_data.get("STRUCTURE")
        if not isinstance(structure, Mapping):
            raise TableDatasetStructureError(
                "STRUCTURE must be a dictionary.", context=self._context()
            )

        for name in ("COLUMNS", "SYMBOL", "UNIT", "ROLE"):
            if not isinstance(structure.get(name), list):
                raise TableDatasetStructureError(
                    f"STRUCTURE.{name} must be a list.",
                    context=self._context(field=name),
                )

        columns = list(structure["COLUMNS"])
        symbols = list(structure["SYMBOL"])
        units = list(structure["UNIT"])
        roles = list(structure["ROLE"])
        if not columns:
            raise TableDatasetStructureError(
                "STRUCTURE.COLUMNS must not be empty.", context=self._context()
            )
        if not all(isinstance(column, str) and column for column in columns):
            raise TableDatasetDefinitionError(
                "Column names must be non-empty strings.", context=self._context()
            )
        if len(set(columns)) != len(columns):
            raise TableDatasetDefinitionError(
                "Column names must be unique.", context=self._context()
            )
        if not all(len(values) == len(columns) for values in (symbols, units, roles)):
            raise TableDatasetStructureError(
                "COLUMNS, SYMBOL, UNIT, and ROLE lengths must match.",
                context=self._context(),
            )

        non_null_symbols = [symbol for symbol in symbols if symbol is not None]
        if not all(isinstance(symbol, str) and symbol for symbol in non_null_symbols):
            raise TableDatasetDefinitionError(
                "Non-null symbols must be non-empty strings.",
                context=self._context(),
            )
        if len(set(non_null_symbols)) != len(non_null_symbols):
            raise TableDatasetDefinitionError(
                "Non-null symbols must be unique.", context=self._context()
            )
        if not all(unit is None or isinstance(unit, str) for unit in units):
            raise TableDatasetDefinitionError(
                "Units must be strings or None.", context=self._context()
            )
        invalid_roles = [role for role in roles if role not in self._allowed_roles]
        if invalid_roles:
            raise TableDatasetDefinitionError(
                "Roles must be 'input', 'output', or None.",
                context=self._context(roles=invalid_roles),
            )

        self._table_structure = deepcopy(dict(structure))
        self._table_columns = columns
        self._table_symbols = symbols
        self._table_units = units
        self._table_roles = roles

    def _normalize_dataset_ids(
        self, source: Any
    ) -> dict[str, tuple[int, ...]] | None:
        # NOTE: DATASET-IDS remains optional at the runtime class level.
        if source is None:
            return None
        if not isinstance(source, list):
            raise TableDatasetFormatError(
                "DATASET-IDS must be a list of one-key mappings.",
                context=self._context(),
            )

        normalized: dict[str, tuple[int, ...]] = {}
        for item in source:
            if not isinstance(item, Mapping) or len(item) != 1:
                raise TableDatasetFormatError(
                    "Each DATASET-IDS entry must be a one-key mapping.",
                    context=self._context(entry=item),
                )
            dataset_id, raw_positions = next(iter(item.items()))
            if not isinstance(dataset_id, str) or not dataset_id.strip():
                raise TableDatasetFormatError(
                    "Dataset identifiers must be non-empty strings.",
                    context=self._context(dataset_id=dataset_id),
                )
            if dataset_id in normalized:
                raise TableDatasetDefinitionError(
                    "Dataset identifiers must be unique.",
                    context=self._context(dataset_id=dataset_id),
                )

            if isinstance(raw_positions, bool):
                raw_values: list[Any] = []
            elif isinstance(raw_positions, int):
                raw_values = [raw_positions]
            elif isinstance(raw_positions, str):
                raw_values = [part.strip() for part in raw_positions.split("|")]
            else:
                raw_values = []
            try:
                positions = tuple(int(value) for value in raw_values if value != "")
            except (TypeError, ValueError) as exc:
                raise TableDatasetFormatError(
                    "Dataset positions must be pipe-separated positive integers.",
                    context=self._context(dataset_id=dataset_id),
                ) from exc
            if (
                not positions
                or len(positions) != len(raw_values)
                or any(position <= 0 for position in positions)
            ):
                raise TableDatasetFormatError(
                    "Dataset positions must be pipe-separated positive integers.",
                    context=self._context(dataset_id=dataset_id),
                )
            if len(set(positions)) != len(positions):
                raise TableDatasetDefinitionError(
                    "Dataset positions must be unique.",
                    context=self._context(dataset_id=dataset_id),
                )
            normalized[dataset_id] = positions
        return normalized

    # SECTION: DataFrame construction and dataset-reference validation
    def _build_dataframe(
        self, dataset_table: Optional[pd.DataFrame]
    ) -> pd.DataFrame:
        if dataset_table is not None:
            # ! A supplied frame must follow the declared schema exactly.
            if not isinstance(dataset_table, pd.DataFrame):
                raise TableDatasetFrameError(
                    "dataset_table must be a pandas DataFrame.",
                    context=self._context(),
                )
            if list(dataset_table.columns) != self._table_columns:
                raise TableDatasetFrameError(
                    "dataset_table columns must match STRUCTURE.COLUMNS.",
                    context=self._context(columns=list(dataset_table.columns)),
                )
            frame = dataset_table.copy(deep=True)
        else:
            # NOTE: Inline VALUES retain their native Python scalar types.
            values = self.table_data.get("VALUES")
            if not isinstance(values, list):
                raise TableDatasetStructureError(
                    "VALUES must be a list when dataset_table is not supplied.",
                    context=self._context(),
                )
            normalized_rows: list[list[Any]] = []
            for row_index, row in enumerate(values):
                if (
                    not isinstance(row, Sequence)
                    or isinstance(row, (str, bytes, bytearray))
                    or len(row) != len(self._table_columns)
                ):
                    raise TableDatasetStructureError(
                        "Every VALUES row must align with COLUMNS.",
                        context=self._context(row=row_index),
                    )
                normalized_rows.append(
                    [self._normalize_missing_value(value) for value in row]
                )
            frame = pd.DataFrame(normalized_rows, columns=self._table_columns)
        return frame.apply(
            lambda column: column.map(self._normalize_missing_value)
        )

    def _validate_dataset_references(self) -> None:
        # ? Without DATASET-IDS, Id values remain valid opaque identifiers.
        if self._dataset_ids is None or "Id" not in self._table_columns:
            return
        for row_index, dataset_id in enumerate(self.dataset_table["Id"].tolist()):
            if self._is_missing(dataset_id) or dataset_id not in self._dataset_ids:
                raise TableDatasetDefinitionError(
                    "VALUES contains an unknown dataset identifier.",
                    context=self._context(row=row_index, dataset_id=dataset_id),
                )

    def _resolve_column(self, column: str) -> str:
        if not isinstance(column, str):
            raise TableDatasetFormatError(
                "Column lookup must be a string.",
                context=self._context(column=column),
            )
        if column in self._table_columns:
            return column
        if column in self._symbol_to_column:
            return self._symbol_to_column[column]
        raise TableDatasetLookupError(
            "Dataset column or symbol was not found.",
            context=self._context(column=column),
        )

    # SECTION: public structural metadata
    @property
    def table_columns(self) -> list[str]:
        return self._table_columns.copy()

    @property
    def table_symbols(self) -> list[str | None]:
        return self._table_symbols.copy()

    @property
    def table_units(self) -> list[str | None]:
        return self._table_units.copy()

    @property
    def table_roles(self) -> list[str | None]:
        return self._table_roles.copy()

    @property
    def columns(self) -> list[str]:
        return self.table_columns

    @property
    def symbols(self) -> list[str | None]:
        return self.table_symbols

    @property
    def units(self) -> list[str | None]:
        return self.table_units

    @property
    def roles(self) -> list[str | None]:
        return self.table_roles

    @property
    def dataset_ids(self) -> dict[str, tuple[int, ...]] | None:
        return None if self._dataset_ids is None else dict(self._dataset_ids)

    @property
    def dataframe(self) -> pd.DataFrame:
        return self.dataset_table.copy(deep=True)

    @property
    def shape(self) -> tuple[int, int]:
        return self.dataset_table.shape

    # SECTION: role-based views
    @property
    def input_columns(self) -> list[str]:
        return [
            column
            for column, role in zip(self._table_columns, self._table_roles)
            if role == "input"
        ]

    @property
    def output_columns(self) -> list[str]:
        return [
            column
            for column, role in zip(self._table_columns, self._table_roles)
            if role == "output"
        ]

    @property
    def inputs(self) -> pd.DataFrame:
        return self.dataset_table.loc[:, self.input_columns].copy()

    @property
    def outputs(self) -> pd.DataFrame:
        return self.dataset_table.loc[:, self.output_columns].copy()

    # SECTION: lookup, filtering, and conversion APIs
    def get(self, column: str) -> pd.Series:
        """Return a copy of a column resolved by exact name or symbol."""
        return self.dataset_table.loc[:, self._resolve_column(column)].copy()

    def get_dataset(self, dataset_id: str) -> pd.DataFrame:
        """Return all rows whose ``Id`` exactly matches ``dataset_id``."""
        if "Id" not in self._table_columns:
            raise TableDatasetLookupError(
                "Dataset table has no 'Id' column.",
                context=self._context(dataset_id=dataset_id),
            )
        if self._dataset_ids is not None and dataset_id not in self._dataset_ids:
            raise TableDatasetLookupError(
                "Dataset identifier was not found.",
                context=self._context(dataset_id=dataset_id),
            )
        selected = self.dataset_table.loc[self.dataset_table["Id"] == dataset_id]
        if selected.empty:
            raise TableDatasetLookupError(
                "Dataset identifier was not found.",
                context=self._context(dataset_id=dataset_id),
            )
        return selected.copy().reset_index(drop=True)

    def get_dataset_positions(self, dataset_id: str) -> tuple[int, ...]:
        """Return ordered positional metadata for one dataset identifier."""
        if self._dataset_ids is None or dataset_id not in self._dataset_ids:
            raise TableDatasetLookupError(
                "Dataset positional metadata was not found.",
                context=self._context(dataset_id=dataset_id),
            )
        return tuple(self._dataset_ids[dataset_id])

    def filter(self, **conditions: Any) -> pd.DataFrame:
        """Return rows matching every exact column-or-symbol condition."""
        selected = self.dataset_table
        for requested, value in conditions.items():
            column = self._resolve_column(requested)
            if self._is_missing(value):
                selected = selected.loc[selected[column].isna()]
            else:
                selected = selected.loc[selected[column] == value]
        return selected.copy().reset_index(drop=True)

    def to_numpy(
        self, columns: Optional[Sequence[str]] = None
    ) -> np.ndarray:
        """Return all or selected columns as a detached NumPy array."""
        try:
            if columns is None:
                frame = self.dataset_table
            else:
                if (
                    not isinstance(columns, Sequence)
                    or isinstance(columns, (str, bytes, bytearray))
                ):
                    raise TableDatasetFormatError(
                        "columns must be a sequence of column names or symbols.",
                        context=self._context(),
                    )
                resolved = [self._resolve_column(column) for column in columns]
                frame = self.dataset_table.loc[:, resolved]
            return frame.to_numpy(copy=True)
        except (TableDatasetFormatError, TableDatasetLookupError):
            raise
        except Exception as exc:
            raise TableDatasetConversionError(
                "Dataset could not be converted to NumPy.",
                context=self._context(),
            ) from exc
