# import libs
import logging
from typing import Dict, Any, Union, List, Literal
from pythermodb_settings.utils import measure_time
import yaml
# locals
from .checker import ReferenceChecker

# NOTE: setup logger
logger = logging.getLogger(__name__)


class ReferenceMaker(ReferenceChecker):
    """
    A class to load a custom reference and insert data to each table.
    """

    def __init__(
        self,
        custom_reference: Union[Dict[str, Any], str]
    ):
        """
        Initialize the ReferenceMaker class.

        Parameters
        ----------
        custom_reference : Dict[str, Any] | str
            The custom reference as a dictionary or string.
        """
        try:
            # NOTE: check if custom_reference is a dict
            if not isinstance(custom_reference, (dict, str)):
                raise TypeError(
                    "custom_reference must be a dictionary or string.")

            # NOTE: create ReferenceChecker instance
            super().__init__(custom_reference)
        except (TypeError, KeyError) as e:
            logging.error(f"Error checking custom reference: {e}")
            raise

    # SECTION: build YAML reference content
    def build_yaml_reference(self) -> str:
        """
        Build the YAML reference content and return it as a string.

        Returns
        -------
        str
            YAML string with top-level `REFERENCES` key.
        """
        try:
            class _FlowStyleList(list):
                """List marker for YAML flow-style serialization."""
                pass

            class _ReferenceDumper(yaml.SafeDumper):
                """Custom dumper to support selective flow-style lists."""
                pass

            def _flow_style_list_representer(dumper, data):
                return dumper.represent_sequence(
                    'tag:yaml.org,2002:seq',
                    data,
                    flow_style=True
                )

            _ReferenceDumper.add_representer(
                _FlowStyleList,
                _flow_style_list_representer
            )

            inline_list_keys = {
                'COLUMNS',
                'SYMBOL',
                'UNIT',
                'CONVERSION',
                'MATRIX-SYMBOL'
            }

            def _apply_inline_list_style(value, parent_key=None):
                if isinstance(value, dict):
                    return {
                        k: _apply_inline_list_style(v, parent_key=k)
                        for k, v in value.items()
                    }

                if isinstance(value, list):
                    styled_items = [
                        _apply_inline_list_style(item, parent_key=parent_key)
                        for item in value
                    ]
                    # Keep VALUES as block list, but render each row inline.
                    if parent_key == 'VALUES':
                        return [
                            _FlowStyleList(item) if isinstance(
                                item, list) else item
                            for item in styled_items
                        ]
                    if parent_key in inline_list_keys:
                        return _FlowStyleList(styled_items)
                    return styled_items

                return value

            # NOTE: get reference content
            reference_content = self.reference

            # NOTE: check reference content
            if reference_content is None:
                raise ValueError("Reference content is not loaded.")
            if not isinstance(reference_content, dict):
                raise TypeError("Reference content must be a dictionary.")

            # NOTE: normalize to expected root structure
            payload = (
                reference_content
                if 'REFERENCES' in reference_content
                else {'REFERENCES': reference_content}
            )
            payload = _apply_inline_list_style(payload)

            # NOTE: build YAML reference content
            return yaml.dump(
                payload,
                Dumper=_ReferenceDumper,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
                indent=2,
                width=120
            )
        except Exception as e:
            logging.error(f"Error building YAML reference: {e}")
            raise

    # NOTE: build YAML reference content and save to file
    def save_yaml_reference(self, file_path: str) -> None:
        """
        Build the YAML reference content and save it to a file.

        Parameters
        ----------
        file_path : str
            The path to the file where the YAML reference will be saved.
        """
        try:
            yaml_content = self.build_yaml_reference()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            logger.info(f"YAML reference saved to {file_path}")
        except Exception as e:
            logging.error(f"Error saving YAML reference: {e}")
            raise

    # SECTION: update multiple tables values
    def update_tables_values(
        self,
        databook_name: str,
        tables_data: Dict[str, List[List[str | float | int]]]
    ) -> Dict[str, bool]:
        """
        Update values for multiple tables in the reference.

        Parameters
        ----------
        databook_name : str
            The name of the databook to update.
        tables_data : Dict[str, List[List[str | float | int]]]
            A dictionary where keys are table names and values are lists of new values.

        Returns
        -------
        Dict[str, bool]
            A dictionary indicating which tables were successfully updated.
        """
        results = {}
        for table_name, new_values in tables_data.items():
            try:
                result = self.update_table_values(
                    databook_name=databook_name,
                    table_name=table_name,
                    new_values=new_values
                )
                results[table_name] = result is not None
            except Exception as e:
                logging.error(f"Error updating table '{table_name}': {e}")
                results[table_name] = False
        return results


@measure_time
def insert_data_to_reference_tables(
    reference: str,
    databook_name: str,
    tables_data: Dict[str, List[List[str | float | int]]],
    res_format: Literal['string', 'yaml'] = 'string',
    **kwargs
) -> str | dict[str, Any]:
    """
    Insert data to reference tables.

    Parameters
    ----------
    reference : str
        The reference content as a string.
    databook_name : str
        The name of the databook to update.
    tables_data : Dict[str, List[List[str | float | int]]]
        A dictionary where keys are table names and values are lists of new values.
    **kwargs
        Additional keyword arguments.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    str | dict[str, Any]
        The updated reference content in the specified format.
    """
    try:
        # NOTE: create ReferenceMaker instance
        reference_maker = ReferenceMaker(reference)

        # NOTE: update tables values
        results = reference_maker.update_tables_values(
            databook_name=databook_name,
            tables_data=tables_data
        )

        # NOTE: retrieve updated reference content
        # >> check result format
        if res_format == 'yaml':
            updated_reference = reference_maker.build_yaml_reference()
        else:
            updated_reference = reference_maker.reference

        # > check if None
        if updated_reference is None:
            raise ValueError("Updated reference content is None.")

        return updated_reference
    except Exception as e:
        logging.error(f"Error inserting data to reference tables: {e}")
        raise
