# Utils for data handling
# ------------------------
import logging
import pandas as pd
from typing import Optional, Union, List, Dict, Any
# locals
from ..data import TableTypes
from ..models import PayLoadType, Component

# NOTE: logger
logger = logging.getLogger(__name__)


def make_payload(df: pd.DataFrame, table_type: str):
    """
    Make payload from dataframe based on table type.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the table data.
    table_type : str
        Type of the table ('Matrix' or other).
    """
    try:
        # SECTION: check inputs
        if df is None or df.empty:
            logger.warning("DataFrame is None or empty.")
            return None

        # check table type
        validate_table_types = [
            TableTypes.EQUATIONS.value,
            TableTypes.DATA.value,
            TableTypes.MATRIX_EQUATIONS.value,
            TableTypes.MATRIX_DATA.value
        ]

        # validate table type
        if table_type not in validate_table_types:
            logger.warning(
                f"Invalid table type: {table_type}. Must be one of {validate_table_types}.")
            return None

        matrix_tb = table_type in [
            TableTypes.MATRIX_DATA.value, TableTypes.MATRIX_EQUATIONS.value]

        # SECTION: process
        if len(df) > 0:
            # payload
            if matrix_tb:
                records_clean = df.iloc[4, :].fillna(0).to_list()
            else:
                records_clean = df.iloc[2, :].fillna(0).to_list()

            # payload
            payload: PayLoadType = {
                "header": df.columns.to_list(),
                "symbol": df.iloc[0, :].to_list(),
                "unit": df.iloc[1, :].to_list(),
                "records": records_clean,
            }
            return payload
        else:
            logger.warning("DataFrame is empty. Cannot create payload.")
            return None
    except Exception as e:
        logger.error(f"Error creating payload: {e}")
        return None


def is_payload_header_valid(
    header: List[str],
    required_columns: List[str] = [
        'Name', 'Formula', 'State'
    ]
) -> bool:
    """
    Check if the header contains all required columns.

    Parameters
    ----------
    header : List[str]
        List of column names in the header.
    required_columns : List[str]
        List of required column names.

    Returns
    -------
    bool
        True if all required columns are present, False otherwise.
    """
    try:
        # SECTION: check inputs
        if not header or not required_columns:
            logger.warning("Header or required columns list is empty.")
            return False

        # check if all required columns are in header
        for col in required_columns:
            if col not in header:
                logger.info(f"Missing required column: {col}")
                return False
        return True
    except Exception as e:
        logger.error(f"Error checking header validity: {e}")
        return False


def create_component(payload: PayLoadType) -> Component | None:
    """
    Extract component information from payload.

    Parameters
    ----------
    payload : PayLoadType
        Payload containing header and records.

    Returns
    -------
    Component | None
        Component object with name, formula, and state, or None if extraction fails.
    """
    try:
        # SECTION: check inputs
        if not payload or 'header' not in payload or 'records' not in payload:
            logger.warning("Invalid payload structure.")
            return None

        header = payload['header']
        records = payload['records']

        # validate header
        if not is_payload_header_valid(header):
            logger.warning("Payload header is missing required columns.")
            return None

        # extract indices
        name_idx = header.index('Name')
        formula_idx = header.index('Formula')
        state_idx = header.index('State')

        # extract values
        name = records[name_idx] if name_idx < len(records) else None
        formula = records[formula_idx] if formula_idx < len(records) else None
        state = records[state_idx] if state_idx < len(records) else None

        if not name or not formula or not state:
            logger.warning("Missing component information in records.")
            return None

        # create Component object
        component = Component(
            name=str(name).strip(),
            formula=str(formula).strip(),
            state=str(state).strip().lower()
        )
        return component
    except Exception as e:
        logger.error(f"Error extracting component from payload: {e}")
        return None
