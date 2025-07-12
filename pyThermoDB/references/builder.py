# import libs
import logging
import os
import csv
from io import StringIO
import re
from typing import (
    Union,
    Dict,
    Any,
    List,
    Optional
)
from pathlib import Path
# locals


class TableBuilder:
    """
    TableBuilder class serves as a base class for building tables in the pyThermoDB package.
    """
    # NOTE: attributes
    # data table

    def __init__(self):
        # NOTE: set
        # tables
        pass

    @staticmethod
    def load_csv(csv_data: Union[str, Path]) -> str:
        """
        Load data from a CSV string.

        Parameters
        ----------
        csv_data : Union[str, Path]
            The CSV data as a string or a path to a CSV file.

        Returns
        -------
        str
            The loaded CSV data as a string.
        """
        try:
            # check if csv_data is a Path object or a string
            if isinstance(csv_data, Path):
                # read the CSV file
                csv_data = csv_data.read_text(encoding="utf-8-sig").strip()
            elif isinstance(csv_data, str):
                # check if csv_data is a path directory
                if os.path.exists(csv_data):
                    # read the CSV file with utf-8-sig to remove BOM if present
                    csv_data = Path(csv_data).read_text(
                        encoding="utf-8-sig"
                    ).strip()
                else:
                    # strip any leading or trailing whitespace
                    csv_data = csv_data.strip()
            else:
                raise ValueError("csv_data must be a string or a Path object.")

            # return the loaded CSV data
            return csv_data
        except Exception as e:
            logging.error(f"Error loading CSV data: {e}")
            raise ValueError("Failed to load CSV data.") from e

    @staticmethod
    def extract_csv_data(
        csv_data: str,
        column_names: List[str] = [
            "No.", "Name", "Formula", "State"
        ]
    ) -> List[List[str]]:
        """
        Extract the CSV data format.

        Parameters
        ----------
        csv_data : str
            The CSV data as a string.

        Returns
        -------
        List[List[str]]
            A list of lists, where each inner list represents a row of data.
        """
        try:
            # check if the CSV data is not empty
            if not csv_data.strip():
                return []

            # Use csv.reader to handle quoted fields
            reader = csv.reader(StringIO(csv_data.strip()))
            lines = list(reader)

            # NOTE: check if there are at least 4 lines (header, symbols, units, data[0])
            if len(lines) < 4:
                logging.error(
                    "CSV data must contain at least 4 lines (header, symbols, units, data[0]).")
                return []

            # NOTE: check all lines have the same number of columns
            num_columns = len(lines[0])

            # NOTE: check if the first line contains the column names
            header = lines[0]

            # if column_names is provided, check if all required columns are present
            if column_names and isinstance(column_names, list):
                # check if all required columns are present in the header
                if not header:
                    logging.error("CSV data must contain a header line.")
                    return []

                # check if all required columns are present in the header
                if len(column_names) > 0 and header:
                    # check if all required columns are present
                    for col in column_names:
                        if col not in header:
                            logging.error(
                                f"Column '{col}' is missing in the CSV data.")
                            return []

            # SECTION: data lines
            data_lines = []

            # iterate through each line and check the number of columns
            for i, split_line in enumerate(lines):
                if any(field.strip() for field in split_line):  # skip empty lines
                    if len(split_line) != num_columns:
                        logging.error(
                            f"All lines in the CSV data must have the same number of columns, check line {i + 1}."
                        )
                        return []
                    data_lines.append(split_line)

            return data_lines
        except Exception as e:
            logging.error(f"Error validating CSV data: {e}")
            return []

    @staticmethod
    def convert_function_equation_v2(
        equation: str,
        columns: List[str],
        symbols: List[str],
        units: List[str]
    ) -> List[str]:
        """
        Convert extended function-like equation body to target format.

        Extended format:
        f([res_name, res_sym, res_unit] | [arg1_name, arg1_sym, arg1_unit], ... | param1, param2, ...) = expression

        Parameters
        ----------
        equation : str
            Equation string in extended format.
        columns : list of str
            List of all parameter names (for metadata lookup).
        symbols : list of str
            Corresponding symbols for each column.
        units : list of str
            Corresponding units for each column.

        Returns
        -------
        list of str
            Converted body as list of strings.
        """
        body_lines = []
        parms_lines = []

        # Split header and expression
        header, expression = equation.split("=", 1)
        header_match = re.search(r"f\((.*?)\)", header.strip())
        if not header_match:
            raise ValueError("Equation header format is invalid")
        header_content = header_match.group(1)

        # Split into result | arguments | parameters
        parts = [part.strip() for part in header_content.split("|")]
        if len(parts) != 3:
            raise ValueError(
                "Expected 3 sections: result | arguments | parameters")

        # Parse result block
        res_parts = re.findall(r"\[([^\[\]]+)\]", parts[0])[0].split(",")
        res_name, res_sym, res_unit = [p.strip() for p in res_parts]
        res_key = f"{res_name} | {res_sym} | {res_unit}"

        # Parse argument blocks
        args_list = []
        arg_blocks = re.findall(r"\[([^\[\]]+)\]", parts[1])
        for arg_entry in arg_blocks:
            name, sym, unit = [p.strip() for p in arg_entry.split(",")]
            key = f"{name} | {sym} | {unit}"
            args_list.append((sym, f"args['{key}']"))

        # Parse parameter list
        parms_list = []
        for param in parts[2].split(","):
            param = param.strip()
            if param:
                if param in columns:
                    idx = columns.index(param)
                    sym = symbols[idx]
                    unit = units[idx]
                    key = f"{param} | {sym} | {unit}"
                    parms_list.append((param, f"parms['{key}']"))
                    parms_lines.append(
                        f"parms['{key}'] = parms['{key}']/{unit}")
                else:
                    raise ValueError(
                        f"Parameter '{param}' not found in columns")

        # Replace variables in expression
        def replace_var(match):
            var = match.group(0)
            for sym, repl in parms_list + args_list:
                if var == sym:
                    return repl
            return var  # leave untouched if not found

        converted_expression = re.sub(
            r'\b[A-Za-z_][A-Za-z0-9_]*\b', replace_var, expression.strip())

        # Add result assignment
        result_line = f"res['{res_key}'] = {converted_expression}"

        # Combine lines
        body_lines.extend(parms_lines)
        body_lines.append(result_line)

        return body_lines

    @staticmethod
    def analyze_equation(
        body: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze the equation body to extract metadata.

        Parameters
        ----------
        body : List[str]
            The equation body to analyze.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the metadata extracted from the equation body.
            - returns
            - parms
            - args
        """
        try:
            pass
            results = {"returns": [], "parms": [], "args": []}

            # Patterns for res[], parms[], args[]
            patterns = {
                "returns": r"res\['([^']+)'\]",
                "parms": r"parms\['([^']+)'\]",
                "args": r"args\['([^']+)'\]"
            }

            for key, pattern in patterns.items():
                found = set()  # avoid duplicates
                for line in body:
                    matches = re.findall(pattern, line)
                    for match in matches:
                        if match not in found:
                            parts = [p.strip() for p in match.split("|")]
                            # Pad with None if missing parts
                            while len(parts) < 3:
                                parts.append(None)
                            results[key].append({
                                "name": parts[0],
                                "symbol": parts[1],
                                "unit": parts[2]
                            })

                            # Avoid duplicates
                            found.add(match)

            return results
        except Exception as e:
            logging.error(f"Error analyzing equation: {e}")
            raise ValueError("Failed to analyze equation body.") from e
