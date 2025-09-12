# import libs
import logging
from typing import (
    Dict,
    Union,
    Any,
    Tuple
)
# local
from .checker import ReferenceChecker
from ..utils import YAMLExtractor

# NOTE: setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def load_reference_from_str(
    custom_reference: str
):
    """
    Load a custom reference (string format) and return a dictionary.

    Parameters
    ----------
    custom_reference : str
        The custom reference as a string.

    Returns
    -------
    Dict[str, Any] | None
        A dictionary containing the custom reference if it exists, otherwise None.
    """
    try:
        # NOTE: check if custom_reference is a dict
        if not isinstance(custom_reference, str):
            raise TypeError("custom_reference must be a dictionary or string.")

        # SECTION: create ReferenceChecker instance
        ReferenceChecker_ = ReferenceChecker(custom_reference)

        # reference
        reference = ReferenceChecker_.reference

        return reference
    except (TypeError, KeyError) as e:
        logging.error(f"Error checking custom reference: {e}")
        raise


def check_custom_reference(
    custom_reference: Union[Dict[str, Any], str]
):
    """
    Load and check the custom reference and return a dictionary.

    Parameters
    ----------
    custom_reference : str
        The custom reference as a string.

    Returns
    -------
    Dict[str, Any] | None
        A dictionary containing the custom reference if it exists, otherwise None.
    """
    try:
        # NOTE: check if custom_reference is a dict
        if not isinstance(custom_reference, (dict, str)):
            raise TypeError("custom_reference must be a dictionary or string.")

        # SECTION: create ReferenceChecker instance
        ReferenceChecker_ = ReferenceChecker(custom_reference)

        # reference
        reference = ReferenceChecker_.reference

        return reference
    except (TypeError, KeyError) as e:
        logging.error(f"Error checking custom reference: {e}")
        raise


def extract_reference_from_str(
    content: str
) -> Tuple[bool, str]:
    """
    Extract and validate reference sections from a string.

    Parameters
    ----------
    content : str
        The content string to extract reference sections from.

    Returns
    -------
    Tuple[bool, str]
        A tuple containing a boolean indicating if YAML was found and a yaml string.

    Notes
    -----
    The extracted section contains only one `REFERENCES` marker and can be directly used in the init function.
    """
    try:
        # SECTION: create YAMLExtractor instance
        extractor = YAMLExtractor()

        # NOTE: extract and validate
        result = extractor.extract_and_validate(content)

        # NOTE: yaml found
        yaml_found = result.get('found_yaml', False)
        if not yaml_found:
            # return
            return False, "The input string does not contain any valid YAML sections."

        # NOTE: yaml sections
        yaml_sections = result.get('sections', [])
        # it should contain only one section
        # >>> no sections
        if len(yaml_sections) == 0:
            return False, "The input string does not contain any valid YAML sections."

        # >>> multiple sections
        if len(yaml_sections) > 1:
            logging.warning(
                "Multiple YAML sections found. Using the first one.")
            return False, "Multiple YAML sections found. Using the first one."

        # NOTE: use the first section
        first_section = yaml_sections[0]
        # >>> valid status
        if not first_section.get('valid', False):
            return False, "The extracted YAML section is not valid."

        # >>> raw yaml
        raw_yaml = first_section.get('raw', '')
        # strip
        raw_yaml = raw_yaml.strip()

        return True, raw_yaml
    except Exception as e:
        logging.error(f"Error extracting reference from string: {e}")
        raise
