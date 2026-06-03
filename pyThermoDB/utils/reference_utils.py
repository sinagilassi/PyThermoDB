# import libs
import logging
from collections.abc import Mapping
from typing import Any, Dict, List, Optional, Literal, Union, cast
from pythermodb_settings.models import Component
# locals
from ..config import REFERENCE_CONFIG_KEYS
from .convertor import Convertor

# NOTE: logger
logger = logging.getLogger(__name__)


def _normalize_constant_reference_config(
    reference_config: Union[Mapping[str, Any], str]
) -> Dict[str, Dict[str, Any]]:
    """
    Normalize constants reference configs.
    """
    if isinstance(reference_config, str):
        convertor = Convertor()
        ref_format = convertor.which_format(reference_config)

        if ref_format == "unknown":
            logging.error(
                "Unknown format. Please provide data in YAML or JSON format.")
            reference_config = {}
        elif ref_format.lower() in ["yaml", "json"]:
            reference_config = convertor.str_to_dict(
                reference_config,
                format=ref_format.lower()
            )
        else:
            raise ValueError(f"Unsupported format: {ref_format}")

    if not isinstance(reference_config, Mapping):
        raise TypeError("reference_config must be a dictionary")

    for wrapper_key in ['CONSTANTS', 'constants', 'constant']:
        wrapper_value = reference_config.get(wrapper_key, None)
        if isinstance(wrapper_value, dict):
            reference_config = wrapper_value
            break

    if not reference_config:
        raise ValueError("reference_config must not be empty")

    return {
        str(source_name).strip(): cast(Dict[str, Any], source_config)
        for source_name, source_config in reference_config.items()
        if str(source_name).strip() and isinstance(source_config, dict)
    }


def _normalize_constants_filter(
    constants: Optional[Union[str, List[str]]]
) -> List[str]:
    """
    Normalize requested constants into a list.
    """
    if constants is None:
        return []
    if isinstance(constants, str):
        return [constants]
    if isinstance(constants, list) and all(isinstance(c, str) for c in constants):
        return constants
    raise TypeError("constants must be a string, a list of strings, or None")


def _constant_config_labels(
    source_config: Dict[str, Any]
) -> List[str]:
    """
    Extract constants identifiers declared in config labels/symbols.
    """
    identifiers: List[str] = []

    label_ = source_config.get('label', None) or source_config.get(
        'symbol', None
    )
    if isinstance(label_, str):
        identifiers.append(label_)

    labels_ = source_config.get('labels', None) or source_config.get(
        'symbols', None
    )
    if isinstance(labels_, dict):
        for key, value in labels_.items():
            if isinstance(key, str):
                identifiers.append(key)
            if isinstance(value, str):
                identifiers.append(value)
    elif isinstance(labels_, list):
        identifiers.extend([item for item in labels_ if isinstance(item, str)])
    elif isinstance(labels_, str):
        identifiers.append(labels_)

    return list(dict.fromkeys([item for item in identifiers if item.strip()]))


def _is_constants_table_type(
    thermodb: Any,
    databook: str,
    table: str
) -> bool:
    """
    Check whether a table is registered as a constants table.
    """
    table_info_ = thermodb.table_info(
        databook=databook,
        table=table,
        res_format='dict'
    )
    if not isinstance(table_info_, dict):
        raise TypeError("Table info must be a dictionary")

    return table_info_.get('Type', None) == 'Constants'


# SECTION: Build constants sources
def _build_constant_sources(
    thermodb: Any,
    reference_config: Dict[str, Dict[str, Any]],
    constants: Optional[Union[str, List[str]]] = None,
    search_mode: Literal['NAME', 'SYMBOL', 'BOTH'] = 'BOTH',
    check_source: bool = False,
    verbose: Optional[bool] = False
) -> Dict[str, Any]:
    """
    Build constants sources from config and optionally validate constants.

    Parameters
    ----------
    thermodb : Any
        The thermodynamic database instance to use for building constants.
    reference_config : Dict[str, Dict[str, Any]]
        A dictionary containing reference configurations for constants sources.
    constants : Optional[Union[str, List[str]]], optional
        A constant name or a list of constant names to check for availability in the sources. If None, no availability check is performed, by default None.
    search_mode : Literal['NAME', 'SYMBOL', 'BOTH'], optional
        The mode to search for constants in the sources: by 'NAME', by 'SYMBOL', or 'BOTH', by default 'BOTH'.
    check_source : bool, optional
        Whether to perform additional checks on the source tables (e.g., check if the table is a constants table and if configured labels/symbols are available), by default False.
    verbose : Optional[bool], optional
        Whether to log additional information during the process, by default False.

    Returns
    -------
    Dict[str, Any]
        A dictionary of built constants sources that passed the availability and optional checks, keyed by source name.
    """
    if search_mode not in ['NAME', 'SYMBOL', 'BOTH']:
        raise ValueError("search_mode must be 'NAME', 'SYMBOL', or 'BOTH'.")

    constants_ = _normalize_constants_filter(constants)
    res: Dict[str, Any] = {}

    databook_list = thermodb.list_databooks(res_format='list')
    if not isinstance(databook_list, list):
        raise TypeError("Databook list must be a list")

    for source_name, source_config in reference_config.items():
        databook_ = source_config.get('databook', None)
        if databook_ is None:
            logging.error(
                f"Databook for constants source '{source_name}' is not specified."
            )
            continue

        if is_databook_available(str(databook_), databook_list) is False:
            logging.error(
                f"Databook '{databook_}' for constants source '{source_name}' is not found in the databook list."
            )
            continue

        table_dict_ = thermodb.list_tables(
            databook=databook_,
            res_format='dict'
        )
        if not isinstance(table_dict_, dict):
            raise TypeError("Table list must be a dictionary")

        table_list_ = list(table_dict_.values())
        if not isinstance(table_list_, list) or not table_list_:
            raise TypeError("Table list must be a list")

        table_ = source_config.get('table', None)
        if table_ is None:
            logging.error(
                f"Table for constants source '{source_name}' is not specified."
            )
            continue

        if is_table_available(str(table_), table_list_) is False:
            logging.error(
                f"Table '{table_}' for constants source '{source_name}' is not found in the databook '{databook_}'."
            )
            continue

        if check_source:
            try:
                if not _is_constants_table_type(
                    thermodb=thermodb,
                    databook=str(databook_),
                    table=str(table_)
                ):
                    logging.error(
                        f"Table '{table_}' for constants source '{source_name}' is not a constants table."
                    )
                    continue
            except Exception as e:
                logging.error(
                    f"Checking constants table '{table_}' for source '{source_name}' failed! {e}"
                )
                continue

        try:
            item_ = thermodb.build_constants(
                databook=databook_,
                table=table_
            )
        except Exception as e:
            logging.error(
                f"Building constants source '{source_name}' from table '{table_}' failed! {e}"
            )
            continue

        if constants_:
            constant_availability = [
                item_.is_constant_available(
                    constant,
                    search_mode=search_mode
                ).availability
                for constant in constants_
            ]
            if not any(constant_availability):
                if verbose:
                    logging.info(
                        f"Constants source '{source_name}' skipped because requested constants were not found."
                    )
                continue

        if check_source:
            configured_labels = _constant_config_labels(source_config)
            label_availability = [
                item_.is_constant_available(
                    label,
                    search_mode='BOTH'
                ).availability
                for label in configured_labels
            ]
            if configured_labels and not all(label_availability):
                logging.error(
                    f"Constants source '{source_name}' skipped because configured labels/symbols were not found."
                )
                continue

        res[source_name] = item_

    return res


# SECTION: Look up reference configs
def look_up_component_reference_config(
    component_id: str,
    reference_config: Dict[str, Any],
    reference_config_default_check: Optional[bool] = True
) -> Dict[str, Any]:
    '''
    Look up the reference configuration for a given component ID.

    Parameters
    ----------
    component_id : str
        The ID of the component to look up.
    reference_config : Dict[str, Any]
        A dictionary containing reference configurations for components.
    reference_config_default_check : Optional[bool], optional
        Whether to perform default checks on the reference configuration, by default True

    Returns
    -------
    Dict[str, Any]
        The reference configuration for the specified component.

    Raises
    ------
    ValueError
        If no reference configuration is found for the specified component.
    '''
    # Convert all keys to lowercase for case-insensitive lookup
    reference_config_lower = {
        k.lower(): v for k, v in reference_config.items()
    }
    # Lowercase component_id for case-insensitive lookup
    component_id_lower = component_id.lower()

    # Extract component reference config
    component_reference_config = reference_config_lower.get(
        component_id_lower,
        {}
    )

    # Check if reference_config is empty
    if not component_reference_config:
        # Check default
        if reference_config_default_check:
            for key in REFERENCE_CONFIG_KEYS:
                key_lower = key.lower()
                if key_lower in reference_config_lower:
                    component_reference_config = reference_config_lower[key_lower]
                    break

    if not component_reference_config:
        raise ValueError(
            f"No reference config found for component '{component_id}' in the provided reference config."
        )

    return component_reference_config


# SECTION: Look up mixture reference configs
def look_up_binary_mixture_reference_config(
        component_id_1: str,
        component_id_2: str,
        reference_config: Dict[str, Any],
        reference_config_default_check: Optional[bool] = True,
        delimiter: str = '|'
) -> Dict[str, Any]:
    '''
    Look up the reference configuration for a given binary mixture of two components.

    Parameters
    ----------
    component_id_1 : str
        The ID of the first component in the mixture.
    component_id_2 : str
        The ID of the second component in the mixture.
    reference_config : Dict[str, Any]
        A dictionary containing reference configurations for components and mixtures.
    reference_config_default_check : Optional[bool], optional
        Whether to perform default checks on the reference configuration, by default True
    delimiter : str, optional
        Delimiter to separate component identifiers in the mixture, by default '|'

    Returns
    -------
    Dict[str, Any]
        The reference configuration for the specified binary mixture.

    Raises
    ------
    ValueError
        If no reference configuration is found for the specified binary mixture.
    '''
    # Create possible mixture IDs (both orders)
    mixture_id_1 = f"{component_id_1.strip().lower()}{delimiter}{component_id_2.strip().lower()}"
    mixture_id_2 = f"{component_id_2.strip().lower()}{delimiter}{component_id_1.strip().lower()}"

    # Convert all keys to lowercase for case-insensitive lookup
    reference_config_lower = {
        k.lower(): v for k, v in reference_config.items()
    }

    # NOTE: Extract binary mixture reference config
    binary_mixture_reference_config = reference_config_lower.get(
        mixture_id_1,
        reference_config_lower.get(mixture_id_2, {})
    )

    # NOTE: Check if reference_config is empty
    if not binary_mixture_reference_config:
        # Check default
        if reference_config_default_check:
            for key in REFERENCE_CONFIG_KEYS:
                key_lower = key.lower()
                if key_lower in reference_config_lower:
                    binary_mixture_reference_config = reference_config_lower[key_lower]
                    break

    if not binary_mixture_reference_config:
        raise ValueError(
            f"No reference config found for binary mixture '{component_id_1}' and '{component_id_2}' in the provided reference config."
        )

    return binary_mixture_reference_config


def look_up_mixture_reference_config(
        components: List[Component],
        reference_config: Dict[str, Any],
        reference_config_default_check: Optional[bool] = True,
        mixture_key: Literal['Name', 'Formula'] = 'Name',
        delimiter: str = '|'
) -> Dict[str, Any]:
    '''
    Look up the reference configuration for a given mixture of components.

    Parameters
    ----------
    components : List[Component]
        A list of Component objects representing the components in the mixture.
    reference_config : Dict[str, Any]
        A dictionary containing reference configurations for components and mixtures.
    reference_config_default_check : Optional[bool], optional
        Whether to perform default checks on the reference configuration, by default True
    mixture_key : Literal['Name', 'Formula'], optional
        Key to identify the component in the reference content, by default 'Name'
    delimiter : str, optional
        Delimiter to separate component identifiers in the mixture, by default '|'

    Returns
    -------
    Dict[str, Any]
        The reference configuration for the specified mixture.

    Raises
    ------
    ValueError
        If no reference configuration is found for the specified mixture.
    '''
    if len(components) < 2:
        raise ValueError(
            "At least two components are required to form a mixture.")

    # Generate mixture ID based on component_key
    if mixture_key == 'Name':
        component_ids = [
            comp.name.strip() for comp in components
        ]
    elif mixture_key == 'Formula':
        component_ids = [
            comp.formula.strip() for comp in components
        ]
    else:
        raise ValueError(
            "Invalid component_key. Must be 'Name-State' or 'Formula-State'.")

    # NOTE: Create mixture ID by sorting component IDs to ensure order-independence
    mixture_id = delimiter.join(sorted([cid.lower() for cid in component_ids]))

    # NOTE: Normalize reference_config keys: split, strip, lowercase, sort, join
    reference_config_normalized = {
        delimiter.join(sorted([part.strip().lower() for part in k.split(delimiter)])): v
        for k, v in reference_config.items() if delimiter in k
    }

    # NOTE: Extract mixture reference config
    mixture_reference_config = reference_config_normalized.get(
        mixture_id,
        {}
    )

    # NOTE: Check if reference_config is empty
    if not mixture_reference_config:
        # Check default (only for mixture keys)
        if reference_config_default_check:
            for key in REFERENCE_CONFIG_KEYS:
                key_lower = key.lower()
                if key_lower in reference_config_normalized:
                    mixture_reference_config = reference_config_normalized[key_lower]
                    break

    if not mixture_reference_config:
        raise ValueError(
            f"No reference config found for mixture '{mixture_id}' in the provided reference config."
        )

    # return mixture reference config
    return mixture_reference_config


def is_table_available(
        table_name: str,
        tables: List[str]
):
    '''
    Check if a table name is available in the list of tables.

    Parameters
    ----------
    table_name : str
        The name of the table to check.
    tables : List[str]
        A list of available table names.

    Returns
    -------
    bool
        True if the table name is available, False otherwise.

    Notes
    -----
    - The comparison is case-insensitive and ignores leading/trailing whitespace.
    '''
    try:
        # Normalize table name for comparison
        normalized_table_name = table_name.strip().lower()
        normalized_tables = [t.strip().lower() for t in tables]

        return normalized_table_name in normalized_tables
    except Exception as e:
        logger.error(f"Error checking table availability: {e}")
        return False


def is_databook_available(
        databook_name: str,
        databooks: List[str]
):
    '''
    Check if a databook name is available in the list of databooks.

    Parameters
    ----------
    databook_name : str
        The name of the databook to check.
    databooks : List[str]
        A list of available databook names.

    Returns
    -------
    bool
        True if the databook name is available, False otherwise.

    Notes
    -----
    - The comparison is case-insensitive and ignores leading/trailing whitespace.
    '''
    try:
        # Normalize databook name for comparison
        normalized_databook_name = databook_name.strip().lower()
        normalized_databooks = [d.strip().lower() for d in databooks]

        return normalized_databook_name in normalized_databooks
    except Exception as e:
        logger.error(f"Error checking databook availability: {e}")
        return False
