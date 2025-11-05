# import libs
import logging
from typing import Literal, List
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

    @staticmethod
    def get_variable_range(
        variable_names: List[str],
        symbol_names: List[str],
        range_suffix_brackets: List[str] = ["[@]", "(@)", "{@}", "@"],
        range_names: List[str] = ["min", "max", "low", "high"],
    ) -> dict[str, List[str]]:
        """
        Create a dictionary of variable range names based on the specified bracket type.

        Parameters
        ----------
        variable_names : List[str]
            The list of variable names to create range names for.
        symbol_names : List[str]
            The list of symbol names associated with the variables.
        range_suffix_brackets : List[str]
            The type of brackets to use for the range suffix.
        range_names : List[str]
            The list of range names to append the suffix to.

        Returns
        -------
        Dict[str, List[str]]
            A dictionary with variable names as keys and lists of available range names as values.
        """
        try:
            # SECTION: create variable range names with respect to bracket type
            variable_range_names = {}

            # determine suffix based on bracket type
            for var in variable_names:
                # create
                variable_range_names[var] = []
                # create range names
                for range_name in range_names:
                    # iterate bracket types
                    for range_suffix_bracket in range_suffix_brackets:
                        if range_suffix_bracket == "[@]":
                            range_name_full = f"{var}[{range_name}]"
                        elif range_suffix_bracket == "(@)":
                            range_name_full = f"{var}({range_name})"
                        elif range_suffix_bracket == "{@}":
                            range_name_full = f"{var}{{{range_name}}}"
                        elif range_suffix_bracket == "@":
                            range_name_full = f"{var}{range_name}"
                        else:
                            logger.warning(
                                "Invalid range suffix bracket type!"
                            )
                            continue

                        variable_range_names[var].append(range_name_full)

            # SECTION: check if variable range names exist in symbol names
            available_variable_ranges = {}

            # >> iterate through variable range names
            for var, range_names_list in variable_range_names.items():
                # create var key
                available_variable_ranges[var] = []

                # >> iterate through range names
                for range_name in range_names_list:
                    if range_name in symbol_names:
                        available_variable_ranges[var].append(range_name)

            return available_variable_ranges

        except Exception as e:
            logger.error(f"Error creating variable range names: {e}")
            return {}
