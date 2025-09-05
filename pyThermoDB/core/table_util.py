# import libs
import logging
from typing import Literal
# locals
from ..models import PropertyMatch

# NOTE: logger
logger = logging.getLogger(__name__)


class TableUtil:
    """
    Utility class for table operations.
    """

    @staticmethod
    def is_symbol_available(symbol: str, table_symbols: list):
        '''
        Check if a symbol is available in the table data.

        Parameters
        ----------
        symbol : str
            Symbol to check.

        Returns
        -------
        bool
            True if the symbol is available, False otherwise.
        '''
        try:
            # NOTE: check if table symbols exist
            if not table_symbols:
                logger.warning("No table symbols found!")
                return PropertyMatch(
                    prop_id=symbol,
                    availability=False,
                    search_mode='SYMBOL'
                )

            # NOTE: check inputs
            if not isinstance(symbol, str):
                logger.error("Invalid symbol input! Symbol must be a string.")
                return PropertyMatch(
                    prop_id=symbol,
                    availability=False,
                    search_mode='SYMBOL'
                )

            # NOTE: get symbols
            symbols = table_symbols

            # SECTION: check if symbol exists (case-sensitive)
            # NOTE: normalized to lower case
            symbols_lower = [s.lower() for s in symbols]

            # check
            search_res = symbol.lower().strip() in symbols_lower

            return PropertyMatch(
                prop_id=symbol,
                availability=search_res,
                search_mode='SYMBOL'
            )
        except Exception as e:
            logger.error(f"Error checking symbol availability: {e}")
            return PropertyMatch(
                prop_id=symbol,
                availability=False,
                search_mode='SYMBOL',
            )

    @staticmethod
    def is_column_name_available(
        column_name: str,
        table_columns: list
    ) -> PropertyMatch:
        '''
        Check if a column name is available in the table data.

        Parameters
        ----------
        column_name : str
            Column name to check.

        Returns
        -------
        bool
            True if the column name is available, False otherwise.
        '''
        try:
            # NOTE: check if table columns exist
            if not table_columns:
                logger.warning("No table columns found!")
                return PropertyMatch(
                    prop_id=column_name,
                    availability=False,
                    search_mode='COLUMN'
                )

            # NOTE: check inputs
            if not isinstance(column_name, str):
                logger.error(
                    "Invalid column name input! Column name must be a string.")
                return PropertyMatch(
                    prop_id=column_name,
                    availability=False,
                    search_mode='COLUMN'
                )

            # NOTE: get column names
            column_names = table_columns

            # SECTION: check if column exists (case-sensitive)
            # NOTE: normalized to lower case
            column_names_lower = [c.lower() for c in column_names]

            # check
            search_res = column_name.lower().strip() in column_names_lower

            # return
            return PropertyMatch(
                prop_id=column_name,
                availability=search_res,
                search_mode='COLUMN'
            )
        except Exception as e:
            logger.error(f"Error checking column name availability: {e}")
            return PropertyMatch(
                prop_id=column_name,
                availability=False,
                search_mode='COLUMN',
            )
