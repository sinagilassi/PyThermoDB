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


class ReferenceContentSource:
    """
    Class to handle reference source for building thermodynamic databooks.
    """
    # SECTION: Attributes

    def __init__(
        self,
        content: str,
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
        self.reference_content = content

        try:
            if isinstance(content, str):
                # SECTION: create ReferenceChecker instance
                self.ReferenceChecker_ = ReferenceChecker(content)

                # NOTE: load all databooks
                self.databooks: List[str] = self.ReferenceChecker_.get_databook_names(
                )

                # check databooks
                if not isinstance(self.databooks, list) or not self.databooks:
                    raise ValueError(
                        "No databooks found in the reference content.")
                # SECTION: build thermodb
                # set reference
                self.reference: CustomReference = {
                    'reference': [self.reference_content]}

                self.thermodb = init(
                    custom_reference=self.reference
                )
            else:
                raise TypeError(
                    "reference_content must be a string representing the reference source."
                )
        except Exception as e:
            logger.error(f"Error initializing ReferenceChecker: {e}")
            raise


class CustomReferenceSource:
    """
    Class to handle custom reference source for building thermodynamic databooks.
    """

    def __init__(
        self,
        reference: CustomReference,
        config: Union[
            Dict[str, Dict[str, str]],
            Dict[str, ComponentConfig],
            str
        ],
        **kwargs
    ):
        """
        Initialize the CUstomReferenceSource class.

        Parameters
        ----------
        custom_reference : CustomReference
            Custom reference dictionary for external references.
        reference_config : Union[Dict[str, Dict[str, str]], str, Dict[str, ComponentConfig]]
            Dictionary containing properties of the components to be included in the thermodynamic databook.
        """
        # NOTE: custom reference
        self.reference = reference
        # NOTE: reference config
        self.reference_config = config

        try:
            # SECTION: build thermodb
            self.thermodb = init(
                custom_reference=reference
            )

        except Exception as e:
            logger.error(f"Error initializing CUstomReferenceSource: {e}")
            raise


@measure_time
def build_component_thermodb_from_reference_source(
        component: Component,
        reference_source: ReferenceContentSource,
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
    reference_source : ReferenceContentSource
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


@measure_time
def check_and_build_component_thermodb(
    component: Component,
    reference_source: CustomReferenceSource,
    component_key: Literal[
        'Name-State', 'Formula-State'
    ] = 'Formula-State',
    thermodb_name: Optional[str] = None,
    message: Optional[str] = None,
    reference_config_default_check: Optional[bool] = True,
    thermodb_save: Optional[bool] = False,
    thermodb_save_path: Optional[str] = None,
    verbose: Optional[bool] = False,
    include_data: bool = True,
    **kwargs
) -> Optional[ComponentThermoDB]:
    '''
    Build component thermodynamic databook (thermodb) including data and equations.

    Parameters
    ----------
    component : Component
        Component object to build thermodynamic databook for Which includes name, formula, and state.
    reference_source : CustomReferenceSource
        CustomReferenceSource object including the custom reference and reference config for building the thermodb.
    component_key : Literal['Name-State', 'Formula-State'], optional
        Key to identify the component in the reference content, by default 'Formula-State'
    thermodb_name : Optional[str], optional
        Name of the thermodynamic databook to be built, by default None
    message : Optional[str], optional
        A short description of the component thermodynamic databook, by default None
    reference_config_default_check : Optional[bool], optional
        Whether to perform default checks on the reference configuration, by default True
    thermodb_save : Optional[bool], optional
        Whether to save the built thermodb to a file, by default False
    thermodb_save_path : Optional[str], optional
        Path to save the built thermodb file, by default None. If None, it will save to the current directory with the name `{thermodb_name}.pkl`.
    verbose : Optional[bool], optional
        Whether to print verbose logs, by default False
    include_data : bool
        Whether to include data tables in the built thermodb, by default True
    **kwargs
        Additional keyword arguments.
        - ignore_state_props: Optional[List[str]]
            List of property names to ignore state during the build. By default, None.
        - ignore_state_all_props: Optional[bool]
            Whether to ignore state for all properties during the build. By default, False.
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
    - Property dict should contain the following format:

    ```python
    # reference config for a single component:

    # Dict[str, Dict[str, str]]
    reference_config = {
        'heat-capacity': {
            'databook': 'CUSTOM-REF-1',
            'table': 'Ideal-Gas-Molar-Heat-Capacity',
            'label': 'Cp_IG',
        },
        'vapor-pressure': {
            'databook': 'CUSTOM-REF-1',
            'table': 'Vapor-Pressure',
            'label': 'VaPr',
        },
        'general': {
            'databook': 'CUSTOM-REF-1',
            'table': 'General-Data',
            'labels': {
                'molecular-weight': 'MW',
                'critical-temperature': 'Tc',
                'critical-pressure': 'Pc',
                'acentric-factor': 'AcFa',
        },
    }

    # str yaml format
    reference_config_yaml = """
    component_id:
        property_name:
            databook: DATABOOK_NAME
            table: TABLE_NAME
            label: LABEL_NAME
            labels:
                label_key: LABEL_NAME
    """
    ```

    - Table should contain columns including `Name`, `Formula`, and `State` to identify the component. Otherwise during the check, it will raise an error.
    - ignore_state_props: List of property names to ignore state during the build. For example, if you want to ignore state for a thermo property such as vapor pressure and use only component name and formula, set `ignore_state_props=['VaPr']`.
    '''
    try:
        # LINK: start time
        if verbose:
            start_time = time.time()
            logging.info("Starting mixture thermodb check and build...")

        # NOTE: kwargs
        ignore_state_props: Optional[List[str]] = kwargs.get(
            'ignore_state_props',
            None
        )
        # set default if None
        if ignore_state_props is None:
            ignore_state_props = []

        # NOTE: check if ignore state for all properties
        ignore_state_all_props: bool = kwargs.get(
            'ignore_state_all_props',
            False
        )

        if not isinstance(ignore_state_all_props, bool):
            # logging warning
            logging.warning(
                "ignore_state_all_props must be a boolean, setting to False."
            )
            ignore_state_all_props = False

        # ! check both ignore_state_props and ignore_state_all_props
        if len(ignore_state_props) > 0:
            # set ignore_state_all_props to False
            ignore_state_all_props = False

        # NOTE: check inputs
        if not isinstance(component, Component):
            raise TypeError("component_name must be a string")

        # LINK: set include_data in config
        cfg = AppConfig(
            include_data=include_data,
            build_type='single',
            component_name=component.name,
            component_formula=component.formula,
            component_state=component.state,
        )
        # ! set config
        set_config(cfg)

        # SECTION: extract reference source
        # NOTE: reference source
        reference_config = reference_source.reference_config
        # custom reference
        custom_reference = reference_source.reference

        # SECTION: reference_config check
        if not isinstance(reference_config, (dict, str)):
            raise TypeError(
                "reference config must be a dictionary or a string")

        # SECTION: COMPONENT ID
        # set id based on key
        component_id = set_component_id(
            component=component,
            component_key=component_key
        )

        # SECTION: check if reference_config is a string
        if isinstance(reference_config, str):
            # ! init ReferenceConfig
            ReferenceConfig_ = ReferenceConfig()
            # convert to dict
            reference_config_ = \
                ReferenceConfig_.set_reference_config(
                    reference_config
                )

            # ! extract component reference config
            reference_config = look_up_component_reference_config(
                component_id=component_id,
                reference_config=reference_config_,
                reference_config_default_check=reference_config_default_check
            )

        # NOTE: check if reference_config is a dict
        if not isinstance(reference_config, dict):
            raise TypeError("reference_config must be a dictionary")

        # SECTION: build thermodb
        thermodb = init(
            custom_reference=custom_reference
        )

        # SECTION: init res
        res = {}
        # labels
        labels: List[str] = []
        # ignore state for all properties
        ignore_component_state: bool = False

        # NOTE: databook list
        databook_list = thermodb.list_databooks(res_format='list')
        # >> check
        if not isinstance(databook_list, list):
            raise TypeError("Databook list must be a list")

        # SECTION: check both databook and table
        for prop_name, prop_idx in reference_config.items():
            # property name
            prop_name = prop_name.strip()

            # ! databook
            databook_ = prop_idx.get('databook', None)
            if databook_ is None:
                raise ValueError(
                    f"Databook for property '{prop_name}' is not specified.")
            # >> check databook exists
            if is_databook_available(databook_, databook_list) is False:
                logger.error(
                    f"Databook '{databook_}' for property '{prop_name}' is not found in the databook list."
                )
                continue

            # NOTE: tables
            table_dict_ = thermodb.list_tables(
                databook=databook_,
                res_format='dict'
            )
            # check
            if not isinstance(table_dict_, dict):
                raise TypeError("Table list must be a list")

            # ! table list
            table_list_ = list(table_dict_.values())
            if not isinstance(table_list_, list) or not table_list_:
                raise TypeError("Table list must be a list")

            # ! table
            table_ = prop_idx.get('table', None)
            if table_ is None:
                raise ValueError(
                    f"Table for property '{prop_name}' is not specified.")

            # check table
            if is_table_available(table_, table_list_) is False:
                logging.error(
                    f"Table '{table_}' for property '{prop_name}' is not found in the databook '{databook_}'."
                )
                # ? skip if table is not found
                continue

            # SECTION: table info
            # ! table info
            table_info_ = thermodb.table_info(
                databook=databook_,
                table=table_,
                res_format='dict'
            )
            # check table info
            if not isinstance(table_info_, dict):
                raise TypeError("Table info must be a dictionary")

            table_data_type = table_info_.get('Type', None)
            # check
            if table_data_type == 'Matrix-Data':
                # log
                logging.warning(
                    f"Table '{table_}' for property '{prop_name}' is a matrix data table. Only single component properties are supported in this method."
                )
                continue  # skip if table is matrix data

            # ! label/labels
            # NOTE: >> check label
            label_ = prop_idx.get(
                'label', None) or prop_idx.get('symbol', None)
            # >> check
            if label_:
                # append to labels
                labels.append(str(label_))

                # >> set ignore state
                # ! for label
                if len(ignore_state_props) > 0:
                    ignore_component_state = ignore_state_in_prop(
                        label_,
                        ignore_state_props
                    )

            # NOTE: >> check labels
            labels_ = prop_idx.get(
                'labels', None) or prop_idx.get('symbols', None)
            # check
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
                        # ! for labels
                        ignore_component_state = ignore_state_in_prop(
                            item,
                            ignore_state_props
                        )
                        # check
                        if ignore_component_state:
                            break
                else:
                    ignore_component_state = False

            # >> override if ignore all state is True
            # ! for all property skip
            if ignore_state_all_props:
                ignore_component_state = True

            # NOTE: check component settings
            # check ignore state
            if ignore_component_state:
                # ! set component name based on key
                component_name_ = component.name if component_key == 'Name-State' else component.formula
                column_name_ = 'Name' if component_key == 'Name-State' else 'Formula'

                # ! check component
                component_checker_ = thermodb.check_component(
                    component_name=component_name_,
                    databook=databook_,
                    table=table_,
                    column_name=column_name_,
                    res_format='dict'
                )

            else:
                # ! check component
                component_checker_ = thermodb.is_component_available(
                    component=component,
                    databook=databook_,
                    table=table_,
                    component_key=component_key,
                    res_format='dict'
                )

            # check
            if not isinstance(component_checker_, dict):
                raise TypeError("Component checker must be a dictionary")

            if not component_checker_['availability']:
                continue  # skip if component is not available in the table

            # SECTION: build thermodb items
            # ! create Tables [TableEquation | TableData | TableMatrixEquation | TableMatrixData]

            # NOTE: ignore state during the build if specified
            try:
                if ignore_component_state:
                    # ! set component name based on key
                    # ! already set above

                    # ! build_thermo_property with component name
                    item_ = thermodb.build_thermo_property(
                        component_names=[component_name_],
                        databook=databook_,
                        table=table_,
                        column_name=column_name_,
                        query=False
                    )
                else:
                    # ! build_thermo_property with component object
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
                    f"Building property '{prop_name}' for component '{component.name} and {component.formula}' failed! {e}")
                continue

            # NOTE: reset loop vars
            # ! ignore state
            if len(ignore_state_props) > 0:
                ignore_component_state = False

        # SECTION: build component thermodb
        # NOTE: check thermodb_name
        if thermodb_name is None:
            thermodb_name = component_id

        # NOTE: check message
        if message is None:
            prop_names_list = ', '.join(list(reference_config.keys()))
            message = f"Thermodb including {prop_names_list} for component: {component_id}"

        # NOTE: init thermodb
        thermodb_comp = build_thermodb(
            thermodb_name=thermodb_name,
            message=message
        )

        # SECTION: check if res is empty
        if len(res) == 0:
            # log
            if verbose:
                logging.warning(
                    f"No properties were built for component '{component_id}'. Thermodb will not be created."
                )

            # res
            return None

        # add items to thermodb
        for prop_name, prop_value in res.items():
            # add item to thermodb
            add_data_res_ = thermodb_comp.add_data(
                prop_name,
                prop_value
            )

            # log
            if verbose:
                if add_data_res_:
                    logging.info(
                        f"Property '{prop_name}' added to thermodb '{thermodb_name}'.")
                else:
                    logging.warning(
                        f"Adding property '{prop_name}' to thermodb '{thermodb_name}' may have issues, please check the logs."
                    )

        # SECTION: build and save thermodb
        # ! save thermodb if specified
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

            # log
            if verbose:
                if save_res_:
                    logging.info(
                        f"Thermodb '{thermodb_name}' saved to {thermodb_save_path}."
                    )
                else:
                    logging.warning(
                        f"Saving thermodb '{thermodb_name}' may have issues, please check the logs."
                    )
        else:
            # build
            build_res_ = thermodb_comp.build()

            # log
            if verbose:
                if build_res_:
                    logging.info(
                        f"Thermodb '{thermodb_name}' built successfully."
                    )
                else:
                    logging.warning(
                        f"Building thermodb '{thermodb_name}' may have issues, please check the logs."
                    )

        # LINK: end time
        if verbose:
            end_time = time.time()
            elapsed_time = end_time - start_time
            logging.info(
                f"Mixture thermodb check and build completed in {elapsed_time:.2f} seconds."
            )

        # SECTION: ComponentThermoDB settings
        # NOTE: reference thermodb
        reference_thermodb = ReferenceThermoDB(
            reference=custom_reference,
            contents=[],
            configs={},
            labels=None,
            ignore_labels=None,
            ignore_props=None
        )

        # NOTE: init ComponentThermoDB
        res = ComponentThermoDB(
            component=component,
            thermodb=thermodb_comp,
            reference_thermodb=reference_thermodb,
        )

        # return
        return res
    except Exception as e:
        raise Exception(f"Building {component_id} thermodb failed! {e}")
