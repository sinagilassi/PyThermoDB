"""Validate generated YAML as a pyThermoDB custom reference.

Usage:
    python check_reference.py path/to/reference.yml CUSTOM-REF-1 table-1 table-2
"""

# import libs
import argparse
from typing import Any, Dict, List
import logging
from pathlib import Path
import sys
from rich import print


def _ensure_local_project_imports() -> None:
    for candidate in [Path.cwd(), Path(__file__).resolve().parents[3]]:
        if (candidate / "pyThermoDB").is_dir():
            candidate_text = str(candidate)
            if candidate_text not in sys.path:
                sys.path.insert(0, candidate_text)
            return


_ensure_local_project_imports()

import pyThermoDB as ptdb
from pyThermoDB.references import check_custom_reference
from pyThermoDB.core import TableData, TableEquation


# NOTE: logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SECTION: Check reference content


def validate_pythermodb_yaml_reference_content(
        yaml_content: str,
) -> bool:
    """
    Validate the pythermodb YAML content can be used as a reference in pyThermoDB.

    Parameters
    ----------
    yaml_content : str
        The YAML content to be checked as a reference.

    Returns
    -------
    bool
        True if the YAML content can be used as a reference. False otherwise.
    """
    try:
        # NOTE: custom ref
        custom_reference: Dict[str, Any] = {'reference': [yaml_content]}

        # NOTE: check custom reference
        if not check_custom_reference(custom_reference):
            logger.error("The YAML content cannot be used as a reference.")
            return False

        return True
    except Exception as e:
        logger.error(
            f"An error occurred while checking the YAML reference: {e}")
        return False


def check_yaml_reference_tables(
        yaml_content: str,
        databook_name: str,
        table_names: List[str]
) -> bool:
    """
    Check if the YAML content can be used as a reference in pyThermoDB, then check if the specified databook and tables exist in the database.

    Parameters
    ----------
    yaml_content : str
        The YAML content to be checked as a reference.
    databook_name : str
        The name of the databook to check for.
    table_names : List[str]
        A list of table names to check for in the specified databook.

    Returns
    -------
    bool
        True if the YAML content can be used as a reference and the specified databook and tables exist, False otherwise.
    """
    try:
        # NOTE: custom ref
        custom_reference: Dict[str, Any] = {'reference': [yaml_content]}

        # initialization of thermo_db with custom reference
        thermo_db = ptdb.init(custom_reference=custom_reference)

        # NOTE: list databooks
        db_list = thermo_db.list_databooks(res_format='list')
        # >> check if databook name is in the list
        if databook_name not in db_list:
            print(f"Databook {databook_name} not found in the database.")
            return False

        # NOTE: table list
        tb_list = thermo_db.list_table_names(databook_name)

        # >> check
        if len(tb_list) == 0:
            print(f"No tables found in databook {databook_name}.")
            return False

        # NOTE: check if table names are in the list
        for table_name in table_names:
            if table_name not in tb_list:
                print(
                    f"Table {table_name} not found in databook {databook_name}.")
                return False

        return True
    except Exception as e:
        logger.error(
            f"An error occurred while checking the YAML reference: {e}")
        return False


logger = logging.getLogger(__name__)


def check_yaml_reference(
    yaml_content: str,
    databook_name: str,
    table_names: List[str],
    strict_table_type: bool = True,
) -> Dict[str, Any]:
    """
    Validate generated YAML reference content for PyThermoDB.

    Returns a report instead of only True/False.

    Parameters
    ----------
    yaml_content : str
        a string containing the YAML content to be validated as a reference for PyThermoDB.
    databook_name : str
        the name of the databook to check for in the reference.
    table_names : List[str]
        a list of table names to check for in the specified databook.
    strict_table_type : bool, optional
        if True, also check the type of the table objects (data or equation), by default True.

    Returns
    -------
    Dict[str, Any]
        a report dictionary containing the results of the validation, including:
    """

    report = {
        "ok": False,
        "databook_found": False,
        "tables_found": [],
        "tables_missing": [],
        "table_types": {},
        "errors": [],
    }

    try:
        custom_reference: Dict[str, Any] = {"reference": [yaml_content]}
        thermo_db = ptdb.init(custom_reference=custom_reference)

        db_list = thermo_db.list_databooks(res_format="list")

        if databook_name not in db_list:
            report["errors"].append(f"Databook not found: {databook_name}")
            return report

        report["databook_found"] = True

        tb_list = thermo_db.list_table_names(databook_name)

        for table_name in table_names:
            if table_name not in tb_list:
                report["tables_missing"].append(table_name)
                continue

            report["tables_found"].append(table_name)

            if strict_table_type:
                table_obj = thermo_db.get_table(databook_name, table_name)

                if isinstance(table_obj, TableData):
                    report["table_types"][table_name] = "data"
                elif isinstance(table_obj, TableEquation):
                    report["table_types"][table_name] = "equation"
                elif isinstance(table_obj, dict):
                    table_type = table_obj.get("table_type")
                    if table_type == "data":
                        report["table_types"][table_name] = "data"
                    elif table_type in {"equation", "equations"}:
                        report["table_types"][table_name] = "equation"
                    elif table_type:
                        report["table_types"][table_name] = str(table_type)
                    elif table_obj.get("DATA") or table_obj.get("data"):
                        report["table_types"][table_name] = "data"
                    elif table_obj.get("EQUATIONS") or table_obj.get("equations"):
                        report["table_types"][table_name] = "equation"
                    else:
                        report["table_types"][table_name] = "dict"
                        report["errors"].append(
                            f"Could not infer table type for {table_name} from table dictionary."
                        )
                else:
                    report["table_types"][table_name] = type(
                        table_obj).__name__
                    report["errors"].append(
                        f"Unknown table object type for {table_name}: {type(table_obj)}"
                    )

        if report["tables_missing"]:
            report["errors"].append(
                f"Missing tables: {report['tables_missing']}"
            )

        report["ok"] = (
            report["databook_found"]
            and not report["tables_missing"]
            and not report["errors"]
        )

        return report

    except Exception as e:
        logger.exception("Failed to validate YAML reference.")
        report["errors"].append(str(e))
        return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate YAML content as a pyThermoDB custom reference."
    )
    parser.add_argument("path", help="Path to a pyThermoDB reference YAML file.")
    parser.add_argument("databook", help="Databook name, e.g. CUSTOM-REF-1.")
    parser.add_argument(
        "tables",
        nargs="+",
        help="One or more table names expected in the databook.",
    )
    parser.add_argument(
        "--no-strict-table-type",
        action="store_true",
        help="Skip table object type checks after table existence is confirmed.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    yaml_content = Path(args.path).read_text(encoding="utf-8")
    report = check_yaml_reference(
        yaml_content=yaml_content,
        databook_name=args.databook,
        table_names=args.tables,
        strict_table_type=not args.no_strict_table_type,
    )
    print(report)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
