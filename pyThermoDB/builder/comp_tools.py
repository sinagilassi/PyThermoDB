# import libs
import logging
from typing import List, Dict, Any, Optional
# local
from pyThermoDB.core import TableEquation, TableData
from ..references.symbols_controller import SymbolController

# NOTE: logger
logger = logging.getLogger(__name__)


class CompTools:
    """
    Component Tools for handling thermodynamic data and functions (equations).
    """

    def __init__(self):
        # LINK: Initialize SymbolController
        self.symbol_controller = SymbolController()

    def get_fn_structure(
            self,
            func: List[TableEquation]
    ):
        try:
            # NOTE: init
            res: Dict[str, Any] = {}

            for fn in func:
                # get info
                db_name = fn.databook_name
                tb_name = fn.table_name
                eq_number = fn.eq_num
                returns = fn.returns
                return_symbols = fn.return_symbols
                return_identifiers = fn.make_identifiers(
                    param_id="return",
                    mode="symbol"
                )
                args = fn.args
                arg_symbols = fn.arg_symbols
                arg_identifiers = fn.make_identifiers(
                    param_id="arg",
                    mode="symbol"
                )
                fn_body = fn.body
                fn_body_integral = fn.body_integral

                # set id
                fn_id = f"{db_name}::{tb_name}"

                # build structure
                res[fn_id] = {
                    "function_numbers": eq_number,
                    "returns": returns,
                    "return_symbols": return_symbols,
                    "return_identifiers": return_identifiers,
                    "args": args,
                    "arg_symbols": arg_symbols,
                    "arg_identifiers": arg_identifiers,
                    "function_body": fn_body,
                    "function_body_integral": fn_body_integral
                }

            return res
        except Exception as e:
            logger.error(f"Error in getting functions' structure: {e}")
            return None

    def get_fn_identifier(
            self,
            func: List[TableEquation]
    ) -> Optional[List[Dict[str, str]]]:
        try:
            res = [
                {
                    f"{fn.databook_name}::{fn.table_name}": fn.make_identifiers(
                        param_id="return",
                        mode="symbol"
                    )[0]
                }
                for fn in func
            ]

            # res
            return res
        except Exception as e:
            logger.error(f"Error in getting functions' identifiers: {e}")
            return None

    def get_data_structure(
            self,
            data: List[TableData]
    ):
        try:
            # NOTE: init
            res: Dict[str, Any] = {}

            for dt in data:
                # get info
                db_name = dt.databook_name
                tb_name = dt.table_name
                prop_names = dt.property_names
                symbols = dt.table_symbols

                # set id
                data_id = f"{db_name}::{tb_name}"

                # build structure
                res[data_id] = {
                    "property_names": prop_names,
                    "symbols": symbols
                }

            return res
        except Exception as e:
            logger.error(f"Error in getting data structure: {e}")
            return None

    def get_data_identifier(
            self,
            data: List[TableData]
    ) -> Optional[List[Dict[str, List[str]]]]:
        try:
            res = [
                {
                    f"{dt.databook_name}::{dt.table_name}": dt.table_symbols
                }
                for dt in data
            ]

            # res
            return res
        except Exception as e:
            logger.error(f"Error in getting data identifiers: {e}")
            return None

    def get_data_id_labels(
            self,
            data: List[TableData]
    ) -> List[Dict[str, str]]:
        '''
        Get all available symbol labels

        Parameters
        ----------
        data : List[TableData]
            List of TableData objects to extract symbols from.

        Returns
        -------
        List[Dict[str, str]]
            A list of dictionaries containing symbol and their labels.
        '''
        try:
            # SECTION: get TableData symbols
            symbols = self.get_data_identifier(data)
            if not symbols:
                return []

            # SECTION: find labels using SymbolController
            res: List[Dict[str, str]] = []

            for symbol_dict in symbols:
                for symbol_list in symbol_dict.values():
                    for symbol in symbol_list:
                        label = self.symbol_controller.map_symbol_to_property_name(
                            symbol)
                        res.append({symbol: label})

            return res
        except Exception as e:
            logger.error(f"Error listing properties: {e}")
            return []
