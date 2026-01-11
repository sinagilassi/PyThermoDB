# import libs
import logging
import time
from typing import (
    Optional,
    Dict,
    List,
    Union,
    Literal,
    cast
)
from pythermodb_settings.models import (
    Component,
    ReferenceThermoDB,
    ComponentConfig,
    CustomReference
)
from pythermodb_settings.utils import measure_time
# local
from .app import init, build_thermodb
from .references import ReferenceConfig, ReferenceChecker
from .utils import (
    set_component_id,
    ignore_state_in_prop,
    look_up_component_reference_config,
    is_table_available,
    is_databook_available,
    check_file_path,
    look_up_binary_mixture_reference_config,
    look_up_mixture_reference_config,
    create_mixture_ids
)
from .builder import CompBuilder
from .config import DEFAULT_COMPONENT_STATES
from .thermodb import ComponentThermoDB, MixtureThermoDB
# ! deps
from .config.deps import set_config, AppConfig

# NOTE: logger
logger = logging.getLogger(__name__)


class ReferenceSource:
    """
    Class to handle reference source for building thermodynamic databooks.
    """
    # SECTION: Attributes

    def __init__(
        self,
        reference_content: str,
        **kwargs
    ):
        """
        Initialize the BuildThermoDB class.

        Parameters
        ----------
        reference_content : str
            The content source for reference data (e.g., file path or database identifier).
        """
        # NOTE: reference content
        self.reference_content = reference_content

        try:
            # reference checker
            # SECTION: create ReferenceChecker instance
            self.ReferenceChecker_ = ReferenceChecker(reference_content)

            # NOTE: load all databooks
            self.databooks: List[str] = self.ReferenceChecker_.get_databook_names(
            )

            # check databooks
            if not isinstance(self.databooks, list) or not self.databooks:
                raise ValueError(
                    "No databooks found in the reference content.")
        except Exception as e:
            logger.error(f"Error initializing ReferenceChecker: {e}")
            raise

        try:
            # SECTION: build thermodb
            # set reference
            self.reference: CustomReference = {
                'reference': [self.reference_content]}

            self.thermodb = init(
                custom_reference=self.reference
            )
        except Exception as e:
            logger.error(f"Error initializing thermodb: {e}")
            raise


@measure_time
def build_component_thermodb_from_reference_source(
        component: Component,
        reference_source: ReferenceSource,
        component_key: Literal[
            'Name-State', 'Formula-State'
        ] = 'Name-State',
        add_label: Optional[bool] = True,
        check_labels: Optional[bool] = True,
        check_component: Optional[bool] = True,
        thermodb_name: Optional[str] = None,
        message: Optional[str] = None,
        thermodb_save: Optional[bool] = False,
        thermodb_save_path: Optional[str] = None,
        verbose: bool = False,
        include_data: bool = False,
        **kwargs
) -> Optional[ComponentThermoDB]:
    '''
    Build component thermodynamic databook (thermodb) including data and equations.

    Parameters
    ----------
    component : Component
        Component object including name, formula, and state.
    reference_source : ReferenceSource
        ReferenceSource object including the reference content for building the thermodb.
    component_key : Literal['Name-State', 'Formula-State'], optional
        Key to identify the component in the reference content, by default 'Formula-State'
    add_label : Optional[bool], optional
        Whether to add labels to the component reference config, by default True
    check_labels : Optional[bool], optional
        Whether to check labels in the component reference config, by default True
    check_component : Optional[bool], optional
        Whether to check component availability in the reference content, by default True
    thermodb_name : Optional[str], optional
        Name of the thermodynamic databook to be built, by default None
    message : Optional[str], optional
        A short description of the component thermodynamic databook, by default None
    thermodb_save : Optional[bool], optional
        Whether to save the built thermodb to a file, by default False
    thermodb_save_path : Optional[str], optional
        Path to save the built thermodb file, by default None. If None, it will save to the current directory with the name `{thermodb_name}.pkl`.
    verbose : bool, optional
        Whether to enable verbose logging, by default False
    include_data : bool, optional
        Whether to include data in the built thermodb, by default False
    **kwargs
        Additional keyword arguments.
        - ignore_state_props: Optional[List[str]]
            List of property names to ignore state during the build. By default, None.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    ComponentThermoDB : object | None
        ComponentThermoDB object used for building component thermodynamic databook as:
        - `component`: Component
            component object including name, formula, and state
        - `thermodb`: CompBuilder
            CompBuilder object including the built thermodynamic databook
        - `reference_reference`: ReferenceThermoDB
            ReferenceThermoDB object including the reference content, configs, rules, labels, and ignore settings.

    Notes
    -----
    - The `reference_content` should be a valid YAML string containing the necessary databook and table information.
    - The function utilizes the `ReferenceChecker` class to parse and validate the reference content.
    - The built `ComponentThermoDB` object includes the component details, the thermodynamic databook, and the reference configuration used.
    - The `add_label` and `check_labels` parameters help in managing the reference configuration for the component. In this context, labels defined in the reference are compared with the PyThermoDB labels (symbols) to ensure consistency.
    '''
    try:
        # LINK: start time
        if verbose:
            start_time = time.time()
            logging.info("Building component thermodb from reference...")

        # NOTE: kwargs
        ignore_state_props: Optional[List[str]] = kwargs.get(
            'ignore_state_props',
            None
        )
        # set default if None
        if ignore_state_props is None:
            ignore_state_props = []

        # SECTION: check inputs
        component_name = component.name
        component_formula = component.formula
        component_state = component.state

        # NOTE: reference source
        ReferenceChecker_ = reference_source.ReferenceChecker_
        thermodb = reference_source.thermodb
        reference_content = reference_source.reference_content
        reference = reference_source.reference

        # LINK: set include_data in config
        cfg = AppConfig(
            include_data=include_data,
            build_type='single',
            component_name=component_name,
            component_formula=component_formula,
            component_state=component_state,
        )
        # ! set config
        set_config(cfg)

        # SECTION: Reference config
        # init component reference config
        component_reference_configs = ReferenceChecker_.get_component_reference_configs(
            component_name=component_name,
            component_formula=component_formula,
            component_state=component_state,
            add_label=add_label,
            check_labels=check_labels,
            component_key=component_key,
            ignore_state_props=ignore_state_props
        )

        # NOTE: check if reference_config is a dict
        if not isinstance(component_reference_configs, dict) or not component_reference_configs:
            raise ValueError(
                f"No reference config found for component '{component_name}' in the provided reference content."
            )

        # SECTION: generate reference rules
        reference_rules = ReferenceChecker_.generate_component_reference_rules(
            reference_configs=component_reference_configs
        )

        # SECTION: build thermodb items
        # NOTE: init res
        res = {}
        # labels
        labels = []
        # ignore labels
        ignore_labels: List[str] = []
        # ignore state in property
        ignore_props: List[str] = []
        # ignore state for all properties
        ignore_component_state: bool = False
        # ignore component state check
        ignore_state_props_check: bool = False

        # NOTE: databook list
        databook_list = thermodb.list_databooks(res_format='list')
        if not isinstance(databook_list, list):
            raise TypeError("Databook list must be a list")

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

                # >> set ignore state
                if len(ignore_state_props) > 0:
                    # ! for label
                    ignore_state_props_check = ignore_state_in_prop(
                        label_,
                        ignore_state_props
                    )

                    # >> set & append to ignore labels
                    if ignore_state_props_check:
                        ignore_component_state = True
                        ignore_labels.append(str(label_))
                        ignore_props.append(str(prop_name))

            # >> check labels
            labels_ = prop_idx.get('labels', None)
            if labels_ and isinstance(labels_, dict):
                # extract labels
                for lbl_key, lbl_val in labels_.items():
                    if lbl_val and isinstance(lbl_val, str):
                        # append to labels
                        labels.append(str(lbl_val))

                # >> set ignore state
                # iterate over labels
                if len(ignore_state_props) > 0:
                    for item in labels_.values():
                        # set ignore state
                        ignore_state_props_check = ignore_state_in_prop(
                            item,
                            ignore_state_props
                        )
                        # check
                        if ignore_state_props_check:
                            ignore_component_state = True
                            ignore_labels.append(str(item))
                            ignore_props.append(str(prop_name))

            # SECTION: check component
            if check_component:
                # NOTE: check availability
                component_checker_ = ReferenceChecker_.check_component_availability(
                    component_name=component_name,
                    component_formula=component_formula,
                    component_state=component_state,
                    databook_name=databook_,
                    table_name=table_,
                    component_key=component_key,
                    ignore_component_state=ignore_component_state,
                )

                # check
                if not isinstance(component_checker_, dict):
                    raise TypeError(
                        "Component checker must be a dictionary")

                if not component_checker_[table_]:
                    continue  # skip if component is not available in the table

                # availability
                table_check = component_checker_[table_]
                if isinstance(table_check, dict):
                    availability_ = table_check.get('available', False)
                else:
                    availability_ = False

                if not availability_:
                    continue  # skip if component is not available in the table

            # SECTION: build thermodb items
            # ! create Tables [TableEquation | TableData | TableMatrixEquation | TableMatrixData]
            # NOTE: ignore state during the build if specified
            try:
                if ignore_component_state:
                    # ! set component name based on key
                    component_name_ = component_name if component_key == 'Name-State' else component_formula
                    column_name_ = 'Name' if component_key == 'Name-State' else 'Formula'

                    # ! build_thermo_property
                    item_ = thermodb.build_thermo_property(
                        [component_name_],
                        databook=databook_,
                        table=table_,
                        column_name=column_name_
                    )
                else:
                    # ! build_components_thermo_property
                    item_ = thermodb.build_components_thermo_property(
                        components=[component],
                        databook=databook_,
                        table=table_,
                        component_key=component_key
                    )

                # save
                res[prop_name] = item_
            except Exception as e:
                logging.error(
                    f"Building property '{prop_name}' for component '{component_name}' failed! {e}")
                continue

            # NOTE: reset loop vars
            if len(ignore_state_props) > 0:
                ignore_state_props_check = False
                ignore_component_state = False

        # SECTION: build component thermodb
        # NOTE: check thermodb_name
        if thermodb_name is None:
            thermodb_name = component_name
        # NOTE: check message
        if message is None:
            prop_names_list = ', '.join(
                list(component_reference_configs.keys()))
            message = f"Thermodb including {prop_names_list} for component: {component_name}"

        # NOTE: remove duplicate labels
        if labels and isinstance(labels, list):
            labels = list(set(labels))
        else:
            labels = []

        # init thermodb
        thermodb_comp = build_thermodb(
            thermodb_name=thermodb_name,
            message=message
        )

        # >> log
        if verbose:
            logging.info(
                f"Building thermodb '{thermodb_name}' including properties: {list(res.keys())} for component: {component_name}."
            )

        # check results
        if len(res) == 0:
            logger.error(
                f"No valid properties found to build the thermodb for component: {component_name}."
            )
            # <> raise error
            # raise
            return None

        # add items to thermodb
        for prop_name, prop_value in res.items():
            # add item to thermodb
            add_data_res_ = thermodb_comp.add_data(
                prop_name,
                prop_value
            )

            # >> log
            if verbose:
                if add_data_res_:
                    logging.info(
                        f"Property '{prop_name}' added successfully to thermodb '{thermodb_name}'."
                    )
                else:
                    logging.error(
                        f"Adding property '{prop_name}' to thermodb '{thermodb_name}' failed!"
                    )

        # SECTION: build and save thermodb
        if thermodb_save:
            # NOTE: check path
            thermodb_save_path = check_file_path(
                file_path=thermodb_save_path,
                default_path=None,
                create_dir=True
            )
            # NOTE: save
            save_res_ = thermodb_comp.save(
                filename=thermodb_name,
                file_path=thermodb_save_path
            )

            # >> log
            if verbose:
                if save_res_:
                    logging.info(
                        f"Thermodb '{thermodb_name}' saved successfully at '{thermodb_save_path}'."
                    )
                else:
                    logging.error(
                        f"Saving thermodb '{thermodb_name}' at '{thermodb_save_path}' failed!"
                    )
        else:
            # build
            build_res_ = thermodb_comp.build()

            # >> log
            if verbose:
                if build_res_:
                    logging.info(
                        f"Thermodb '{thermodb_name}' built successfully."
                    )
                else:
                    logging.error(
                        f"Building thermodb '{thermodb_name}' failed!"
                    )

        # SECTION: ComponentThermoDB settings
        # NOTE: reference thermodb
        reference_thermodb = ReferenceThermoDB(
            reference=reference,
            contents=[reference_content],
            configs=component_reference_configs,
            rules=reference_rules,
            labels=labels,
            ignore_labels=ignore_labels,
            ignore_props=ignore_props
        )
        # NOTE: init ComponentThermoDB
        # init ComponentThermoDB
        component_thermodb = ComponentThermoDB(
            component=component,
            thermodb=thermodb_comp,
            reference_thermodb=reference_thermodb,
        )

        # LINK: end time
        if verbose:
            end_time = time.time()
            elapsed_time = end_time - start_time
            logging.info(
                f"Component thermodb check and build completed in {elapsed_time:.2f} seconds."
            )

        # return
        return component_thermodb
    except Exception as e:
        raise Exception(f"Building {component_name} thermodb failed! {e}")
