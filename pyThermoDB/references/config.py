# import libs
from typing import Dict, List, Any, Union, Optional
import logging
# local
from ..utils import Convertor


class ReferenceConfig:
    """
    Configuration for references in pyThermoDB.
    """

    def __init__(self):
        # NOTE: init Convertor
        self.Convertor_ = Convertor()

    def set_reference_config(
        self,
        reference_config: str
    ) -> Dict[str, Any]:
        """
        Convert a string reference config to a dictionary.

        Parameters
        ----------
        reference_config : str
            The reference configuration as a string.

        Returns
        -------
        dict
            The reference configuration as a dictionary.
        """
        try:
            # NOTE: check format
            # SECTION: format check]
            format = self.Convertor_.which_format(reference_config)

            if format == "unknown":
                logging.error(
                    "Unknown format. Please provide data in YAML or JSON format.")
                return {}

            # SECTION: convert
            normalized_format = format.lower()

            # check
            if normalized_format == "markdown":
                # For markdown, we can return a simple dict with the raw data
                return self.md_to_dict(reference_config)
            elif normalized_format in ["yaml", "json"]:
                return self.Convertor_.str_to_dict(
                    reference_config,
                    format=normalized_format
                )
            else:
                logging.error(f"Unsupported format: {format}")
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            raise Exception(f"Error converting reference config: {e}") from e

    def md_to_dict(self, md: str) -> dict:
        lines = md.strip().splitlines()
        config = {}
        current_comp = None
        current_section = None
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if line.startswith("## "):
                current_comp = line[3:].strip()
                config[current_comp] = {}
                i += 1

            elif line.endswith(":") and not line.startswith("-"):
                current_section = line[:-1].strip()
                config[current_comp][current_section] = {}
                i += 1

                while i < len(lines) and lines[i].strip() == "":
                    i += 1

                while i < len(lines):
                    subline = lines[i]
                    stripped = subline.strip()

                    if not stripped or stripped.startswith("##") or (not stripped.startswith("-") and stripped.endswith(":")):
                        break

                    if stripped.startswith("- "):
                        item = stripped[2:]
                        if item.endswith(":"):
                            nested_key = item[:-1].strip()
                            config[current_comp][current_section][nested_key] = {}
                            i += 1
                            while i < len(lines) and lines[i].startswith("  - "):
                                subitem_line = lines[i].strip()[2:]
                                if ":" in subitem_line:
                                    subkey, subval = map(
                                        str.strip, subitem_line.split(":", 1))
                                    config[current_comp][current_section][nested_key][subkey] = subval
                                i += 1
                        elif ":" in item:
                            key, val = map(str.strip, item.split(":", 1))
                            config[current_comp][current_section][key] = val
                            i += 1
                        else:
                            i += 1
                    else:
                        i += 1
            else:
                i += 1

        return config
