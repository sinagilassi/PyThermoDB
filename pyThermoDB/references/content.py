# import libs
from typing import (
    Dict,
    List,
    Any,
    Optional,
    Literal
)
import logging
# local
from ..utils import Convertor
from ..docs import ManageData, CustomRef


class ReferenceContent:
    """
    Class to handle reference content.
    This class is used to manage the content of references in pyThermoDB.
    """

    def __init__(self):
        """Initialize the ReferenceContent class."""
        # NOTE: init Convertor
        self.Convertor_ = Convertor()

    def set_reference_content(
        self,
        reference_config: str
    ) -> Dict[str, Any]:
        """
        Convert a string reference content to a dictionary.

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
                # return self.md_to_dict(reference_config)
                logging.error(
                    "Markdown format is not supported for reference content.")
                return {}
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


def load_custom_reference(
    custom_reference: Dict[str, List[str]],
    save_to_file: bool = False,
    file_format: Literal['txt', 'yml'] = 'txt',
    file_name: Optional[str] = None,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    '''
    Load custom reference (external reference) to check and build thermodynamic data and equations.

    Parameters
    ----------
    custom_reference : dict
        Custom reference dictionary to check.
    save_to_file : bool, optional
        If True, save the custom reference to a txt file, by default False.
    file_format : Literal['txt', 'yml'], optional
        Format of the file to save the custom reference, by default 'txt'. Options are 'txt' or 'yml'.
    file_name : str, optional
        Name of the file to save the custom reference, by default None. If not specified,
    directory : str, optional
        Directory to save the custom reference file, by default None. The file will be saved in the current working directory if not specified.

    Returns
    -------
    bool
        True if the custom reference is valid, False otherwise.
    '''
    try:
        # SECTION: check custom reference
        if not isinstance(custom_reference, dict):
            logging.error("Custom reference must be a dictionary!")
            return {}

        # check if custom_reference is empty
        if not custom_reference:
            logging.error("Custom reference is empty!")
            return {}

        # SECTION: build custom reference
        CustomRefC = CustomRef(custom_reference)
        # check ref
        CustomRefC.init_ref()

        # SECTION: load custom reference
        reference = ManageData.load_custom_reference(
            custom_ref=CustomRefC,
            save_to_file=save_to_file,
            file_format=file_format,
            file_name=file_name,
            output_dir=output_dir
        )

        # res
        if not isinstance(reference, dict):
            logging.error("Custom reference is not valid or empty!")
            return {}

        # return
        return reference
    except Exception as e:
        logging.error(f"Loading custom reference failed! {e}")
        return {}
