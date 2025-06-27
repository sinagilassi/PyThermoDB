# import libs
import yaml
import json
import re
import logging
# local


class Convertor:
    """Convertor class for converting different data types."""
    # NOTE: attributes

    def __init__(self):
        """Initialize the Convertor class."""
        pass

    def which_format(self, data: str) -> str:
        """
        Determine the format of the input string.

        Parameters:
            data (str): The input string.

        Returns:
            str: Format of the input string ('yaml', 'json', or 'markdown').
        """
        # SECTION: Robust Markdown detection with regex
        markdown_patterns = [
            r'^#{1,6} ',                # Headers (#, ##, ###, etc.)
            # r'^\*{1,2}[^*]+\*{1,2}',    # Bold or italic
            # r'^- ',                    # Unordered list
            # r'^\d+\.',                 # Ordered list
            # r'^> ',                    # Blockquote
            # r'`{1,3}[^`]+`{1,3}',      # Inline or fenced code
            # r'\[.*\]\(.*\)',           # Links
            # r'!\[.*\]\(.*\)',          # Images
            # r'^---$',                  # Horizontal rule
        ]

        for pattern in markdown_patterns:
            if re.search(pattern, data, re.MULTILINE):
                return "markdown"

        # # SECTION: Try JSON
        try:
            json.loads(data)
            return "json"
        except (json.JSONDecodeError, TypeError):
            pass

        # # SECTION: Try YAML (note: YAML can parse JSON too, so test JSON first)
        try:
            yaml.safe_load(data)
            return "yaml"
        except yaml.YAMLError:
            pass

        # Default fallback
        return "unknown"

    def str_to_dict(self, data: str, format: str) -> dict:
        """
        Convert a string in YAML or JSON format to a Python dictionary.

        Parameters
        ----------
        data : str
            The input string containing data in YAML or JSON format.

        Returns
        -------
        dict
            The converted data as a Python dictionary.
        """
        # SECTION: convert
        normalized_format = format.lower()

        # NOTE: We assume that the input data is already in a valid format
        try:
            if normalized_format == "yaml":
                return yaml.safe_load(data)
            elif normalized_format == "json":
                return json.loads(data)
            else:
                logging.error(f"Unsupported format: {format}")
                raise ValueError(f"Unsupported format: {format}")
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            # The original format string is used in the error for better user feedback
            logging.error(f"Error parsing {format} data: {e}")
            raise ValueError(f"Invalid {format} data") from e

    # def md_to_dict(self, data: str) -> dict:
    #     """
    #     Convert a Markdown string to a Python dictionary.

    #     Parameters
    #     ----------
    #     data : str
    #         The input Markdown string.

    #     Returns
    #     -------
    #     dict
    #         The converted data as a Python dictionary.
    #     """
    #     try:
    #         lines = data.strip().splitlines()
    #         config = {}
    #         current_comp = None
    #         current_section = None
    #         i = 0

    #         while i < len(lines):
    #             line = lines[i].strip()

    #             if line.startswith("## "):
    #                 current_comp = line[3:].strip()
    #                 config[current_comp] = {}
    #                 i += 1

    #             elif line.endswith(":") and not line.startswith("-"):
    #                 current_section = line[:-1].strip()
    #                 config[current_comp][current_section] = {}
    #                 i += 1

    #                 while i < len(lines) and lines[i].strip() == "":
    #                     i += 1

    #                 while i < len(lines):
    #                     subline = lines[i]
    #                     stripped = subline.strip()

    #                     if not stripped or stripped.startswith("##") or (not stripped.startswith("-") and stripped.endswith(":")):
    #                         break

    #                     if stripped.startswith("- "):
    #                         item = stripped[2:]
    #                         if item.endswith(":"):
    #                             nested_key = item[:-1].strip()
    #                             config[current_comp][current_section][nested_key] = {}
    #                             i += 1
    #                             while i < len(lines) and lines[i].startswith("  - "):
    #                                 subitem_line = lines[i].strip()[2:]
    #                                 if ":" in subitem_line:
    #                                     subkey, subval = map(
    #                                         str.strip, subitem_line.split(":", 1))
    #                                     config[current_comp][current_section][nested_key][subkey] = subval
    #                                 i += 1
    #                         elif ":" in item:
    #                             key, val = map(str.strip, item.split(":", 1))
    #                             config[current_comp][current_section][key] = val
    #                             i += 1
    #                         else:
    #                             i += 1
    #                     else:
    #                         i += 1
    #             else:
    #                 i += 1

    #         return config
    #     except Exception as e:
    #         logging.error(f"Error converting Markdown to dict: {e}")
    #         return {}
