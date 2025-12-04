# import libs
import logging
import yaml
import os
from rich import print
from typing import Optional, Literal, Dict
from yaml import SafeLoader as Loader, SafeDumper
import time


# NOTE: logger setup
logger = logging.getLogger(__name__)


# --- Flow-style list & quoted string machinery ---
class FlowList(list):
    """A list that will be dumped in YAML flow style."""
    pass


class QuotedStr(str):
    """A string that will always be dumped with double quotes."""
    pass


def flow_representer(dumper, data):
    return dumper.represent_sequence(
        'tag:yaml.org,2002:seq',
        data,
        flow_style=True,
    )


def quoted_representer(dumper, data):
    return dumper.represent_scalar(
        'tag:yaml.org,2002:str',
        data,
        style='"',
    )


# Custom Dumper class to prevent line wrapping in flow sequences
class CustomSafeDumper(SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, indentless)


CustomSafeDumper.best_width = 999999

# Register representer on CustomSafeDumper
CustomSafeDumper.add_representer(FlowList, flow_representer)
CustomSafeDumper.add_representer(QuotedStr, quoted_representer)


def filter_yaml_for_component(
    component: str,
    *,
    match_by: Literal["name", "formula", "state", "auto"] = "auto",
    input_path: Optional[str] = None,
    yaml_text: Optional[str] = None,
    output_path: Optional[str] = None,
    verbose: bool = False,
) -> Optional[bool | str | tuple[Optional[str], Dict[str, bool]]]:
    try:
        # SECTION: verbose config
        if verbose:
            # start time
            start_time = time.time()

        # SECTION: extraction records
        extraction_records: Dict[str, bool] = {}

        # NOTE: Validate inputs
        if (
            input_path is None and
            yaml_text is None
        ) or (
            input_path is not None and
            yaml_text is not None
        ):
            logger.error(
                "Either input_path or yaml_text must be provided, but not both.")
            return None

        search_value = component.strip()
        search_lower = search_value.lower()

        # Normalize source
        if input_path is not None:
            with open(input_path, "r", encoding="utf-8") as f:
                source_text = f.read()
        else:
            if yaml_text is None:
                logger.error(
                    "yaml_text is None while input_path is also None.")
                return None
            source_text = yaml_text

        data = yaml.load(source_text, Loader=Loader)
        if data is None:
            logger.error("YAML data is empty or could not be parsed.")
            return None
        if not isinstance(data, dict):
            logger.error("Expected top-level YAML structure to be a mapping.")
            return None
        if "REFERENCES" not in data or not isinstance(data["REFERENCES"], dict):
            logger.error(
                "YAML data does not contain a valid 'REFERENCES' section.")
            return None

        new_data = {"REFERENCES": {}}

        def classify_column(col_label: str) -> Optional[str]:
            label = col_label.strip().lower()
            if label == "name":
                return "name"
            if "formula" in label:
                return "formula"
            if "cas" in label:
                return "cas"
            if "state" in label:
                return "state"
            return None

        for ref_name, ref in data["REFERENCES"].items():
            if not isinstance(ref, dict):
                new_data["REFERENCES"][ref_name] = ref
                continue

            tables = ref.get("TABLES")
            if not isinstance(tables, dict):
                new_data["REFERENCES"][ref_name] = ref
                continue

            new_tables = {}

            for table_name, table in tables.items():
                # ! init extraction record
                extraction_records[table_name] = False

                if not isinstance(table, dict):
                    new_tables[table_name] = table
                    continue

                values = table.get("VALUES")
                struct = table.get("STRUCTURE")

                if not values or not isinstance(values, list):
                    new_tables[table_name] = table
                    continue

                col_indices: dict[str, int] = {}
                if isinstance(struct, dict):
                    cols = struct.get("COLUMNS")
                    if isinstance(cols, list):
                        for i, col in enumerate(cols):
                            if isinstance(col, str):
                                kind = classify_column(col)
                                if kind is not None and kind not in col_indices:
                                    col_indices[kind] = i

                if match_by == "auto":
                    lookup_order = ["name", "formula", "state"]
                else:
                    lookup_order = [match_by]

                chosen_idx = None
                for key in lookup_order:
                    if key in col_indices:
                        chosen_idx = col_indices[key]
                        break

                if chosen_idx is None:
                    new_tables[table_name] = table
                    continue

                row = next(
                    (
                        row
                        for row in values
                        if isinstance(row, (list, tuple))
                        and len(row) > chosen_idx
                        and isinstance(row[chosen_idx], str)
                        and row[chosen_idx].strip().lower() == search_lower
                    ),
                    None,
                )

                if row is not None:
                    # Make a mutable copy of the row
                    qrow = list(row)

                    # Quote Name, Formula, State, CAS if indices known
                    name_idx = col_indices.get("name")
                    formula_idx = col_indices.get("formula")
                    state_idx = col_indices.get("state")
                    cas_idx = col_indices.get("cas")

                    for idx in (name_idx, formula_idx, state_idx, cas_idx):
                        if idx is not None and idx < len(qrow) and isinstance(qrow[idx], str):
                            qrow[idx] = QuotedStr(qrow[idx])

                    new_table = dict(table)
                    new_table["VALUES"] = [FlowList(qrow)]

                    # Convert STRUCTURE lists to flow style
                    if "STRUCTURE" in new_table and isinstance(new_table["STRUCTURE"], dict):
                        struct = new_table["STRUCTURE"]
                        new_struct = dict(struct)
                        for key in ["COLUMNS", "SYMBOL", "UNIT", "CONVERSION"]:
                            if key in new_struct and isinstance(new_struct[key], list):
                                new_struct[key] = FlowList(new_struct[key])
                        new_table["STRUCTURE"] = new_struct

                    new_tables[table_name] = new_table

                    # ! upd extraction records
                    extraction_records[table_name] = True
                # Skip table if component not found (don't add it to new_tables)

            # Only add reference if it has tables with data
            if new_tables:
                new_ref = dict(ref)
                new_ref["TABLES"] = new_tables
                new_data["REFERENCES"][ref_name] = new_ref

        # SECTION: verbose output
        if verbose:
            # end time
            end_time = time.time()

            # total time taken
            total_time = end_time - start_time
            print(
                f"Time taken: {total_time:.2f} seconds to filter component '{component}'")

        # SECTION: check if component was found
        if not new_data["REFERENCES"]:
            logger.warning(
                f"Component '{component}' not found in any reference.")
            if output_path is not None:
                return False
            return None, extraction_records

        # SECTION: output to file if output_path provided
        if output_path is not None:
            try:
                # ensure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                with open(output_path, "w", encoding="utf-8") as f:
                    yaml.dump(
                        new_data,
                        f,
                        Dumper=CustomSafeDumper,
                        sort_keys=False,
                        allow_unicode=True,
                        width=999999,
                    )

                return True
            except Exception as e:
                logger.error(f"Error writing filtered YAML to file: {e}")
                # res
                return False

        # SECTION: return YAML text
        try:
            res = yaml.dump(
                new_data,
                Dumper=CustomSafeDumper,
                sort_keys=False,
                allow_unicode=True,
                width=999999,
            )
            # res
            return res, extraction_records
        except Exception as e:
            logger.error(f"Error dumping YAML to string: {e}")
            return None, extraction_records
    except Exception as e:
        logger.error(f"Error in filter_yaml_for_component: {e}")
        return None
