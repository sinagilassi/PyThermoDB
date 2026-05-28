# import libs
import logging
from typing import List, Dict, Any, Optional
# local
from pyThermoDB.core import (
    TableConstants,
    TableData,
    TableEquation,
    TableMatrixData,
    TableMatrixEquation
)
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

    def get_constants_structure(
            self,
            constants: List[TableConstants]
    ):
        try:
            res: Dict[str, Any] = {}

            for const in constants:
                const_id = f"{const.databook_name}::{const.table_name}"
                data = const.data_structure()
                names = (
                    data['Name'].dropna().astype(str).tolist()
                    if 'Name' in data.columns else []
                )
                symbols = (
                    data['Symbol'].dropna().astype(str).tolist()
                    if 'Symbol' in data.columns else []
                )

                res[const_id] = {
                    "columns": const.table_columns,
                    "names": names,
                    "symbols": symbols
                }

            return res
        except Exception as e:
            logger.error(f"Error in getting constants structure: {e}")
            return None

    def get_constants_identifier(
            self,
            constants: List[TableConstants]
    ) -> Optional[List[Dict[str, List[str]]]]:
        try:
            res = []

            for const in constants:
                data = const.data_structure()
                symbols = (
                    data['Symbol'].dropna().astype(str).tolist()
                    if 'Symbol' in data.columns else []
                )
                res.append({
                    f"{const.databook_name}::{const.table_name}": symbols
                })

            return res
        except Exception as e:
            logger.error(f"Error in getting constants identifiers: {e}")
            return None

    def get_constants_id_labels(
            self,
            constants: List[TableConstants]
    ) -> List[Dict[str, str]]:
        try:
            res: List[Dict[str, str]] = []

            for const in constants:
                data = const.data_structure()
                if 'Symbol' not in data.columns:
                    continue

                for _, row in data.iterrows():
                    symbol = row.get('Symbol')
                    if symbol is None:
                        continue
                    label = row.get('Name', symbol)
                    res.append({str(symbol): str(label)})

            return res
        except Exception as e:
            logger.error(f"Error listing constants: {e}")
            return []

    def get_matrix_data_structure(
            self,
            data: List[TableMatrixData]
    ):
        try:
            res: Dict[str, Any] = {}

            for dt in data:
                data_id = f"{dt.databook_name}::{dt.table_name}"
                res[data_id] = {
                    "matrix_symbol": dt.matrix_symbol,
                    "matrix_mode": dt.matrix_mode,
                    "matrix_item_keys": dt.matrix_item_keys,
                    "table_structure": dt.table_structure
                }

            return res
        except Exception as e:
            logger.error(f"Error in getting matrix data structure: {e}")
            return None

    def get_matrix_data_identifier(
            self,
            data: List[TableMatrixData]
    ) -> Optional[List[Dict[str, List[str]]]]:
        try:
            res = [
                {
                    f"{dt.databook_name}::{dt.table_name}": dt.matrix_symbol or []
                }
                for dt in data
            ]

            return res
        except Exception as e:
            logger.error(f"Error in getting matrix data identifiers: {e}")
            return None

    def get_matrix_data_id_labels(
            self,
            data: List[TableMatrixData]
    ) -> List[Dict[str, str]]:
        try:
            symbols = self.get_matrix_data_identifier(data)
            if not symbols:
                return []

            res: List[Dict[str, str]] = []

            for symbol_dict in symbols:
                for symbol_list in symbol_dict.values():
                    for symbol in symbol_list:
                        label = self.symbol_controller.map_symbol_to_property_name(
                            symbol)
                        res.append({symbol: label})

            return res
        except Exception as e:
            logger.error(f"Error listing matrix data properties: {e}")
            return []

    def get_matrix_fn_structure(
            self,
            func: List[TableMatrixEquation]
    ):
        try:
            res: Dict[str, Any] = {}

            for fn in func:
                fn_id = f"{fn.databook_name}::{fn.table_name}"
                res[fn_id] = {
                    "returns": fn.returns,
                    "return_symbols": fn.return_symbols,
                    "args": fn.args,
                    "arg_symbols": fn.arg_symbols,
                    "function_body": fn.body,
                    "function_body_integral": fn.body_integral,
                    "function_body_first_derivative": fn.body_first_derivative,
                    "function_body_second_derivative": fn.body_second_derivative,
                    "custom_integral": fn.custom_integral,
                    "matrix_elements": fn.matrix_elements
                }

            return res
        except Exception as e:
            logger.error(f"Error in getting matrix functions' structure: {e}")
            return None

    def get_matrix_fn_identifier(
            self,
            func: List[TableMatrixEquation]
    ) -> Optional[List[Dict[str, List[str]]]]:
        try:
            res: List[Dict[str, List[str]]] = []

            for fn in func:
                identifiers = (
                    list(fn.return_symbols.keys())
                    if isinstance(fn.return_symbols, dict) else []
                )
                res.append({
                    f"{fn.databook_name}::{fn.table_name}": identifiers
                })

            return res
        except Exception as e:
            logger.error(f"Error in getting matrix functions' identifiers: {e}")
            return None
