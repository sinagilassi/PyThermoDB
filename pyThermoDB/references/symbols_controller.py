# import libs
import logging
import yaml
import os
from typing import Dict, Any, Optional, List
# locals

# NOTE: logger
logger = logging.getLogger(__name__)


class SymbolController:

    def __init__(self) -> None:
        '''
        Initialize the SymbolController

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        # SECTION
        self.symbols_reference = self.load_symbols_reference()

        # NOTE: symbols
        self.symbols = self.list_symbols()
        # NOTE: properties
        self.properties = self.list_properties()

    def load_symbols_reference(self) -> dict:
        '''
        Load symbols used in the databooks

        Parameters
        ----------
        None

        Returns
        -------
        symbols : list
            list of symbols
        '''
        try:
            # current dir
            current_path = os.path.join(os.path.dirname(__file__))

            # Go back to the parent directory (pyThermoDB)
            parent_path = os.path.abspath(os.path.join(current_path, '..'))

            # Now navigate to the data folder
            data_path = os.path.join(parent_path, 'config')

            # relative
            config_path = os.path.join(data_path, 'symbols.yml')

            with open(config_path, 'r') as f:
                symbols = yaml.safe_load(f)

            # return
            return symbols['SYMBOLS']
        except Exception as e:
            raise Exception(f"symbol loading error! {e}")

    def list_symbols(self) -> List[str]:
        '''
        List all available symbols

        Parameters
        ----------
        None

        Returns
        -------
        symbols : list
            list of symbols
        '''
        try:
            if not self.symbols_reference:
                self.symbols_reference = self.load_symbols_reference()

            # check empty
            if not self.symbols_reference:
                logger.warning("No symbol reference found!")
                return []

            return list(self.symbols_reference.values())

        except Exception as e:
            logger.error(f"Error listing symbols: {e}")
            return []

    def list_properties(self) -> List[str]:
        '''
        List all available properties

        Parameters
        ----------
        None

        Returns
        -------
        properties : list
            list of properties
        '''
        try:
            if not self.symbols_reference:
                self.symbols_reference = self.load_symbols_reference()

            # check empty
            if not self.symbols_reference:
                logger.warning("No symbol reference found!")
                return []

            return list(self.symbols_reference.keys())

        except Exception as e:
            logger.error(f"Error listing properties: {e}")
            return []

    def check_symbols(self, symbols: List[str]) -> bool:
        '''
        Check if a symbol is valid

        Parameters
        ----------
        symbols : List[str]
            The symbol to check.

        Returns
        -------
        bool
            True if the symbol is valid, False otherwise.
        '''
        try:
            # NOTE: check input
            if not isinstance(symbols, list):
                logger.error(
                    "Invalid symbol input. It must be a non-empty string.")
                return False

            if not symbols:
                logger.error("Symbol list is empty.")
                return False

            # NOTE: check in symbols
            # invalid list
            invalid_symbols = [
                symbol for symbol in symbols if symbol not in self.symbols
            ]

            if invalid_symbols:
                raise ValueError(
                    f"Invalid symbols found: {', '.join(invalid_symbols)}"
                )

            return True
        except Exception as e:
            raise Exception(f"Symbol checking error! {e}")
