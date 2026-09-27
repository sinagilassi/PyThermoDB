# import packages/modules
import logging
import pandas as pd
from typing import Optional, List, Dict, Any, Literal, cast
# local imports
from ..models import DataResult, PropertyMatch
from ..handlers import (
    TableColumnError,
    TableConversionError,
    TableDataError,
    TableLookupError,
    TableSymbolError,
    TableUnitError,
    TableValidationError,
)
from .table_util import TableUtil
# ! deps
from ..config.deps import get_config

# logger
logger = logging.getLogger(__name__)


class TableData:
    """Store and query component property table data.

    The class wraps a table definition loaded from a reference file and
    provides access to its columns, symbols, units, values, and property
    records. Property values can be retrieved by column name, symbol, or
    one-based column number.

    Parameters
    ----------
    databook_name : str | int
        Name or identifier of the source databook.
    table_name : str | int
        Name or identifier of the data table.
    table_data : dict
        Table structure and metadata loaded from the source reference.
    table_values : list | dict, optional
        Table values loaded from the source reference.
    table_structure : dict, optional
        Explicit table structure retained for compatibility with the table
        loading API.

    Notes
    -----
    The global configuration controls whether table values are retained. If
    ``include_data`` is false, property values are unavailable even when
    ``table_values`` is supplied. Integer property lookups are one-based.

    Methods
    -------
    data_structure()
        Return the table definition as a pandas DataFrame.
    get_property(property, message=None)
        Retrieve a property by name, symbol, or one-based column number.
    insert(property, message=None)
        Retrieve a property using the legacy insertion lookup behavior.
    is_property_available(prop_id, search_mode='BOTH')
        Check a property by symbol, column name, or both.
    to_dict()
        Return the stored property-data mapping as a dictionary.
    """

    # vars
    __trans_data = {}
    __prop_data = {}

    def __init__(
        self,
        databook_name,
        table_name,
        table_data,
        table_values: Optional[List | Dict] = None,
        table_structure: Optional[Dict[str, Any]] = None
    ):
        """Initialize a component property table.

        Parameters
        ----------
        databook_name : str | int
            Name or identifier of the source databook.
        table_name : str | int
            Name or identifier of the data table.
        table_data : dict
            Table data loaded from the source reference.
        table_values : list | dict, optional
            Property values loaded from the source reference.
        table_structure : dict, optional
            Explicit table structure, when provided.

        Notes
        -----
        The current configuration is read during initialization. When its
        ``include_data`` setting is false, supplied table values are discarded.
        """
        # NOTE: get config
        config = get_config()
        # ! include data tables based on config
        self.include_data = config.include_data
        # logging
        logger.debug(
            f"TableData initialized with include_data={self.include_data}"
        )

        # NOTE: set attributes
        self.databook_name = databook_name
        self.table_name = table_name

        # reference template (yml)
        self.table_data = table_data

        # table values (yml)
        self.__table_values = table_values if table_values else None

        # table structure (yml)
        self.__table_structure = table_structure if table_structure else None

        # SECTION: set data only if include_data is True
        if self.include_data is False:
            # logging
            logger.info(
                f"Data tables are excluded as per configuration. "
                f"Table data for '{self.table_name}' will not include property data."
            )
            self.__table_values = None

    @property
    def trans_data(self):
        """Return the stored transport-data payload."""
        return self.__trans_data

    @trans_data.setter
    def trans_data(self, value):
        """Replace the stored transport-data payload."""
        self.__trans_data = {}
        self.__trans_data = value

    @property
    def prop_data(self):
        """Return the property-data mapping used for lookups."""
        return self.__prop_data

    @prop_data.setter
    def prop_data(self, value):
        """Store property data while excluding the nested ``data`` entry."""
        self.__prop_data = {}
        exclude_key = 'data'
        self.__prop_data = {
            key: value for key, value in value.items() if key != exclude_key
        }

    @property
    def table_values(self):
        """Return table values, or print a notice and return ``None`` if absent."""
        if self.__table_values:
            return self.__table_values
        else:
            msg = f"""No table values found in the following reference \n
            ::: {self.databook_name}
            :::  {self.table_name}!
            """
            print(msg)
            return None

    @property
    def table_structure(self):
        """Return the explicit table structure, or ``None`` if absent."""
        if self.__table_structure:
            return self.__table_structure
        else:
            msg = f"""No table structure found in the following reference \n
            ::: {self.databook_name}
            :::  {self.table_name}!
            """
            print(msg)
            return None

    @property
    def table_columns(self, column_name: str = 'COLUMNS') -> List[str]:
        """Return column names from the table structure.

        Parameters
        ----------
        column_name : str
            Structure key to read. Defaults to ``'COLUMNS'``.

        Returns
        -------
        list[str]
            Declared table columns.

        Raises
        ------
        TableColumnError
            If the requested key is missing.
        TableDataError
            If the structure cannot be read.
        """
        try:
            return self.table_data[column_name]
        except KeyError as exc:
            raise TableColumnError(
                "Table columns not found in the data table structure!",
                databook_name=self.databook_name,
                table_name=self.table_name,
                context={"column_name": column_name},
            ) from exc
        except Exception as e:
            raise TableDataError(
                "Error retrieving table columns",
                databook_name=self.databook_name,
                table_name=self.table_name,
            ) from e

    @property
    def table_symbols(self, symbol_name: str = 'SYMBOL') -> List[str]:
        """Return unique, usable property symbols from the table structure.

        Parameters
        ----------
        symbol_name : str
            Structure key to read. Defaults to ``'SYMBOL'``.

        Returns
        -------
        list[str]
            Symbols with null-like, placeholder, and duplicate values removed.

        Raises
        ------
        TableSymbolError
            If the requested key is missing.
        TableDataError
            If the symbols cannot be read.
        """
        try:
            # get all symbols
            symbols_ = self.table_data[symbol_name]

            # remove None values
            symbols = [s for s in symbols_ if s is not None]
            # remove 'None' strings
            symbols = [s for s in symbols if s.lower() != 'none']
            # remove dash/hyphen/underscore/empty strings
            symbols = [s for s in symbols if s not in ('-', '', '_')]

            # remove duplicates while preserving order (Python 3.7+)
            seen = set()
            symbols = [s for s in symbols if s not in seen and not seen.add(s)]

            return symbols
        except KeyError as exc:
            raise TableSymbolError(
                "Table symbols not found in the data table structure!",
                databook_name=self.databook_name,
                table_name=self.table_name,
                context={"symbol_name": symbol_name},
            ) from exc
        except Exception as e:
            raise TableDataError(
                "Error retrieving table symbols",
                databook_name=self.databook_name,
                table_name=self.table_name,
            ) from e

    @property
    def table_units(
        self,
        unit_name: str = 'UNIT'
    ) -> List[str]:
        """Return property units from the table structure.

        Parameters
        ----------
        unit_name : str
            Structure key to read. Defaults to ``'UNIT'``.

        Returns
        -------
        list[str]
            Declared property units.

        Raises
        ------
        TableUnitError
            If the requested key is missing.
        TableDataError
            If the units cannot be read.
        """
        try:
            return self.table_data[unit_name]
        except KeyError as exc:
            raise TableUnitError(
                "Table units not found in the data table structure!",
                databook_name=self.databook_name,
                table_name=self.table_name,
                context={"unit_name": unit_name},
            ) from exc
        except Exception as e:
            raise TableDataError(
                "Error retrieving table units",
                databook_name=self.databook_name,
                table_name=self.table_name,
            ) from e

    @property
    def property_names(self) -> List[str]:
        """Return property columns excluding component identity columns.

        Returns
        -------
        list[str]
            Columns other than ``id``, ``no``, ``name``, ``formula``, and
            ``state`` (case-insensitive).

        Raises
        ------
        TableDataError
            If property names cannot be read.
        """
        try:
            # NOTE: column names
            prop_names = self.table_columns

            # NOTE: remove "Name", "Formula", "State" from property names
            exclude_props = ['id', 'no.', 'no', 'name', 'formula', 'state']

            property_names = [
                prop for prop in prop_names if prop.lower() not in exclude_props
            ]

            return property_names
        except Exception as e:
            raise TableDataError(
                "Error retrieving property names",
                databook_name=self.databook_name,
                table_name=self.table_name,
            ) from e

    def data_structure(self):
        """Return the table definition as a DataFrame with an ``ID`` column.

        The generated one-based ``ID`` column is placed at the end of the
        returned DataFrame.
        """
        # dataframe
        df = pd.DataFrame(self.table_data)
        # add ID column
        df.insert(0, 'ID', range(1, len(df) + 1))
        # arrange columns
        # change the position of ID column to the last
        cols = df.columns.tolist()
        cols.insert(len(cols), cols.pop(cols.index('ID')))
        df = df[cols]

        return df

    def get_property(
            self,
            property: str | int,
            message: Optional[str] = None
    ) -> DataResult:
        """Retrieve a component property from the property-data mapping.

        Parameters
        ----------
        property : str | int
            Property name, symbol, or one-based column number.
        message : str, optional
            Message to include in the result.

        Returns
        -------
        DataResult
            The selected property and its metadata.

        Raises
        ------
        TableLookupError
            If a string property name or symbol is not found.
        TableValidationError
            If ``property`` is neither a string nor an integer.
        """
        # ! get data for a selected component
        # dataframe
        df = pd.DataFrame(self.prop_data)

        get_data = None
        # choose a column
        if isinstance(property, str):
            # df = df[property_name]
            # look up prop_data dict
            # ! case insensitive
            prop_data_keys_ = [key.lower() for key in self.prop_data.keys()]

            # NOTE: property lower
            property_ = property.lower().strip()

            # check key exists
            if property_ in prop_data_keys_:
                # loop through prop_data dict
                for key, value in self.prop_data.items():
                    # check key
                    if property_ == key.lower():
                        # value found
                        get_data = self.prop_data[key]
                        # property name
                        property = key
                        break
                # get_data = self.prop_data[property]
            else:
                # NOTE: symbol
                # check symbol value in each item
                for key, value in self.prop_data.items():
                    # check if property is in the symbol
                    # ! case insensitive
                    if property_ == str(value['symbol']).lower().strip():
                        # value found
                        get_data = self.prop_data[key]
                        # property name
                        property = key
                        break

            # ! check if property found
            if get_data is None:
                raise TableLookupError(
                    f"Property '{property}' not found!",
                    databook_name=self.databook_name,
                    table_name=self.table_name,
                    context={"property": property},
                )
            # series
            sr = pd.Series(get_data, dtype='str')
            # print(type(sr))

        elif isinstance(property, int):
            # get column index
            column_index = df.columns[property-1]
            sr = df.loc[:, column_index]
            # print(type(sr))

        else:
            raise TableValidationError(
                f"loading error! {property} is not a valid type!",
                databook_name=self.databook_name,
                table_name=self.table_name,
                context={"property": property},
            )

        # convert to dict
        data_dict = self._build_data_result(sr)
        # print(data_dict, type(data_dict))

        # property name
        if isinstance(property, str):
            data_dict['property_name'] = property
        else:
            data_dict['property_name'] = df.columns[property-1]

        # update message
        if message:
            data_dict['message'] = str(message)
        else:
            data_dict['message'] = 'No message'

        # add databook and table name
        data_dict['databook_name'] = self.databook_name if self.databook_name else 'No databook name'
        data_dict['table_name'] = self.table_name if self.table_name else 'No table name'

        # res
        return data_dict

    def insert(
            self,
            property: str | int,
            message: Optional[str] = None
    ) -> DataResult:
        """Retrieve a property using the legacy insertion lookup behavior.

        Parameters
        ----------
        property : str | int
            Property name, symbol, or one-based column number.
        message : str, optional
            Message to include in the result.

        Returns
        -------
        DataResult
            The selected property and its metadata.

        Raises
        ------
        TableLookupError
            If a string property name or symbol is not found.
        TableValidationError
            If ``property`` is neither a string nor an integer.
        """
        # ! get data for a selected component
        # dataframe
        df = pd.DataFrame(self.prop_data)

        get_data = None
        # choose a column
        if isinstance(property, str):
            # df = df[property_name]
            # look up prop_data dict
            # check key exists
            if property in self.prop_data.keys():
                get_data = self.prop_data[property]
            else:
                # check symbol value in each item
                for key, value in self.prop_data.items():
                    if property == value['symbol']:
                        # value found
                        get_data = self.prop_data[key]
                        # property name
                        property = key
                        break
            if get_data is None:
                raise TableLookupError(
                    f"Property '{property}' not found!",
                    databook_name=self.databook_name,
                    table_name=self.table_name,
                    context={"property": property},
                )
            # series
            sr = pd.Series(get_data, dtype='str')
            # print(type(sr))

        elif isinstance(property, int):
            # get column index
            column_index = df.columns[property-1]
            sr = df.loc[:, column_index]
            # print(type(sr))

        else:
            raise TableValidationError(
                f"loading error! {property} is not a valid type!",
                databook_name=self.databook_name,
                table_name=self.table_name,
                context={"property": property},
            )

        # convert to dict
        data_dict = self._build_data_result(sr)
        # print(data_dict, type(data_dict))

        # property name
        if isinstance(property, str):
            data_dict['property_name'] = property
        else:
            data_dict['property_name'] = df.columns[property-1]

        # update message
        if message:
            data_dict['message'] = str(message)
        else:
            data_dict['message'] = 'No message'

        # add databook and table name
        data_dict['databook_name'] = self.databook_name if self.databook_name else 'No databook name'
        data_dict['table_name'] = self.table_name if self.table_name else 'No table name'

        # res
        return data_dict

    def to_dict(self):
        """Return the property-data mapping as a dictionary.

        Returns
        -------
        dict
            Stored property data, excluding any nested ``data`` entry.

        Raises
        ------
        TableConversionError
            If the property data cannot be converted.
        """
        try:
            # comp data
            res = self.prop_data

            return res
        except Exception as e:
            raise TableConversionError(
                "Conversion failed",
                databook_name=self.databook_name,
                table_name=self.table_name,
            ) from e

    def is_symbol_available(self, symbol: str):
        """Return whether a symbol is available in the table.

        Parameters
        ----------
        symbol : str
            Symbol to check.

        Returns
        -------
        PropertyMatch
            Availability result using ``SYMBOL`` search mode.
        """
        try:
            # NOTE: get symbols
            symbols = self.table_symbols

            # SECTION: check if symbol exists (case-sensitive)
            return TableUtil.is_symbol_available(symbol, symbols)
        except Exception as e:
            logger.error(f"Error checking symbol availability: {e}")
            return PropertyMatch(
                prop_id=symbol,
                availability=False,
                search_mode='SYMBOL',
            )

    def is_column_name_available(self, column_name: str):
        """Return whether a column name is available in the table.

        Parameters
        ----------
        column_name : str
            Column name to check.

        Returns
        -------
        PropertyMatch
            Availability result using ``COLUMN`` search mode.
        """
        try:
            # NOTE: get column names
            column_names = self.table_columns

            # SECTION: check if column exists (case-sensitive)
            return TableUtil.is_column_name_available(column_name, column_names)
        except Exception as e:
            logger.error(f"Error checking column name availability: {e}")
            return PropertyMatch(
                prop_id=column_name,
                availability=False,
                search_mode='COLUMN',
            )

    def is_property_available(
            self,
            prop_id: str,
            search_mode: Literal[
                'SYMBOL', 'COLUMN', 'BOTH'
            ] = 'BOTH'
    ) -> PropertyMatch:
        """Check whether a property is available by symbol, column, or both.

        Parameters
        ----------
        prop_id : str
            Property ID to check.
        search_mode : Literal['SYMBOL', 'COLUMN', 'BOTH'], optional
            Search mode. Defaults to ``'BOTH'``.

        Returns
        -------
        PropertyMatch
            Availability result. Invalid inputs and internal lookup errors
            produce an unavailable result.
        """
        try:
            # NOTE: check inputs
            if not isinstance(prop_id, str):
                logger.error(
                    "Invalid property ID input! Property ID must be a string.")
                return False

            # SECTION: get property names
            if search_mode == 'SYMBOL':
                # ! symbol only
                return self.is_symbol_available(prop_id)
            elif search_mode == 'COLUMN':
                # ! column name only
                return self.is_column_name_available(prop_id)
            elif search_mode != 'BOTH':
                logger.error(
                    "Invalid search mode! Must be 'SYMBOL', 'COLUMN', or 'BOTH'."
                )
                return False

            # SECTION: check both symbol and column name
            # NOTE: check symbols (true/false)
            check_symbol_res = self.is_symbol_available(prop_id)

            # NOTE: check column names (true/false)
            check_column_res = self.is_column_name_available(prop_id)

            # check
            if check_symbol_res.availability or check_column_res.availability:
                return PropertyMatch(
                    prop_id=prop_id,
                    availability=True,
                    search_mode='BOTH'
                )
            else:
                return PropertyMatch(
                    prop_id=prop_id,
                    availability=False,
                    search_mode='BOTH'
                )

        except Exception as e:
            logger.error(f"Error checking property availability: {e}")
            return PropertyMatch(
                prop_id=prop_id,
                availability=False,
                search_mode=search_mode,
            )

    def _build_data_result(self, sr: pd.Series) -> DataResult:
        """Build a typed :class:`DataResult` from a pandas Series."""
        sr_dict = cast(Dict[str, Any], sr.to_dict())
        return DataResult(
            property_name=cast(Optional[str], sr_dict.get('property_name')),
            symbol=cast(Optional[str], sr_dict.get('symbol')),
            unit=cast(Optional[str], sr_dict.get('unit')),
            value=cast(Optional[str | float], sr_dict.get('value')),
            message=cast(Optional[str], sr_dict.get('message')),
            databook_name=cast(Optional[str | int],
                               sr_dict.get('databook_name')),
            table_name=cast(Optional[str | int], sr_dict.get('table_name')),
        )
