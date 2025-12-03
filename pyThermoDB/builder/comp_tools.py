# import libs
import logging
from typing import List, Dict, Any
# local
from pyThermoDB.core import TableEquation, TableData

# NOTE: logger
logger = logging.getLogger(__name__)


class CompTools:
    """
    Component Tools for handling thermodynamic data and functions (equations).
    """

    def __init__(self):
        pass

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
                args = fn.args
                arg_symbols = fn.arg_symbols
                fn_body = fn.body
                fn_body_integral = fn.body_integral

                # set id
                fn_id = f"{db_name}::{tb_name}"

                # build structure
                res[fn_id] = {
                    "function_numbers": eq_number,
                    "returns": returns,
                    "return_symbols": return_symbols,
                    "args": args,
                    "arg_symbols": arg_symbols,
                    "function_body": fn_body,
                    "function_body_integral": fn_body_integral
                }

            return res
        except Exception as e:
            logger.error(f"Error in getting functions' structure: {e}")
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
