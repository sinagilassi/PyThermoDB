import ast
import json
import logging
from typing import Any, Dict, List, Literal, Optional

import pandas as pd

from ..handlers import (
    TableColumnError,
    TableConstantsError,
    TableLookupError,
    TableValidationError,
)
from ..models import ConstantResult, PropertyMatch


logger = logging.getLogger(__name__)


class TableConstants:
    """Table-wide constants that are not associated with a component."""

    def __init__(
        self,
        databook_name: str | int,
        table_name: str | int,
        table_data: Dict[str, Any],
        table_values: Optional[List | Dict] = None,
        table_structure: Optional[Dict[str, Any]] = None
    ):
        self.databook_name = databook_name
        self.table_name = table_name
        self.table_data = table_data
        self.table_values = table_values if table_values is not None else []
        self.table_structure = table_structure if table_structure is not None else table_data

    @property
    def table_columns(self) -> List[str]:
        try:
            return self.table_data['COLUMNS']
        except KeyError as exc:
            raise TableColumnError(
                "Table columns not found in the constants table structure!",
                databook_name=self.databook_name,
                table_name=self.table_name,
                context={"column_name": "COLUMNS"},
            ) from exc

    def data_structure(self) -> pd.DataFrame:
        """Return the constants records using their declared columns."""
        try:
            return pd.DataFrame(self.table_values, columns=self.table_columns)
        except Exception as exc:
            raise TableConstantsError(
                "Failed to build constants data structure",
                databook_name=self.databook_name,
                table_name=self.table_name,
            ) from exc

    def get_constant(
        self,
        constant: str | int,
        message: Optional[str] = None,
        strict: bool = True
    ) -> Optional[ConstantResult]:
        """Retrieve a constant by name, symbol, or its ``No.`` identifier.

        When ``strict`` is ``False``, returns ``None`` if the constant is not found.
        """
        data = self.data_structure()
        row = None

        if isinstance(constant, str):
            lookup = constant.strip().lower()
            for column in ('Name', 'Symbol'):
                if column in data.columns:
                    matches = data[
                        data[column].astype(
                            str).str.strip().str.lower() == lookup
                    ]
                    if not matches.empty:
                        row = matches.iloc[0]
                        break
        elif isinstance(constant, int):
            if 'No.' not in data.columns:
                raise TableColumnError(
                    "Constant identifier column 'No.' not found!",
                    databook_name=self.databook_name,
                    table_name=self.table_name,
                    context={"column_name": "No."},
                )
            matches = data[data['No.'] == constant]
            if not matches.empty:
                row = matches.iloc[0]
        else:
            raise TableValidationError(
                f"{constant} is not a valid constant identifier!",
                databook_name=self.databook_name,
                table_name=self.table_name,
                context={"constant": constant},
            )

        if row is None:
            logger.debug(
                "Constant lookup miss for %r (databook=%r, table=%r, strict=%s)",
                constant,
                self.databook_name,
                self.table_name,
                strict,
            )
            if not strict:
                return None
            raise TableLookupError(
                f"Constant '{constant}' not found!",
                databook_name=self.databook_name,
                table_name=self.table_name,
                context={"constant": constant},
            )

        return ConstantResult(
            constant_name=row.get('Name'),
            symbol=row.get('Symbol'),
            state=row.get('State'),
            value=self._coerce_constant_value(row.get('Value')),
            unit=row.get('Unit'),
            description=row.get('Description'),
            message=str(message) if message else 'No message',
            databook_name=self.databook_name,
            table_name=self.table_name,
        )

    # SECTION: convert/force constant values to native Python types
    @staticmethod
    def _coerce_constant_value(value: Any) -> Any:
        """Convert stringified scalar/collection literals to native Python types.

        YAML-native values stay unchanged; coercion is applied only to string
        values (typically from CSV-backed constants tables).
        """
        if not isinstance(value, str):
            return value

        text = value.strip()
        if text == '':
            return value

        lower_text = text.lower()
        if lower_text in {'none', 'null', 'nan'}:
            return None
        if lower_text == 'true':
            return True
        if lower_text == 'false':
            return False

        try:
            return json.loads(text)
        except Exception:
            pass

        try:
            return ast.literal_eval(text)
        except Exception:
            return value

    def _is_value_available(
        self,
        value: str,
        column: Literal['Name', 'Symbol'],
        search_mode: str
    ) -> PropertyMatch:
        if not isinstance(value, str):
            return PropertyMatch(
                prop_id=str(value), availability=False, search_mode=search_mode
            )
        data = self.data_structure()
        if column not in data.columns:
            return PropertyMatch(
                prop_id=value, availability=False, search_mode=search_mode
            )
        lookup = value.strip().lower()
        available = bool(
            (data[column].astype(str).str.strip().str.lower() == lookup).any()
        )
        return PropertyMatch(
            prop_id=value, availability=available, search_mode=search_mode
        )

    def is_name_available(self, name: str) -> PropertyMatch:
        return self._is_value_available(name, 'Name', 'NAME')

    def is_symbol_available(self, symbol: str) -> PropertyMatch:
        return self._is_value_available(symbol, 'Symbol', 'SYMBOL')

    def is_constant_available(
        self,
        constant: str,
        search_mode: Literal['NAME', 'SYMBOL', 'BOTH'] = 'BOTH'
    ) -> PropertyMatch:
        if search_mode == 'NAME':
            return self.is_name_available(constant)
        if search_mode == 'SYMBOL':
            return self.is_symbol_available(constant)
        if search_mode != 'BOTH':
            raise TableValidationError(
                "Invalid search mode! Must be 'NAME', 'SYMBOL', or 'BOTH'.",
                databook_name=self.databook_name,
                table_name=self.table_name,
                context={"search_mode": search_mode},
            )
        available = (
            self.is_name_available(constant).availability or
            self.is_symbol_available(constant).availability
        )
        return PropertyMatch(
            prop_id=constant, availability=available, search_mode='BOTH'
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'COLUMNS': list(self.table_columns),
            'VALUES': self.table_values,
        }
