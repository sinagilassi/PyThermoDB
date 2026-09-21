"""Runtime support for scalar multi-component interaction records.

A :class:`TableInteractionData` row describes one ordered ``Mixture`` and one
or more independent scalar interaction properties.  It deliberately does not
construct a matrix or tensor.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any, Literal, Optional

import pandas as pd

from ..handlers import (
    TableInteractionDataConversionError,
    TableInteractionDataDefinitionError,
    TableInteractionDataFormatError,
    TableInteractionDataFrameError,
    TableInteractionDataLookupError,
    TableInteractionDataStructureError,
)


class TableInteractionData:
    """Store scalar interaction properties by an ordered mixture key.

    Parameters
    ----------
    databook_name:
        Name or identifier of the source databook.
    table_name:
        Name or identifier of the source table.
    table_data:
        Canonical reference data containing ``INTERACTION-SYMBOL``,
        ``STRUCTURE``, and ``VALUES``.
    interaction_table:
        Optional already-built table whose columns exactly match ``STRUCTURE``.
    interaction_symbol:
        Optional symbol override, primarily for controlled build pipelines.

    Notes
    -----
    A mixture is an ordered tuple of opaque component IDs.  Therefore
    ``A|B|C`` and ``B|A|C`` are distinct records unless a future model adds
    explicit symmetry metadata.
    """

    # ? A later schema may provide explicit interaction-symmetry metadata.
    _component_key_modes = (
        "Name",
        "Formula",
        "Name-State",
        "Formula-State",
        "Name-Formula-State",
        "Formula-Name-State",
    )

    def __init__(
        self,
        databook_name: str | int,
        table_name: str | int,
        table_data: dict[str, Any],
        interaction_table: Optional[pd.DataFrame] = None,
        interaction_symbol: Optional[list[str]] = None,
    ) -> None:
        """Initialize, validate, and index interaction records."""
        self.databook_name = databook_name
        self.table_name = table_name
        self.table_data = table_data
        self.interaction_table = interaction_table

        # SECTION: instance-owned state
        # ! Mutable state must never be shared between table instances.
        self.__interaction_symbol: list[str] = []
        self._table_structure: dict[str, Any] = {}
        self._interaction_records: dict[tuple[str, ...], dict[str, Any]] = {}

        # SECTION: source definition validation
        if not isinstance(table_data, dict):
            raise TableInteractionDataStructureError(
                "table_data must be a dictionary",
                context=self._context(),
            )

        self._initialize_interaction_symbols(interaction_symbol)
        self._table_structure = self._generate_table_structure(table_data)
        self._validate_structure()
        self._build_interaction_records()

    # SECTION: private normalization and validation helpers
    def _context(self, **context: Any) -> dict[str, Any]:
        """Return common context included in every public exception."""
        base_context = {
            "databook_name": self.databook_name,
            "table_name": self.table_name,
        }
        base_context.update(context)
        return base_context

    @staticmethod
    def _is_null(value: Any) -> bool:
        """Treat Python ``None`` and DataFrame NaN values as unavailable."""
        return value is None or (
            isinstance(value, float) and math.isnan(value)
        )

    @classmethod
    def _normalize_mixture_key(
        cls,
        mixture: str | Sequence[str],
    ) -> tuple[str, ...]:
        """Normalize a raw mixture string or component-ID sequence.

        Whitespace around participants is removed.  The method does not parse,
        sort, or otherwise reinterpret component IDs.
        """
        # ! The `|` delimiter is the only structural syntax in a mixture ID.
        if isinstance(mixture, str):
            tokens = mixture.split("|")
        elif isinstance(mixture, Sequence) and not isinstance(
            mixture,
            (bytes, bytearray),
        ):
            tokens = list(mixture)
        else:
            raise TableInteractionDataFormatError(
                "Mixture must be a string or a sequence of strings."
            )

        if not all(isinstance(token, str) for token in tokens):
            raise TableInteractionDataFormatError(
                "Mixture participants must be strings."
            )

        normalized = tuple(token.strip() for token in tokens)
        if len(normalized) < 2 or any(not token for token in normalized):
            raise TableInteractionDataFormatError(
                "Mixture must contain at least two non-empty participants."
            )

        return normalized

    def _initialize_interaction_symbols(
        self,
        supplied_symbols: Optional[list[str]],
    ) -> None:
        """Read and normalize the ``INTERACTION-SYMBOL`` declaration."""
        # NOTE: Existing references may use descriptive one-item mappings.
        source_symbols = (
            supplied_symbols
            if supplied_symbols is not None
            else self.table_data.get("INTERACTION-SYMBOL")
        )
        if not isinstance(source_symbols, list) or not source_symbols:
            raise TableInteractionDataStructureError(
                "INTERACTION-SYMBOL must be a non-empty list.",
                context=self._context(),
            )

        symbols: list[str] = []
        for item in source_symbols:
            if isinstance(item, str):
                symbol = item
            elif isinstance(item, dict) and len(item) == 1:
                symbol = next(iter(item.values()))
            else:
                raise TableInteractionDataFormatError(
                    "Invalid INTERACTION-SYMBOL item.",
                    context=self._context(item=item),
                )

            if not isinstance(symbol, str) or not symbol.strip():
                raise TableInteractionDataDefinitionError(
                    "Interaction symbols must be non-empty strings.",
                    context=self._context(item=item),
                )

            normalized_symbol = symbol.strip()
            if normalized_symbol in symbols:
                raise TableInteractionDataDefinitionError(
                    "Interaction symbols must be unique.",
                    context=self._context(property_name=normalized_symbol),
                )
            symbols.append(normalized_symbol)

        self.__interaction_symbol = symbols

    def _generate_table_structure(
        self,
        table_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Extract the immutable reference table structure."""
        structure = table_data.get("STRUCTURE")
        if not isinstance(structure, dict):
            raise TableInteractionDataStructureError(
                "STRUCTURE must be a dictionary.",
                context=self._context(),
            )
        return dict(structure)

    def _validate_structure(self) -> None:
        """Validate aligned structural declarations and property mappings."""
        columns = self._table_structure.get("COLUMNS")
        symbols = self._table_structure.get("SYMBOL")
        units = self._table_structure.get("UNIT")

        # NOTE: Validate separately so static type checkers can narrow each list.
        if not isinstance(columns, list):
            raise TableInteractionDataStructureError(
                "COLUMNS must be a list.",
                context=self._context(),
            )
        if not isinstance(symbols, list):
            raise TableInteractionDataStructureError(
                "SYMBOL must be a list.",
                context=self._context(),
            )
        if not isinstance(units, list):
            raise TableInteractionDataStructureError(
                "UNIT must be a list.",
                context=self._context(),
            )

        if len(columns) != len(symbols) or len(columns) != len(units):
            raise TableInteractionDataStructureError(
                "COLUMNS, SYMBOL, and UNIT lengths must match.",
                context=self._context(),
            )

        if "Mixture" not in columns:
            raise TableInteractionDataStructureError(
                "Interaction tables require a Mixture column.",
                context=self._context(),
            )

        # SECTION: each declared interaction symbol needs exactly one column
        for property_name in self.__interaction_symbol:
            self._property_column(property_name)

    def _property_column(self, property_name: str) -> str:
        """Resolve one interaction property to its aligned source column."""
        if property_name not in self.__interaction_symbol:
            raise TableInteractionDataLookupError(
                "Interaction property does not exist.",
                context=self._context(property_name=property_name),
            )

        columns = self._table_structure["COLUMNS"]
        symbols = self._table_structure["SYMBOL"]
        matching_columns = [
            columns[index]
            for index, symbol in enumerate(symbols)
            if symbol == property_name
        ]
        if property_name in columns:
            matching_columns.append(property_name)

        unique_columns = list(dict.fromkeys(matching_columns))
        if len(unique_columns) != 1:
            raise TableInteractionDataDefinitionError(
                "Interaction property must resolve to exactly one column.",
                context=self._context(
                    property_name=property_name,
                    matches=unique_columns,
                ),
            )

        return unique_columns[0]

    def _source_frame(self) -> pd.DataFrame:
        """Create a validated copy of the row-oriented source DataFrame."""
        columns = self._table_structure["COLUMNS"]

        if self.interaction_table is not None:
            if not isinstance(self.interaction_table, pd.DataFrame):
                raise TableInteractionDataFrameError(
                    "interaction_table must be a pandas DataFrame.",
                    context=self._context(),
                )
            if list(self.interaction_table.columns) != columns:
                raise TableInteractionDataFrameError(
                    "interaction_table columns must match STRUCTURE.COLUMNS.",
                    context=self._context(),
                )
            return self.interaction_table.copy()

        values = self.table_data.get("VALUES")
        if not isinstance(values, list):
            raise TableInteractionDataStructureError(
                "VALUES must be a list.",
                context=self._context(),
            )

        for row in values:
            if (
                not isinstance(row, Sequence)
                or isinstance(row, str)
                or len(row) != len(columns)
            ):
                raise TableInteractionDataStructureError(
                    "Every VALUES row must align with COLUMNS.",
                    context=self._context(row=row),
                )

        return pd.DataFrame(values, columns=columns)

    def _build_interaction_records(self) -> None:
        """Build the primary mixture-first lookup mapping."""
        # SECTION: row-to-record transformation
        frame = self._source_frame()
        self.interaction_table = frame.copy()
        property_columns = {
            name: self._property_column(name)
            for name in self.__interaction_symbol
        }

        for _, row in frame.iterrows():
            mixture_key = self._normalize_mixture_key(row["Mixture"])
            if mixture_key in self._interaction_records:
                raise TableInteractionDataDefinitionError(
                    "Duplicate normalized mixture.",
                    context=self._context(mixture=mixture_key),
                )

            # NOTE: None means unavailable; numeric zero remains a valid value.
            self._interaction_records[mixture_key] = {
                name: (
                    None
                    if self._is_null(row[column])
                    else row[column]
                )
                for name, column in property_columns.items()
            }

    # SECTION: public structural properties
    @property
    def interaction_symbol(self) -> list[str]:
        """Return a copy of declared scalar interaction-property symbols."""
        return self.__interaction_symbol.copy()

    @property
    def table_structure(self) -> dict[str, Any]:
        """Return a shallow copy of the reference structure."""
        return dict(self._table_structure)

    @property
    def mixtures(self) -> list[tuple[str, ...]]:
        """Return normalized mixture keys in their source order."""
        return list(self._interaction_records)

    @property
    def mixture_count(self) -> int:
        """Return the number of distinct normalized mixtures."""
        return len(self._interaction_records)

    @property
    def interaction_orders(self) -> set[int]:
        """Return the interaction orders represented by loaded records."""
        return {len(mixture_key) for mixture_key in self._interaction_records}

    # SECTION: scalar and row lookup APIs
    def get(
        self,
        property_name: str,
        mixture: str | Sequence[str],
        *,
        default: Any = None,
    ) -> Any:
        """Return an interaction value or ``default`` when it is unavailable."""
        try:
            mixture_key = self._normalize_mixture_key(mixture)
        except TableInteractionDataFormatError:
            return default

        record = self._interaction_records.get(mixture_key)
        if record is None:
            return default
        return record.get(property_name, default)

    def require(
        self,
        property_name: str,
        mixture: str | Sequence[str],
    ) -> Any:
        """Return a defined interaction value or raise a lookup error."""
        mixture_key = self._normalize_mixture_key(mixture)
        if property_name not in self.__interaction_symbol:
            raise TableInteractionDataLookupError(
                "Interaction property does not exist.",
                context=self._context(property_name=property_name),
            )

        record = self._interaction_records.get(mixture_key)
        if record is None:
            raise TableInteractionDataLookupError(
                "Interaction mixture does not exist.",
                context=self._context(mixture=mixture_key),
            )

        value = record[property_name]
        if value is None:
            raise TableInteractionDataLookupError(
                "Interaction value is unavailable.",
                context=self._context(
                    property_name=property_name,
                    mixture=mixture_key,
                ),
            )
        return value

    def has(
        self,
        property_name: str,
        mixture: str | Sequence[str],
        *,
        require_value: bool = True,
    ) -> bool:
        """Return whether a property exists for a mixture, optionally with a value."""
        try:
            mixture_key = self._normalize_mixture_key(mixture)
        except TableInteractionDataFormatError:
            return False

        record = self._interaction_records.get(mixture_key)
        if record is None or property_name not in record:
            return False
        return not require_value or record[property_name] is not None

    def get_mixture(
        self,
        mixture: str | Sequence[str],
        *,
        include_null: bool = True,
    ) -> dict[str, Any]:
        """Return scalar values for one mixture without exposing internal state."""
        mixture_key = self._normalize_mixture_key(mixture)
        record = self._interaction_records.get(mixture_key)
        if record is None:
            return {}

        return {
            name: value
            for name, value in record.items()
            if include_null or value is not None
        }

    def get_property(
        self,
        property_name: str,
        *,
        include_null: bool = False,
    ) -> dict[tuple[str, ...], Any]:
        """Return one scalar property indexed by normalized mixture keys."""
        if property_name not in self.__interaction_symbol:
            raise TableInteractionDataLookupError(
                "Interaction property does not exist.",
                context=self._context(property_name=property_name),
            )

        return {
            mixture_key: record[property_name]
            for mixture_key, record in self._interaction_records.items()
            if include_null or record[property_name] is not None
        }

    def select(
        self,
        *,
        property_name: Optional[str] = None,
        contains: Optional[Sequence[str]] = None,
        order: Optional[int] = None,
        include_null: bool = False,
    ) -> dict:
        """Select records by exact component IDs, interaction order, or property."""
        if property_name is not None and property_name not in self.__interaction_symbol:
            raise TableInteractionDataLookupError(
                "Interaction property does not exist.",
                context=self._context(property_name=property_name),
            )

        contains_tokens = tuple(contains or ())
        if not all(
            isinstance(token, str) and token.strip()
            for token in contains_tokens
        ):
            raise TableInteractionDataFormatError(
                "contains must contain non-empty component IDs.",
                context=self._context(),
            )

        result: dict = {}
        for mixture_key, record in self._interaction_records.items():
            if order is not None and len(mixture_key) != order:
                continue
            if not all(token.strip() in mixture_key for token in contains_tokens):
                continue

            if property_name is None:
                selected_record = {
                    name: value
                    for name, value in record.items()
                    if include_null or value is not None
                }
                if selected_record or include_null:
                    result[mixture_key] = selected_record
            elif include_null or record[property_name] is not None:
                result[mixture_key] = record[property_name]

        return result

    def interaction_order(self, mixture: str | Sequence[str]) -> int:
        """Return the number of ordered participants in a mixture."""
        return len(self._normalize_mixture_key(mixture))

    # SECTION: compact interaction convenience accessors
    def i(
        self,
        property: str,
        mixture: Optional[str | Sequence[str]] = None,
        *,
        default: Any = None,
        message: Optional[str] = None,
    ) -> dict[str, Any]:
        """Return one scalar interaction as a DataResult-style dictionary.

        Parameters
        ----------
        property : str
            Interaction symbol, or an encoded query in the form
            ``symbol | component-1 | component-2 [| ...]`` when ``mixture``
            is omitted.
        mixture : str | Sequence[str], optional
            Ordered source mixture. It is required when ``property`` contains
            only the interaction symbol.
        default : Any, optional
            Value returned when the ordered mixture or its scalar is absent.
        message : str, optional
            Caller-facing description included in the result.

        Returns
        -------
        dict[str, Any]
            A DataResult-compatible mapping containing property metadata and
            the selected scalar value.

        Notes
        -----
        The compact encoded form preserves component order. It never sorts or
        expands an interaction record into a matrix.
        """
        # SECTION: parse direct or compact interaction query
        if not isinstance(property, str) or not property.strip():
            raise TableInteractionDataFormatError(
                "property must be a non-empty string.",
                context=self._context(),
            )

        property_name = property.strip()
        if mixture is None:
            query_tokens = [token.strip() for token in property.split("|")]
            if len(query_tokens) < 3 or any(not token for token in query_tokens):
                raise TableInteractionDataFormatError(
                    "Compact interaction queries require a symbol and at least two participants.",
                    context=self._context(property=property),
                )
            property_name = query_tokens[0]
            mixture_key = self._normalize_mixture_key(query_tokens[1:])
        else:
            mixture_key = self._normalize_mixture_key(mixture)

        if property_name not in self.__interaction_symbol:
            raise TableInteractionDataLookupError(
                "Interaction property does not exist.",
                context=self._context(property_name=property_name),
            )

        # NOTE: Units are aligned with the resolved property source column.
        column = self._property_column(property_name)
        column_index = self._table_structure["COLUMNS"].index(column)
        unit = self._table_structure["UNIT"][column_index]
        value = self.get(property_name, mixture_key, default=default)
        mixture_display = " | ".join(mixture_key)
        result_message = message or (
            f"Get {property_name} interaction value for {mixture_display}."
        )
        return {
            "property_name": property_name,
            "symbol": property_name,
            "unit": unit,
            "value": value,
            "message": result_message,
            "databook_name": self.databook_name,
            "table_name": self.table_name,
        }

    def iis(
        self,
        property_name: str,
        mixtures: Optional[Sequence[str | Sequence[str]]] = None,
        *,
        include_null: bool = False,
        default: Any = None,
    ) -> dict[tuple[str, ...], Any]:
        """Return one interaction property for multiple ordered mixtures.

        Parameters
        ----------
        property_name : str
            Declared interaction symbol to retrieve.
        mixtures : Sequence[str | Sequence[str]], optional
            Ordered mixtures to retrieve. If omitted, every stored mixture is
            considered.
        include_null : bool, default=False
            Include records whose scalar value is ``None``.
        default : Any, optional
            Value used for requested mixtures not present in the table.

        Returns
        -------
        dict[tuple[str, ...], Any]
            Values indexed by normalized, order-preserving mixture tuples.

        Notes
        -----
        ``iis`` is the plural convenience form of ``i``. It only collects
        scalar records and never generates pairwise or tensor values.
        """
        if property_name not in self.__interaction_symbol:
            raise TableInteractionDataLookupError(
                "Interaction property does not exist.",
                context=self._context(property_name=property_name),
            )

        # NOTE: The all-record case uses the established property lookup path.
        if mixtures is None:
            return self.get_property(property_name, include_null=include_null)
        if isinstance(mixtures, (str, bytes)) or not isinstance(mixtures, Sequence):
            raise TableInteractionDataFormatError(
                "mixtures must be a sequence of mixture strings or token sequences.",
                context=self._context(),
            )

        result: dict[tuple[str, ...], Any] = {}
        for mixture in mixtures:
            mixture_key = self._normalize_mixture_key(mixture)
            value = self.get(property_name, mixture_key, default=default)
            if include_null or value is not None:
                result[mixture_key] = value
        return result
    # SECTION: Component-object lookup APIs
    @staticmethod
    def _component_identifier(component: Any, component_key: str) -> str:
        """Build one supported component identifier from a Component-like object."""
        # NOTE: This method formats IDs only; it never infers chemical meaning.
        try:
            name = str(getattr(component, "name")).strip()
            formula = str(getattr(component, "formula")).strip()
            state = str(getattr(component, "state")).strip()
        except AttributeError as exc:
            raise TableInteractionDataFormatError(
                "components must provide name, formula, and state."
            ) from exc

        candidate_ids = {
            "Name": name,
            "Formula": formula,
            "Name-State": f"{name}-{state}",
            "Formula-State": f"{formula}-{state}",
            "Name-Formula-State": f"{name}-{formula}-{state}",
            "Formula-Name-State": f"{formula}-{name}-{state}",
        }
        if component_key not in candidate_ids:
            raise TableInteractionDataFormatError(
                f"Unsupported component_key: {component_key}."
            )
        return candidate_ids[component_key]

    def _resolve_mixture_from_components(
        self,
        components: Sequence[Any],
        component_key: Optional[str] = None,
    ) -> tuple[str, ...]:
        """Resolve Component objects to exactly one stored mixture record."""
        if (
            not isinstance(components, Sequence)
            or isinstance(components, (str, bytes))
            or len(components) < 2
        ):
            raise TableInteractionDataFormatError(
                "components must contain at least two Component objects.",
                context=self._context(),
            )

        modes = (component_key,) if component_key is not None else self._component_key_modes
        matches: set[tuple[str, ...]] = set()
        for mode in modes:
            candidate = tuple(
                self._component_identifier(component, mode)
                for component in components
            )
            if candidate in self._interaction_records:
                matches.add(candidate)

        if len(matches) == 1:
            return next(iter(matches))
        if not matches:
            raise TableInteractionDataLookupError(
                "No component-key representation matches an interaction mixture.",
                context=self._context(
                    components=list(components),
                    component_key=component_key,
                ),
            )

        # ! Automatic matching must never silently choose an ambiguous source key.
        raise TableInteractionDataDefinitionError(
            "Component IDs resolve to ambiguous interaction mixtures.",
            context=self._context(
                components=list(components),
                matches=list(matches),
            ),
        )

    def get_from_components(
        self,
        property_name: str,
        components: Sequence[Any],
        *,
        component_key: Optional[str] = None,
        default: Any = None,
    ) -> Any:
        """Return a property for Component objects or the supplied default."""
        try:
            mixture_key = self._resolve_mixture_from_components(
                components,
                component_key,
            )
        except TableInteractionDataLookupError:
            return default

        return self.get(property_name, mixture_key, default=default)

    def get_mixture_from_components(
        self,
        components: Sequence[Any],
        *,
        component_key: Optional[str] = None,
        include_null: bool = True,
    ) -> dict[str, Any]:
        """Return the complete row for Component objects."""
        mixture_key = self._resolve_mixture_from_components(
            components,
            component_key,
        )
        return self.get_mixture(mixture_key, include_null=include_null)

    # SECTION: inspection and serialization APIs
    def get_interaction_table(
        self,
        mode: Literal["all", "available"] = "all",
    ) -> pd.DataFrame:
        """Return a copy of all rows or only rows with available values."""
        if mode not in {"all", "available"}:
            raise TableInteractionDataFormatError(
                "mode must be 'all' or 'available'.",
                context=self._context(mode=mode),
            )

        table_source = self.interaction_table
        if table_source is None:
            raise TableInteractionDataFrameError(
                "Interaction table is unavailable.",
                context=self._context(),
            )

        table = table_source.copy()
        if mode == "available":
            property_columns = [
                self._property_column(name)
                for name in self.__interaction_symbol
            ]
            table = table.loc[
                table[property_columns].notna().any(axis=1)
            ].copy()
        return table

    def interaction_data_structure(self) -> pd.DataFrame:
        """Return the reference structure in a display-friendly DataFrame."""
        structure = pd.DataFrame(self._table_structure)
        structure.insert(0, "ID", range(1, len(structure) + 1))
        return structure

    def get_interaction_data_info(self) -> dict[str, Any]:
        """Return table structure plus its declared interaction symbols."""
        return {
            **self.table_structure,
            "INTERACTION-SYMBOL": self.interaction_symbol,
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to canonical reference-compatible scalar interaction data."""
        # REVIEW: Retain rows rather than serializing derived lookup dictionaries.
        try:
            table_source = self.interaction_table
            if table_source is None:
                raise TableInteractionDataFrameError(
                    "Interaction table is unavailable.",
                    context=self._context(),
                )

            # ! Convert to object dtype first so missing numeric cells remain None,
            # not pandas NaN, in the canonical serializable representation.
            values = table_source.astype(object).where(
                pd.notna(table_source),
                None,
            ).values.tolist()
            return {
                "INTERACTION-SYMBOL": self.interaction_symbol,
                "STRUCTURE": self.table_structure,
                "VALUES": values,
            }
        except Exception as exc:
            raise TableInteractionDataConversionError(
                "Converting interaction data failed.",
                context=self._context(),
            ) from exc