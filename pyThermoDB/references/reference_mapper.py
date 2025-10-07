# import libs
import logging
from typing import (
    Literal,
    List,
    Optional
)
from pythermodb_settings.models import (
    Component,
    ComponentReferenceThermoDB,
    ReferenceThermoDB
)
# local
from .checker import ReferenceChecker
from ..utils import ignore_state_in_prop
from ..models import MixtureReferenceThermoDB

# NOTE: set logger
logger = logging.getLogger(__name__)


def component_reference_mapper(
    component: Component,
    reference_content: str,
    component_key: Literal[
        'Name-State', 'Formula-State'
    ] = 'Formula-State',
    add_label: Optional[bool] = True,
    check_labels: Optional[bool] = True,
    ignore_component_state: Optional[bool] = False,
    **kwargs
) -> ComponentReferenceThermoDB:
    '''
    Build component thermodynamic databook (thermodb) including data and equations.

    Parameters
    ----------
    component : Component
        An instance of the Component model containing details about the component.
    reference_content : str
        String content of the reference (YAML format) containing databook and tables.
    component_key : Literal['Name-State', 'Formula-State'], optional
        Key to identify the component in the reference content, by default 'Formula-State'
    add_label : Optional[bool], optional
        Whether to add labels to the component reference config, by default True
    check_labels : Optional[bool], optional
        Whether to check labels in the component reference config, by default True
    ignore_component_state : Optional[bool], optional
        Whether to ignore the component state in the check, by default False.
    **kwargs
        Additional keyword arguments.
        - ignore_state_props: Optional[List[str]]
            List of property names to ignore state during the build. By default, None.

    Returns
    -------
    ComponentReferenceThermoDB
        An instance of ComponentReferenceThermoDB containing the built thermodynamic databook and reference details.

    Notes
    -----
    - The `reference_content` should be a valid YAML string containing the necessary databook and table information.
    - The function utilizes the `ReferenceChecker` class to parse and validate the reference content.
    - The built `ComponentThermoDB` object includes the component details, the thermodynamic databook, and the reference configuration used.
    - The `add_label` and `check_labels` parameters help in managing the reference configuration for the component. In this context, labels defined in the reference are compared with the PyThermoDB labels (symbols) to ensure consistency.
    '''
    try:
        # NOTE: kwargs
        ignore_state_props: Optional[List[str]] = kwargs.get(
            'ignore_state_props', None
        )
        # set default if None
        if ignore_state_props is None:
            ignore_state_props = []

        # NOTE: check inputs
        if not isinstance(component, Component):
            raise TypeError("component must be an instance of Component")

        if not isinstance(reference_content, str) or not reference_content.strip():
            raise ValueError("reference_content must be a non-empty string")

        # SECTION: extract component details
        component_name = component.name.strip()
        component_formula = component.formula.strip()
        component_state = component.state.strip()

        # NOTE: check component_state
        # component_state = cast(DEFAULT_COMPONENT_STATES, component_state)

        # SECTION: create ReferenceChecker instance
        ReferenceChecker_ = ReferenceChecker(reference_content)

        # NOTE: load all databooks
        databooks: List[str] = ReferenceChecker_.get_databook_names()

        # check databooks
        if not isinstance(databooks, list) or not databooks:
            raise ValueError("No databooks found in the reference content.")

        # NOTE: component reference config
        component_reference_configs = ReferenceChecker_.get_component_reference_configs(
            component_name=component_name,
            component_formula=component_formula,
            component_state=component_state,
            add_label=add_label,
            check_labels=check_labels,
            component_key=component_key,
            ignore_component_state=ignore_component_state,
            ignore_state_props=ignore_state_props
        )

        # NOTE: check if reference_config is a dict
        if not isinstance(component_reference_configs, dict) or not component_reference_configs:
            raise ValueError(
                f"No reference config found for component '{component_name}' in the provided reference content."
            )

        # SECTION: generate reference rules
        # ! from component_reference_configs
        reference_rules = ReferenceChecker_.generate_component_reference_rules(
            reference_configs=component_reference_configs
        )

        # SECTION: check component_reference_configs
        # labels
        labels = []
        # ignore component state
        ignore_state_props_check: bool = False
        # labels ignored
        labels_ignored = []
        # property names to ignore state check
        props_ignored = []

        # SECTION: check both databook and table
        for prop_name, prop_idx in component_reference_configs.items():
            # property name
            prop_name = prop_name.strip()

            # ! databook
            databook_ = prop_idx.get('databook', None)
            if databook_ is None:
                raise ValueError(
                    f"Databook for property '{prop_name}' is not specified.")

            # ! table
            table_ = prop_idx.get('table', None)
            if table_ is None:
                raise ValueError(
                    f"Table for property '{prop_name}' is not specified.")

            # ! label/labels
            # >> check label
            label_ = prop_idx.get('label', None)
            if label_:
                # append to labels
                labels.append(str(label_))

                # >> set ignore component property
                ignore_state_props_check = ignore_state_in_prop(
                    label_, ignore_state_props
                )

                # >>> store ignore state for component
                if ignore_state_props_check and label_ not in labels_ignored:
                    # append
                    # >> to labels_ignored
                    labels_ignored.append(label_)

                # >>> store ignore state for property
                if ignore_state_props_check and prop_name not in props_ignored:
                    # append
                    # >> to props_ignored
                    props_ignored.append(prop_name)

            # >> check labels
            labels_ = prop_idx.get('labels', None)
            if labels_ and isinstance(labels_, dict):
                # extract labels
                for lbl_key, lbl_val in labels_.items():
                    if lbl_val and isinstance(lbl_val, str):
                        # append to labels
                        labels.append(str(lbl_val))

                        # >> set ignore component property
                        ignore_state_props_check = ignore_state_in_prop(
                            prop_name=lbl_val,
                            ignore_state_props=ignore_state_props
                        )

                        # >>> store ignore state for component
                        if ignore_state_props_check and lbl_val not in labels_ignored:
                            labels_ignored.append(lbl_val)
                        # >>> store ignore state for property
                        if ignore_state_props_check and prop_name not in props_ignored:
                            props_ignored.append(prop_name)

            # NOTE: reset loop variables
            if len(ignore_state_props) > 0:
                ignore_state_props_check = False

        # NOTE: remove duplicates in labels
        labels = list(set(labels))
        labels_ignored = list(set(labels_ignored))

        # NOTE: check ignore_component_state
        if ignore_component_state:
            labels_ignored = labels.copy()
            props_ignored = list(component_reference_configs.keys())

        # SECTION: return result
        # NOTE: reference thermodb
        reference_thermodb: ReferenceThermoDB = ReferenceThermoDB(
            reference={'reference': [reference_content]},
            contents=[reference_content],
            configs=component_reference_configs,
            rules=reference_rules,
            labels=labels,
            ignore_labels=labels_ignored,
            ignore_props=props_ignored
        )

        # NOTE: component reference thermodb
        return ComponentReferenceThermoDB(
            component=component,
            reference_thermodb=reference_thermodb,
        )
    except Exception as e:
        raise Exception(f"Building {component_name} thermodb failed! {e}")


def mixture_reference_mapper(
    components: List[Component],
    reference_content: str,
    mixture_names: Optional[List[str]] = None,
    component_key: Literal[
        'Name-State', 'Formula-State'
    ] = 'Name-State',
    mixture_key: Literal[
        'Name', 'Formula',
    ] = 'Name',
    delimiter: str = '|',
    column_name: str = 'Mixture',
    add_label: Optional[bool] = True,
    check_labels: Optional[bool] = True,
    ignore_component_state: Optional[bool] = False,
    **kwargs
) -> Optional[MixtureReferenceThermoDB]:
    '''
    Build mixture thermodynamic databook (thermodb) for matrix-data.

    Parameters
    ----------
    components : List[Component]
        A list of Component instances containing details about the components in the mixture.
    reference_content : str
        String content of the reference (YAML format) containing databook and tables.
    mixture_names : Optional[List[str]], optional
        List of mixture names to identify the mixture in the reference content, by default None.
    component_key : Literal['Name-State', 'Formula-State'], optional
        Key to identify the components in the reference content, by default 'Name-State'
    mixture_key : Literal['Name', 'Formula'], optional
        Key to identify the mixture in the reference content, by default 'Name'
    delimiter : str, optional
        Delimiter used to separate component names in the mixture name, by default '|'
    column_name : str, optional
        Column name in the reference content that contains the mixture information, by default 'Mixture'
    add_label : Optional[bool], optional
        Whether to add labels to the mixture reference config, by default True
    check_labels : Optional[bool], optional
        Whether to check labels in the mixture reference config, by default True
    ignore_component_state : Optional[bool], optional
        Whether to ignore the component state in the check, by default False.
    **kwargs
        Additional keyword arguments.
        - ignore_state_props: Optional[List[str]]
            List of property names to ignore state during the build. By default, None.

    Returns
    -------
    Optional[MixtureReferenceThermoDB]
        An instance of MixtureReferenceThermoDB containing the built thermodynamic databook and reference details,
        or None if no valid properties were found to build the thermodb.

    Notes
    -----
    - The `reference_content` should be a valid YAML string containing the necessary databook and table information.
    - The function utilizes the `ReferenceChecker` class to parse and validate the reference content.
    - The built `MixtureThermoDB` object includes the component details, the thermodynamic databook, and the reference configuration used.
    - The `add_label` and `check_labels` parameters help in managing the reference configuration for the mixture. In this context, labels defined in the reference are compared with the PyThermoDB labels (symbols) to ensure consistency.
    - If no valid properties are found to build the thermodb for the given components, the function returns None.
    '''
    try:
        # NOTE: kwargs
        ignore_state_props: Optional[List[str]] = kwargs.get(
            'ignore_state_props', None
        )
        # set default if None
        if ignore_state_props is None:
            ignore_state_props = []

        # NOTE: check inputs
        if not isinstance(components, list) or not components:
            raise ValueError(
                "components must be a non-empty list of Component instances")

        if not all(isinstance(comp, Component) for comp in components):
            raise TypeError(
                "All items in components must be instances of Component")

        if not isinstance(reference_content, str) or not reference_content.strip():
            raise ValueError("reference_content must be a non-empty string")

        # mixture names
        if mixture_names is not None:
            if not isinstance(mixture_names, list) or not mixture_names:
                raise ValueError(
                    "mixture_names must be a non-empty list of strings or None")
            if not all(isinstance(name, str) and name.strip() for name in mixture_names):
                raise ValueError(
                    "All items in mixture_names must be non-empty strings")

        # SECTION: extract component details
        component_names = [comp.name.strip() for comp in components]
        component_formulas = [comp.formula.strip() for comp in components]
        component_states = [comp.state.strip() for comp in components]

        # NOTE: check component_state
        # component_state = cast(DEFAULT_COMPONENT_STATES, component_state)

        # SECTION: create ReferenceChecker instance
        ReferenceChecker_ = ReferenceChecker(reference_content)

        # NOTE: load all databooks
        databooks: List[str] = ReferenceChecker_.get_databook_names()

        # check databooks
        if not isinstance(databooks, list) or not databooks:
            raise ValueError("No databooks found in the reference content.")

        # NOTE: component reference config
        mixture_reference_configs = ReferenceChecker_.get_mixtures_reference_configs(
            components=components,
            add_label=add_label,
            check_labels=check_labels,
            component_key=component_key,
            mixture_key=mixture_key,
            mixture_names=mixture_names,
            delimiter=delimiter,
            column_name=column_name,
            ignore_component_state=ignore_component_state,
            ignore_state_props=ignore_state_props
        )

        # FIXME
        # >> check
        if not mixture_reference_configs:
            logger.warning(
                f"No valid properties found to build thermodb for components: {', '.join(component_names)}"
            )
            return None

        # NOTE: check if reference_config is a dict
        if not isinstance(mixture_reference_configs, dict) or not mixture_reference_configs:
            raise ValueError(
                f"No reference config found for component '{component_names}' in the provided reference content."
            )

        # SECTION: generate reference rules
        # ! from component_reference_configs
        reference_rules = ReferenceChecker_.generate_component_reference_rules(
            reference_configs=mixture_reference_configs
        )

        # SECTION: check component_reference_configs
        # labels
        labels = []
        # ignore component state
        ignore_state_props_check: bool = False
        # labels ignored
        labels_ignored = []
        # property names to ignore state check
        props_ignored = []

        # SECTION: check both databook and table
        for prop_name, prop_idx in mixture_reference_configs.items():
            # property name
            prop_name = prop_name.strip()

            # ! databook
            databook_ = prop_idx.get('databook', None)
            if databook_ is None:
                raise ValueError(
                    f"Databook for property '{prop_name}' is not specified.")

            # ! table
            table_ = prop_idx.get('table', None)
            if table_ is None:
                raise ValueError(
                    f"Table for property '{prop_name}' is not specified.")

            # ! label/labels
            # >> check label
            label_ = prop_idx.get('label', None)
            if label_:
                # append to labels
                labels.append(str(label_))

                # >> set ignore component property
                ignore_state_props_check = ignore_state_in_prop(
                    label_, ignore_state_props
                )

                # >>> store ignore state for component
                if ignore_state_props_check and label_ not in labels_ignored:
                    # append
                    # >> to labels_ignored
                    labels_ignored.append(label_)

                # >>> store ignore state for property
                if ignore_state_props_check and prop_name not in props_ignored:
                    # append
                    # >> to props_ignored
                    props_ignored.append(prop_name)

            # >> check labels
            labels_ = prop_idx.get('labels', None)
            if labels_ and isinstance(labels_, dict):
                # extract labels
                for lbl_key, lbl_val in labels_.items():
                    if lbl_val and isinstance(lbl_val, str):
                        # append to labels
                        labels.append(str(lbl_val))

                        # >> set ignore component property
                        ignore_state_props_check = ignore_state_in_prop(
                            prop_name=lbl_val,
                            ignore_state_props=ignore_state_props
                        )

                        # >>> store ignore state for component
                        if ignore_state_props_check and lbl_val not in labels_ignored:
                            labels_ignored.append(lbl_val)
                        # >>> store ignore state for property
                        if ignore_state_props_check and prop_name not in props_ignored:
                            props_ignored.append(prop_name)

            # NOTE: reset loop variables
            if len(ignore_state_props) > 0:
                ignore_state_props_check = False

        # NOTE: remove duplicates in labels
        labels = list(set(labels))
        labels_ignored = list(set(labels_ignored))

        # NOTE: check ignore_component_state
        if ignore_component_state:
            labels_ignored = labels.copy()
            props_ignored = list(mixture_reference_configs.keys())

        # SECTION: return result
        # NOTE: reference thermodb
        reference_thermodb: ReferenceThermoDB = ReferenceThermoDB(
            reference={'reference': [reference_content]},
            contents=[reference_content],
            configs=mixture_reference_configs,
            rules=reference_rules,
            labels=labels,
            ignore_labels=labels_ignored,
            ignore_props=props_ignored
        )

        # NOTE: component reference thermodb
        return MixtureReferenceThermoDB(
            component=component,
            reference_thermodb=reference_thermodb,
        )
    except Exception as e:
        raise Exception(f"Building {component_names} thermodb failed! {e}")
