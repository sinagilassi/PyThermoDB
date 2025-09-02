# import packages/modules
import logging
import os
import yaml
import re
import ast
from typing import Literal, List

# NOTE: logger
logger = logging.getLogger(__name__)


class CustomRef:
    '''
    Manage new custom references
    '''

    def __init__(self, ref):
        self.ref = ref

        # NOTE: files
        self.src_files: list[str] = []
        self.yml_files: list[str] = []
        self.csv_files: list[str] = []
        self.md_files: list[str] = []

        # NOTE: raw content
        self.contents: List[str | dict] | None = None

        # NOTE: paths
        self.yml_paths: list[str] = []
        self.csv_paths: list[str] = []
        self.md_paths: list[str] = []

        # NOTE: symbols
        self.symbols_files: list[str] = []
        self.symbols_paths: list[str] = []

        # NOTE: data mode
        self.data_mode: Literal['NORMAL', 'VALUES'] = self.set_data_mode()

    def set_data_mode(
        self
    ):
        '''
        Set data mode

        Returns
        -------
        data_mode : str
            data mode, 'NORMAL' or 'VALUES'
        '''
        try:
            # ref keys
            ref_keys = list(self.ref.keys())
            ref_keys = [x.lower() for x in ref_keys]

            # check ref keys [yml, reference, csv, tables, symbols]
            if len(ref_keys) == 0:
                logging.warning("No reference keys found.")
                raise RuntimeError("No reference keys found.")

            # NOTE: check data mode
            # ! only one key is allowed
            if len(ref_keys) == 1:
                # yml or reference
                if 'yml' in ref_keys or 'reference' in ref_keys:
                    # set data mode
                    return 'VALUES'

            # res
            return 'NORMAL'
        except Exception as e:
            raise RuntimeError(f"Setting data mode failed! {e}")

    def init_ref(self) -> bool:
        '''
        Update reference through updating yml

        Parameters
        ----------
        data_mode : str, optional
            data mode, by default 'NORMAL'

        Notes
        ----------
        yml_files : list
            yml files
        csv_files : list
            csv files

        Returns
        -------
        bool
            True if reference is updated, False otherwise
        '''
        try:
            # REVIEW: deprecated reference keys
            if 'yml' in self.ref.keys() or 'md' in self.ref.keys():
                logger.warning(
                    "'yml' key is deprecated, please use 'reference' instead.")

            # SECTION: extract data
            # NOTE: reference
            src_files = self.ref.get('yml') or self.ref.get('md')

            # check
            if src_files is None:
                src_files = self.ref.get('reference')
            # check
            if src_files is None:
                raise Exception("No reference files found.")
            # set
            self.src_files = src_files
            # check type
            if not isinstance(src_files, list):
                raise Exception("Reference files must be a list.")
            if len(src_files) == 0:
                raise Exception("No reference files found.")

            # NOTE: tables
            csv_files = self.ref.get('csv') or self.ref.get('tables') or []
            # NOTE: symbols (optional)
            symbol_files = self.ref.get('symbols') or []

            # SECTION: check files exist
            # NOTE: csv files only for NORMAL mode (yml + csv)
            if len(csv_files) == 0 and self.data_mode == 'NORMAL':
                raise Exception("No csv files to update.")

            # SECTION: extract files from source files
            # NOTE: check file types
            # ! yml files
            yml_files = [x for x in self.src_files if str(x).endswith('.yml')]
            # ! md files
            md_files = [x for x in self.src_files if str(x).endswith('.md')]

            # SECTION: check string format
            # NOTE: if no yml/md files, check content
            # ! only for VALUES mode
            if len(yml_files) == 0 and len(md_files) == 0:
                # get content
                contents_ = self.ref.get('reference')
                # std content
                if isinstance(contents_, list):
                    # check
                    self.contents = self.content_manager(contents_)

            # SECTION: check file path
            # NOTE: yml files
            if len(yml_files) > 0:
                for yml_file in yml_files:
                    if not os.path.exists(yml_file):
                        raise Exception(f"{yml_file} does not exist.")
                    else:
                        # check file ext
                        if yml_file.endswith('.yml'):
                            # get path
                            self.yml_paths.append(os.path.abspath(yml_file))

            # NOTE: md files
            if len(md_files) > 0:
                for md_file in md_files:
                    if not os.path.exists(md_file):
                        raise Exception(f"{md_file} does not exist.")
                    else:
                        # check file ext
                        if md_file.endswith('.md'):
                            # get path
                            self.md_paths.append(os.path.abspath(md_file))

            # SECTION: check
            if self.data_mode == 'NORMAL':
                for csv_file in csv_files:
                    if not os.path.exists(csv_file):
                        raise Exception(f"{csv_file} does not exist.")
                    else:
                        # get path
                        self.csv_paths.append(os.path.abspath(csv_file))

            # NOTE: update vars
            # yml files
            self.yml_files = yml_files
            # md files
            self.md_files = md_files

            # NOTE: check
            if self.data_mode == 'NORMAL':
                self.csv_files = csv_files

            # SECTION: check
            if len(symbol_files) > 0:
                # symbols
                for symbol_file in symbol_files:
                    if not os.path.exists(symbol_file):
                        raise Exception(f"{symbol_file} does not exist.")
                    else:
                        # get path
                        self.symbols_paths.append(os.path.abspath(symbol_file))

                # update vars
                self.symbols_files = symbol_files

            return True
        except Exception as e:
            logger.error(f"updating reference failed! {e}")
            return False

    def load_ref(self) -> dict:
        '''
        Load reference

        Returns
        -------
        ref : dict
            reference
        '''
        try:
            # data
            data = {}

            # SECTION: check yml files
            if len(self.yml_files) > 0:
                # loop through the rest of the files
                for i in range(0, len(self.yml_files)):
                    with open(self.yml_files[i], 'r') as f:
                        # load data
                        temp_data = yaml.load(f, Loader=yaml.FullLoader)
                        # check
                        if temp_data is None:
                            raise Exception(
                                "No data in the file number %d" % i)
                        # merge data
                        data.update(temp_data['REFERENCES'])

            # SECTION: check md files
            if len(self.md_files) > 0:
                # loop through the rest of the files
                for i in range(0, len(self.md_files)):
                    with open(self.md_files[i], 'r', encoding='utf-8') as f:
                        # load data
                        content = f.read()
                        # check
                        if content is None:
                            raise Exception(
                                "No data in the file number %d" % i)

                        # extract data
                        temp_data = self.parse_markdown(content)
                        # merge data
                        data.update(temp_data['REFERENCES'])

            # SECTION: check content
            if self.contents is not None and len(self.contents) > 0:
                # loop through the rest of the files
                for i in range(0, len(self.contents)):
                    # load data
                    content = self.contents[i]
                    # check
                    if content is None:
                        raise Exception(
                            "No data in the file number %d" % i)

                    # NOTE: check if content is a dict
                    if isinstance(content, dict):
                        # ! dict
                        # extract data
                        temp_data = content
                    else:
                        # ! str
                        # ? check content format
                        content_format = self.check_content_format(content)

                        # NOTE: extract data
                        if content_format == 'yml':
                            # ! yml
                            # load data
                            temp_data = yaml.load(
                                content,
                                Loader=yaml.FullLoader
                            )

                            # check
                            if temp_data is None:
                                raise Exception(
                                    "No data in the content number %d" % i)

                        elif content_format == 'markdown':
                            # ! markdown
                            # parse markdown
                            temp_data = self.parse_markdown(content)
                        else:
                            raise Exception(
                                f"Content format {content_format} not recognized.")

                    # NOTE: merge data
                    data.update(temp_data['REFERENCES'])

            # res
            return data
        except Exception as e:
            raise Exception(f"loading reference failed! {e}")

    def load_symbols(self) -> dict:
        '''
        Load symbols

        Returns
        -------
        symbols : dict
            symbols
        '''
        try:
            # data
            data = {}

            # check
            if self.symbols_files is not None:
                # loop through the rest of the files
                for i in range(0, len(self.symbols_files)):
                    with open(self.symbols_files[i], 'r') as f:
                        # load data
                        temp_data = yaml.load(f, Loader=yaml.FullLoader)
                        # check
                        if temp_data is None:
                            raise Exception(
                                "No data in the file number %d" % i)
                        # merge data
                        data.update(temp_data['SYMBOLS'])

            # res
            return data
        except Exception as e:
            raise Exception(f"loading symbols failed! {e}")

    def parse_markdown(self, content: str) -> dict:
        """
        Parse a structured markdown content and extract information.

        Parameters
        ----------
        content : str
            The markdown content to parse.

        Returns
        -------
        dict
            Dictionary containing all the extracted information.
        """
        try:
            # Initialize the result dictionary
            databook_data = {}
            result = {}

            # databook name
            databook_name_match = re.findall(r'## (.*?)(?:\n|$)', content)
            if databook_name_match:
                databook_name_ = databook_name_match[0].strip()
                databook_data[databook_name_] = {}

            # Extract DATABOOK-ID
            databook_match = re.search(r'DATABOOK-ID: (.*?)(?:\n|$)', content)
            if databook_match:
                result['DATABOOK-ID'] = databook_match.group(1).strip()

            # Find all tables through ### table-name
            table_matches = re.findall(r'### (.*?)(?:\n|$)', content)
            if table_matches:
                result['TABLES'] = {}
                for i, table_name in enumerate(table_matches):
                    # Determine the start and end of the table content
                    start_pattern = rf'### {table_name}.*?\n'
                    if i + 1 < len(table_matches):
                        end_pattern = rf'### {table_matches[i + 1]}'
                    else:
                        end_pattern = r'\Z'

                    table_content_match = re.search(
                        rf'{start_pattern}(.*?)(?={end_pattern})',
                        content,
                        re.DOTALL
                    )

                    if table_content_match:
                        table_data = self.parse_markdown_table(
                            table_content_match.group(0))
                        # result['TABLES'].append({table_name: table_data})
                        result['TABLES'][table_name] = table_data

            # update
            databook_data[databook_name_].update(result)
            # reference
            reference = {'REFERENCES': databook_data}

            return reference
        except Exception as e:
            raise Exception(f"Parsing markdown failed! {e}")

    def parse_markdown_table(self, content: str):
        """
        Parse a structured markdown content and extract information.

        Parameters
        ----------
        content : str
            The markdown content to parse.

        Returns
        -------
        dict
            Dictionary containing all the extracted information.
        """
        # Initialize the result dictionary
        result = {}

        # SECTION: TABLE-ID
        table_match = re.search(r'TABLE-ID: (.*?)(?:\n|$)', content)
        if table_match:
            result['TABLE-ID'] = table_match.group(1).strip()

        # SECTION: DESCRIPTION
        desc_match = re.search(r'DESCRIPTION: (.*?)(?:\n|$)', content)
        if desc_match:
            result['DESCRIPTION'] = desc_match.group(1).strip()

        # SECTION: DATA
        data_match = re.search(r'DATA: \[(.*?)\]', content, re.DOTALL)
        if data_match:
            data_str = data_match.group(1).strip()
            if data_str:
                try:
                    result['DATA'] = ast.literal_eval(f"[{data_str}]")
                except Exception:
                    result['DATA'] = data_str
            else:
                result['DATA'] = []

        # Extract MATRIX-SYMBOL
        matrix_match = re.search(
            r'MATRIX-SYMBOL:\s*\n(.*?)(?:\n\w+:|$)', content, re.DOTALL
        )
        if matrix_match:
            matrix_content = matrix_match.group(1).strip()
            matrix_items = re.findall(r'- (.*?)(?:\n|$)', matrix_content)
            result['MATRIX-SYMBOL'] = [item.strip() for item in matrix_items]

        # SECTION: EQUATIONS
        equations = {}
        eq_pattern = r'EQUATIONS:\s*\n(.*?)(?:\n\w+:|$)'
        eq_section = re.search(eq_pattern, content, re.DOTALL)
        if eq_section:
            eq_content = eq_section.group(1)
            eq_pattern = r'- (EQ-\d+):\s*\n(.*?)(?=\n- EQ-\d+:|\n\w+:|$)'
            eq_blocks = re.findall(eq_pattern, eq_content, re.DOTALL)

            # Debug output to verify equation blocks found
            # print(f"Found {len(eq_blocks)} equation blocks")

            for eq_id, eq_block in eq_blocks:
                equation = {}

                # Extract parts like BODY, BODY-INTEGRAL, etc.
                parts_pattern = (
                    r'  - (\w+(?:-\w+)*):\s*\n(.*?)(?=  - \w+(?:-\w+)*:|\Z)'
                )
                parts = re.findall(parts_pattern, eq_block + '  - ', re.DOTALL)

                for part_name, part_content in parts:
                    # Extract content items from the part content
                    content_items = re.findall(
                        r'- (.*?)(?:\n|$)', part_content)
                    if content_items:
                        equation[part_name] = [
                            item.strip().rstrip('-').strip()
                            for item in content_items
                        ]
                    else:
                        # Ensure empty lists for missing content
                        equation[part_name] = 'None'

                equations[eq_id] = equation

            result['EQUATIONS'] = equations

        # SECTION: STRUCTURE
        structure = {}
        struct_pattern = r'STRUCTURE:\s*\n(.*?)(?:\n\w+:|$)'
        struct_section = re.search(struct_pattern, content, re.DOTALL)
        if struct_section:
            struct_content = struct_section.group(1)

            # Extract parts like COLUMNS, SYMBOL, etc.
            struct_parts = re.findall(r'- (\w+):\s*\[(.*?)\]', struct_content)

            for part_name, part_content in struct_parts:
                try:
                    items = [item.strip() for item in part_content.split(',')]
                    structure[part_name] = items
                except Exception:
                    structure[part_name] = part_content

            result['STRUCTURE'] = structure

        # SECTION: VALUES
        values = []
        values_pattern = r'VALUES:\s*\n(.*?)(?:\n\w+:|$)'
        values_section = re.search(values_pattern, content, re.DOTALL)
        if values_section:
            values_content = values_section.group(1)
            value_rows = re.findall(r'- \[(.*?)\]', values_content)

            for row in value_rows:
                # NOTE: replace double quotes with single quotes
                # row = row.replace('"', "'")
                # NOTE: remove quotes from left and right
                row = row.strip().strip('"')
                # NOTE: remove quotes from left and right
                row = row.strip().strip("'")

                try:
                    # Use a regex to split on commas but not on commas inside single or double quotes
                    items = []
                    # Split by commas that are not within single or
                    # double quotes
                    # pattern = r',\s*(?=(?:[^\'"]*(\'|")[^\'"]*\1)*[^\']*$)'
                    pattern = r"""
                        (                             # Capture group
                            "(?:[^"\\]|\\.)*"         # Double-quoted string, allowing escaped quotes
                            |                         # OR
                            '(?:[^'\\]|\\.)*'         # Single-quoted string, allowing escaped quotes
                            |                         # OR
                            [^,\[\]\s]+               # Unquoted tokens (numbers, identifiers)
                        )
                    """

                    # split the row
                    # parts = re.split(pattern, row)
                    parts = re.findall(pattern, row, re.VERBOSE)

                    # loop through the parts
                    for part in parts:
                        # remove quotes from left and right
                        part = part.strip().strip('"').strip("'")
                        # check if part is empty
                        if part == '':
                            continue

                        items.append(part)
                    values.append(items)
                except Exception:
                    values.append(row)

            result['VALUES'] = values

        # SECTION: ITEMS
        items_match = re.search(
            r'ITEMS:\s*\n(.*?)(?:\n\w+:|$)', content, re.DOTALL
        )
        if items_match:
            items_content = items_match.group(1).strip()
            items = []
            # Updated regex to capture all elements starting with - item:
            item_pattern = (
                # Match any item names starting with "- "
                r'- ([\|\w\d\s]+):\s*\n'
                # Match content containing list elements with square brackets
                r'((?:\s*- \[.*?\]\s*\n)+)'
            )
            item_blocks = re.findall(
                item_pattern,
                items_content,
                re.DOTALL
            )

            for item_name, item_content in item_blocks:
                item_values = re.findall(r'- \[(.*?)\]', item_content)
                _item_res = [
                    [value.strip() for value in row.split(',')]
                    for row in item_values
                ]

                # item name
                item_name = str(item_name).strip()

                # append
                items.append({
                    item_name: _item_res
                })

            result['ITEMS'] = items

        # SECTION: EXTERNAL-REFERENCES
        external_references = []
        ext_ref_pattern = r'EXTERNAL-REFERENCES:\s*\n(.*?)(?:\n\w+:|$)'
        ext_ref_section = re.search(ext_ref_pattern, content, re.DOTALL)
        if ext_ref_section:
            ext_ref_content = ext_ref_section.group(1)
            external_references = re.findall(
                r'- (.*?)(?:\n|$)', ext_ref_content)

            result['EXTERNAL-REFERENCES'] = [
                ref.strip() for ref in external_references
            ]

        return result

    def content_manager(
            self,
            content: List[str | dict]
    ) -> List[str | dict]:
        '''
        Manage content

        Parameters
        ----------
        content : List[str]
            list of content containing separate references

        Returns
        -------
        content : str | dict
            content
        '''
        try:
            # NOTE: check content
            if content is None:
                raise Exception("No content found.")

            # length check
            if len(content) == 0:
                raise Exception("No content found.")

            return content
        except Exception as e:
            raise Exception(f"Content manager failed! {e}")

    def check_content_format(
            self,
            content: str | dict
    ) -> str:
        """
        Check the format of the content and return markdown or yml.

        Parameters
        ----------
        content : str
            The content to check.

        Returns
        -------
        str
            'markdown' if the content is in markdown format, 'yml' otherwise.
        """
        try:
            # NOTE: If content is a dictionary, convert it to a string
            if isinstance(content, dict):
                return 'dict'

            # NOTE: set content to string
            content = str(content)

            # Regex to match a line starting with optional spaces, then # REFERENCES
            pattern = r"^\s*#\s*REFERENCES\s*$"

            # check if the content matches the markdown pattern
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                return 'markdown'
            # Check if the content is in YAML format
            elif yaml.safe_load(content) is not None:
                return 'yml'
            else:
                raise ValueError("Content format not recognized.")
        except Exception as e:
            raise Exception(f"Checking content format failed! {e}")
