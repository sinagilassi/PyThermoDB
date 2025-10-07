# import libs
import logging
import os
from typing import (
    Optional,
    Dict,
    List,
    Union,
    Literal,
    cast
)
from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)
from pythermodb_settings.models import (
    Component,
    ReferenceThermoDB,
    ComponentConfig,
    CustomReference
)
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
    create_binary_mixture_id,
    create_mixture_ids
)
from .builder import CompBuilder
from .config import DEFAULT_COMPONENT_STATES

# NOTE: logger
logger = logging.getLogger(__name__)

# SECTION: define types


class ComponentThermoDB(BaseModel):
    """
    Model for component thermodynamic database (ThermoDB).

    Attributes
    ----------
    component: Component
        The component for which the thermodynamic database is built.
    thermodb: CompBuilder
        The thermodynamic database builder instance.
    reference_thermodb : Optional[ReferenceThermoDB]
        Reference thermodynamic database, default is None.
    """
    component: Component = Field(
        ...,
        description="The component for which the thermodynamic database is built."
    )
    thermodb: CompBuilder = Field(
        ...,
        description="The thermodynamic database builder instance."
    )
    reference_thermodb: Optional[ReferenceThermoDB] = Field(
        None, description="Reference thermodynamic database."
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='allow'
    )


class MixtureThermoDB(BaseModel):
    """
    Model for mixture thermodynamic database (ThermoDB).

    Attributes
    ----------
    components: List[Component]
        The list of components for which the thermodynamic database is built.
    thermodb: CompBuilder
        The thermodynamic database builder instance.
    reference_thermodb : Optional[ReferenceThermoDB]
        Reference thermodynamic database, default is None.
    """
    components: List[Component] = Field(
        ...,
        description="The list of components for which the thermodynamic database is built."
    )
    thermodb: CompBuilder = Field(
        ...,
        description="The thermodynamic database builder instance."
    )
    reference_thermodb: Optional[ReferenceThermoDB] = Field(
        None, description="Reference thermodynamic database."
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='allow'
    )


def build_component_thermodb(
    component_name: str,
    reference_config: Union[
        Dict[str, Dict[str, str]],
        str
    ],
    custom_reference: Optional[
        CustomReference
    ] = None,
    component_key: Literal['Name', 'Formula'] = 'Name',
    thermodb_name: Optional[str] = None,
    message: Optional[str] = None,
    reference_config_default_check: Optional[bool] = True,
    thermodb_save: Optional[bool] = False,
    thermodb_save_path: Optional[str] = None,
) -> CompBuilder:
    '''
    Build component thermodynamic databook (thermodb) including data and equations.

    Parameters
    ----------
    component_name : str
        Name of the component to build thermodynamic databook for.
    reference_config : Dict[str, Dict[str, Any]] | str
        Dictionary containing properties of the component to be included in the thermodynamic databook.
    thermodb_name : Optional[str], optional
        Name of the thermodynamic databook to be built, by default None
    custom_reference : Optional[CustomReference], optional
        Custom reference dictionary for external references, by default None
    component_key : Literal['Name', 'Formula'], optional
        Key to identify the component in the reference content, by default 'Formula'
    thermodb_name : Optional[str], optional
        Name of the thermodynamic databook to be built, by default None
    message : Optional[str], optional
        A short description of the component thermodynamic databook, by default None
    reference_config_default_check : Optional[bool], optional
        Whether to perform default checks on the reference configuration, by default None
    thermodb_save : Optional[bool], optional
        Whether to save the built thermodb to a file, by default False
    thermodb_save_path : Optional[str], optional
        Path to save the built thermodb file, by default None. If None, it will save to the current directory with the name `{thermodb_name}.pkl`.

    Returns
    -------
    CompBuilder : object
        CompBuilder object used for building component thermodynamic databook

    Notes
    -----
    1- Property dict should contain the following format:

    ```python
    # Dict[str, Dict[str, str]]
    reference_config = {
        'heat-capacity': {
            'databook': 'CUSTOM-REF-1',
            'table': 'Ideal-Gas-Molar-Heat-Capacity',
        },
        'vapor-pressure': {
            'databook': 'CUSTOM-REF-1',
            'table': 'Vapor-Pressure',
        },
        'general': {
            'databook': 'CUSTOM-REF-1',
            'table': 'General-Data',
        },
    }
    ```

    2- This method only checks component by `name`. If you want to check by formula/name and state such as `CO2-g`, `carbon dioxide-g`, use `check_and_build_component_thermodb` method.

    Examples
    --------
    ```python
    reference_config = {
        'heat-capacity': {
            'databook': 'CUSTOM-REF-1',
            'table': 'Ideal-Gas-Molar-Heat-Capacity',
        },
        'vapor-pressure': {
            'databook': 'CUSTOM-REF-1',
            'table': 'Vapor-Pressure',
        },
        'general': {
            'databook': 'CUSTOM-REF-1',
            'table': 'General-Data',
        },
    }

    # custom reference (yaml format)
    custom_reference = """
    REFERENCES:
        ...
    """

    # build thermodb for carbon dioxide
    thermodb = build_component_thermodb(
        component_name='carbon dioxide',
        reference_config=reference_config,
        custom_reference=custom_reference,
        component_key='Name',
        thermodb_name='CO2_thermodb',
        message='Thermodb for carbon dioxide',
        thermodb_save=True,
    )
    ```
    '''
    try:
        # NOTE: check inputs
        if not isinstance(component_name, str):
            raise TypeError("component_name must be a string")

        # NOTE: reference_config check
        if not isinstance(reference_config, (dict, str)):
            raise TypeError("property must be a dictionary or a string")

        # NOTE: reference_config default check
        if reference_config_default_check is None:
            reference_config_default_check = True

        # NOTE: check if reference_config is a string
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
                component_id=component_name,
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

        # init res
        res = {}

        # NOTE: databook list
        databook_list = thermodb.list_databooks(res_format='list')
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

            # NOTE: set column name based on key
            column_name_ = 'Name' if component_key == 'Name' else 'Formula'

            # NOTE: check component
            component_checker_ = thermodb.check_component(
                component_name=component_name,
                databook=databook_,
                table=table_,
                column_name=column_name_,
                res_format='dict'
            )

            # check
            if not isinstance(component_checker_, dict):
                raise TypeError("Component checker must be a dictionary")

            if not component_checker_['availability']:
                continue  # skip if component is not available in the table

            # NOTE: build thermodb items
            # ! create Tables [TableEquation | TableData | TableMatrixEquation | TableMatrixData]
            item_ = thermodb.build_thermo_property(
                component_names=[component_name],
                databook=databook_,
                table=table_,
                column_name=column_name_,
                query=False
            )

            # save
            res[prop_name] = item_

        # SECTION: build component thermodb
        # NOTE: check thermodb_name
        if thermodb_name is None:
            thermodb_name = component_name
        # NOTE: check message
        if message is None:
            prop_names_list = ', '.join(list(reference_config.keys()))
            message = f"Thermodb including {prop_names_list} for component: {component_name}"

        # init thermodb
        thermodb_comp = build_thermodb(
            thermodb_name=thermodb_name,
            message=message
        )

        # add items to thermodb
        for prop_name, prop_value in res.items():
            # add item to thermodb
            thermodb_comp.add_data(
                prop_name,
                prop_value
            )

        # SECTION: save thermodb if specified
        # NOTE: build and save
        if thermodb_save:
            # check path
            if thermodb_save_path is None:
                thermodb_save_path = os.getcwd()
            elif not os.path.isdir(thermodb_save_path):
                os.makedirs(thermodb_save_path, exist_ok=True)

            # save
            thermodb_comp.save(
                filename=thermodb_name,
                file_path=thermodb_save_path
            )
            logger.info(f"Thermodb saved to {thermodb_save_path}")
        else:
            # NOTE: build without saving
            build_res_ = thermodb_comp.build()
            # check
            if not build_res_:
                logger.warning(
                    f"Building thermodb for component '{component_name}' may have issues, please check the logs."
                )

        # return
        return thermodb_comp
    except Exception as e:
        raise Exception(f"Building {component_name} thermodb failed! {e}")


def check_and_build_component_thermodb(
    component: Component,
    reference_config: Union[
        Dict[str, Dict[str, str]],
        Dict[str, ComponentConfig],
        str
    ],
    custom_reference: Optional[
        CustomReference
    ] = None,
    component_key: Literal[
        'Name-State', 'Formula-State'
    ] = 'Formula-State',
    thermodb_name: Optional[str] = None,
    message: Optional[str] = None,
    reference_config_default_check: Optional[bool] = True,
    thermodb_save: Optional[bool] = False,
    thermodb_save_path: Optional[str] = None,
    **kwargs
) -> CompBuilder:
    '''
    Build component thermodynamic databook (thermodb) including data and equations.

    Parameters
    ----------
    component : Component
        Component object to build thermodynamic databook for Which includes name, formula, and state.
    reference_config : Dict[str, Dict[str, Any]] | str | Dict[str, ComponentConfig]
        Dictionary containing properties of the component to be included in the thermodynamic databook.
    thermodb_name : Optional[str], optional
        Name of the thermodynamic databook to be built, by default None
    custom_reference : Optional[CustomReference], optional
        Custom reference dictionary for external references, by default None
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
    **kwargs
        Additional keyword arguments.
        - ignore_state_props: Optional[List[str]]
            List of property names to ignore state during the build. By default, None.
        - ignore_state_all_props: Optional[bool]
            Whether to ignore state for all properties during the build. By default, False.

    Returns
    -------
    CompBuilder : object
        CompBuilder object used for building component thermodynamic databook

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

        # NOTE: reference_config check
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

        # add items to thermodb
        for prop_name, prop_value in res.items():
            # add item to thermodb
            thermodb_comp.add_data(
                prop_name,
                prop_value
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
            thermodb_comp.save(
                filename=thermodb_name,
                file_path=thermodb_save_path
            )
        else:
            # build
            thermodb_comp.build()

        # return
        return thermodb_comp
    except Exception as e:
        raise Exception(f"Building {component_id} thermodb failed! {e}")


def build_components_thermodb(
    component_names: List[str],
    reference_config: Union[
        Dict[str, Dict[str, str]],
        str
    ],
    custom_reference: Optional[CustomReference] = None,
    thermodb_name: Optional[str] = None,
    component_key: Literal['Name', 'Formula'] = 'Name',
    delimiter: str = '|',
    message: Optional[str] = None,
    reference_config_default_check: Optional[bool] = True,
    thermodb_save: Optional[bool] = False,
    thermodb_save_path: Optional[str] = None,
    **kwargs
) -> CompBuilder:
    '''
    Build components thermodynamic databook (thermodb) including matrix-data.

    Parameters
    ----------
    component_names : List[str]
        List of component names (binary system) to build thermodynamic databook for.
    reference_config : Dict[str, Dict[str, str]] | str
        Dictionary containing properties of the components to be included in the thermodynamic databook.
    custom_reference : Optional[CustomReference], optional
        Custom reference dictionary for external references, by default None
    thermodb_name : Optional[str], optional
        Name of the thermodynamic databook to be built, by default None
    component_key : Literal['Name', 'Formula'], optional
        Key to identify the component in the reference content, by default 'Name'
    delimiter : str, optional
        Delimiter to separate component names in mixture_id, by default '|'
    message : Optional[str], optional
        A short description of the component thermodynamic databook, by default None
    reference_config_default_check : Optional[bool], optional
        Whether to perform default checks on the reference configuration, by default True
    thermodb_save : Optional[bool], optional
        Whether to save the built thermodb to a file, by default False
    thermodb_save_path : Optional[str], optional
        Path to save the built thermodb file, by default None. If None, it will save to the current directory with the name `{thermodb_name}.pkl`.
    **kwargs
        Additional keyword arguments.

    Returns
    -------
    CompBuilder : object
        CompBuilder object used for building component thermodynamic databook

    Notes
    -----
    1- Property dict should contain the following format:

    ```python
    # Dict[str, Dict[str, str]]
    reference_config = {
        'activity-coefficient': {
            'databook': 'CUSTOM-REF-1',
            'table': 'Activity-Coefficient',
        },
    }

    # str yaml format
    reference_config_yaml = """
    mixture_id:
        property_name:
            databook: DATABOOK_NAME
            table: TABLE_NAME
    """
    ```

    2- This method should be used for binary systems only to build matrix-data thermodb. Such tables are usually used to store binary parameters for activity coefficient models (e.g., NRTL, UNIQUAC).

    3- The table should contain columns including `Name` and `Formula` to identify the components. Otherwise during the check, it will raise an error.
    4- The `state` is ignored in this method when checking for component availability in the table. Use `check_and_build_component_thermodb` method if you want to check by state such as `CO2-g`, `carbon dioxide-g`.
    '''
    try:
        # NOTE: check inputs
        if not isinstance(component_names, list):
            raise TypeError("component_name must be a list")
        if not all(isinstance(c, str) for c in component_names):
            raise TypeError("All component names must be strings")

        # ? check binary system
        if len(component_names) != 2:
            raise ValueError(
                "Only binary systems are supported, provide exactly two component names.")

        # reference_config check
        if not isinstance(reference_config, (dict, str)):
            raise TypeError("property must be a dictionary")

        # NOTE component id
        # set component id based on key
        component_idx = [c.strip() for c in component_names]

        # NOTE: check if reference_config is a string
        # >> str contains mixture_id
        if isinstance(reference_config, str):
            # ! init ReferenceConfig
            ReferenceConfig_ = ReferenceConfig()
            # convert to dict
            reference_config_ = \
                ReferenceConfig_.set_reference_config(
                    reference_config
                )

            # ! extract component reference config
            # look up
            reference_config = look_up_binary_mixture_reference_config(
                component_id_1=component_idx[0],
                component_id_2=component_idx[1],
                reference_config=reference_config_,
                reference_config_default_check=reference_config_default_check,
                delimiter=delimiter
            )

        # >> property names
        property_names = list(reference_config.keys())

        # SECTION: build thermodb
        thermodb = init(
            custom_reference=custom_reference
        )

        # init res
        res = {}

        # NOTE: databook list
        databook_list = thermodb.list_databooks(res_format='list')
        # >> check
        if not isinstance(databook_list, list):
            raise TypeError("Databook list must be a list")

        # check both databook and table
        for prop_name, prop_idx in reference_config.items():
            # property name
            prop_name = prop_name.strip()

            # ! databook
            databook_ = prop_idx.get('databook', None)
            if databook_ is None:
                raise ValueError(
                    f"Databook for property '{prop_name}' is not specified.")
            if databook_ not in databook_list:
                raise ValueError(
                    f"Databook '{databook_}' for property '{prop_name}' is not found in the databook list.")

            # tables
            table_dict_ = thermodb.list_tables(
                databook=databook_,
                res_format='dict'
            )
            # check
            if not isinstance(table_dict_, dict):
                raise TypeError("Table list must be a list")

            # table list
            table_list_ = list(table_dict_.values())
            if not isinstance(table_list_, list) or not table_list_:
                raise TypeError("Table list must be a list")

            # ! table
            table_ = prop_idx.get('table', None)
            if table_ is None:
                raise ValueError(
                    f"Table for property '{prop_name}' is not specified.")

            # check table
            if table_ not in table_list_:
                raise ValueError(
                    f"Table '{table_}' for property '{prop_name}' is not found in the databook '{databook_}'.")

            # ! table info
            table_info_ = thermodb.table_info(
                databook=databook_,
                table=table_,
                res_format='dict'
            )
            # check table info
            if not isinstance(table_info_, dict):
                raise TypeError("Table info must be a dictionary")

            # ! data type
            table_data_type = table_info_.get('Type', None)

            # >> check
            if table_data_type != 'Matrix-Data':
                # log
                logging.error(
                    f"Table '{table_}' for property '{prop_name}' is not a matrix data table."
                )
                # skip if table is not matrix data
                continue

            # SECTION: check component
            # NOTE: set column name based on key
            column_name_ = 'Name' if component_key == 'Name' else 'Formula'

            # NOTE: create query name based on column_name
            try:
                # ! check components
                component_checker_ = thermodb.check_components(
                    component_names=component_names,
                    databook=databook_,
                    table=table_,
                    column_name=column_name_,
                    res_format='dict'
                )

                # >> check
                if not isinstance(component_checker_, dict):
                    raise TypeError("Component checker must be a dictionary")

                if not component_checker_['availability']:
                    continue  # skip if component is not available in the table
            except Exception as e:
                logging.error(
                    f"Checking components '{component_names}' for property '{prop_name}' failed! {e}")
                continue

            # NOTE: build thermodb items
            try:
                # ! create Tables [TableMatrixData]
                item_ = thermodb.build_thermo_property(
                    component_names=component_names,
                    databook=databook_,
                    table=table_,
                    column_name=column_name_,
                )

                # >> save
                res[prop_name] = item_
            except Exception as e:
                logging.error(
                    f"Building property '{prop_name}' for components '{component_names}' failed! {e}")
                continue

        # SECTION: build component thermodb
        # NOTE: check thermodb_name
        if thermodb_name is None:
            thermodb_name = '-'.join(component_names)
        # NOTE: check message
        if message is None:
            prop_names_list = ', '.join(property_names)
            component_names_ = [c.strip() for c in component_names]
            message = f"Thermodb including {prop_names_list} for components: {component_names_}"

        # NOTE: init thermodb
        thermodb_comp = build_thermodb(
            thermodb_name=thermodb_name,
            message=message
        )

        # add items to thermodb
        for prop_name, prop_value in res.items():
            # add item to thermodb
            thermodb_comp.add_data(
                name=prop_name,
                value=prop_value
            )

        # SECTION: build and save thermodb
        if thermodb_save:
            # check path
            thermodb_save_path = check_file_path(
                file_path=thermodb_save_path,
                default_path=None,
                create_dir=True
            )
            # save
            thermodb_comp.save(
                filename=thermodb_name,
                file_path=thermodb_save_path
            )
        else:
            # build
            thermodb_comp.build()

        # return
        return thermodb_comp
    except Exception as e:
        raise Exception(f"Building {component_names} thermodb failed! {e}")


def check_and_build_components_thermodb(
    components: List[Component],
    reference_config: Union[
        Dict[str, Dict[str, str]],
        Dict[str, ComponentConfig],
        str
    ],
    custom_reference: Optional[CustomReference] = None,
    component_key: Literal[
        'Name-State', 'Formula-State'
    ] = 'Name-State',
    mixture_key: Literal[
        'Name', 'Formula'
    ] = 'Name',
    column_name: Optional[str] = None,
    delimiter: str = '|',
    thermodb_name: Optional[str] = None,
    message: Optional[str] = None,
    reference_config_default_check: Optional[bool] = True,
    thermodb_save: Optional[bool] = False,
    thermodb_save_path: Optional[str] = None,
    **kwargs
) -> CompBuilder:
    '''
    Check and build components thermodynamic databook (thermodb) including matrix-data.

    Parameters
    ----------
    components : List[Component]
        List of Component objects to build thermodynamic databook for. Each Component includes name, formula, and state.
    reference_config : Union[Dict[str, Dict[str, str]], str, Dict[str, ComponentConfig]]
        Dictionary containing properties of the components to be included in the thermodynamic databook.
    custom_reference : Optional[CustomReference], optional
        Custom reference dictionary for external references, by default None
    component_key : Literal['Name-State', 'Formula-State'], optional
        Key to identify the component in the reference content, by default 'Name-State'
    mixture_key : Literal['Name', 'Formula'], optional
        Key to identify the components in the mixture, by default 'Name'
        - If 'Name', it will use component names to identify the components in the mixture.
        - If 'Formula', it will use component formulas to identify the components in the mixture.
    column_name : Optional[str], optional
        Column name to identify the mixture in the table, by default None
        - If None, it will use 'Mixture' as the default column name.
    delimiter : str, optional
        Delimiter to separate component names/formulas in the mixture, by default '|'
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
    **kwargs
        Additional keyword arguments.
        - ignore_state_props: Optional[List[str]]
            List of property names to ignore state during the build. By default, None.
        - ignore_state_all_props: Optional[bool]
            Whether to ignore state for all properties during the build. By default, False.

    Returns
    -------
    CompBuilder : object
        CompBuilder object used for building component thermodynamic databook

    Notes
    -----
    1- Property dict should contain the following format:
    ```python
    # Dict[str, Dict[str, str]]
    reference_config = {
        'NRTL': {
            'databook': 'CUSTOM-REF-1',
            'table': 'Activity-Coefficient',
            'labels': {
                'g12': 'g12',
                'g21': 'g21',
                'alpha': 'alpha',
                }
        },
    }

    # or str format yaml
    reference_config_yaml = """
    mixture_id:
        property_name_1:
            databook: DATABOOK_NAME
            table: TABLE_NAME
            labels:
                label_key: LABEL_NAME
        property_name_2:
            databook: DATABOOK_NAME
            table: TABLE_NAME
            label: LABEL_NAME
    """
    ```

    2- This method should be used for binary systems only to build matrix-data thermodb. Such tables are usually used to store binary parameters for activity coefficient models (e.g., NRTL, UNIQUAC).

    3- The table should contain columns including `Name` and `Formula` to identify the components. Otherwise during the check, it will raise an error.

    4- The `state` can be considered or ignored based on the `ignore_state_props` and `ignore_state_all_props` kwargs.

    - ignore_state_props: List of property names to ignore state during the build. For example, if you want to ignore state for a thermo property such as vapor pressure and use only component name and formula, set `ignore_state_props=['VaPr']`.
    - ignore_state_all_props: Boolean to ignore state for all properties during the build. Default is False. If True, it will ignore state for all properties.

    5- The `column_name` is used to identify the mixture in the table. If None, it will use 'Mixture' as the default column name.

    6- The `mixture_key` is used to identify the components in the mixture. If 'Name', it will use component names to identify the components in the mixture. If 'Formula', it will use component formulas to identify the components in the mixture.

    7- The `delimiter` is used to separate component names/formulas in the mixture. Default is '|'.

    8- Components combination in the mixture is not order-dependent. For example, 'Water|Ethanol' is considered the same as 'Ethanol|Water'.

    9- All binary combinations of the provided components will be checked in the table. For example, if you provide components A, B, and C, the method will check for mixtures A|B, A|C, and B|C in the table.
    '''
    try:
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
        if not isinstance(components, list):
            raise TypeError("components must be a list")
        if not all(isinstance(c, Component) for c in components):
            raise TypeError("All components must be Component objects")

        # ? check at least one mixture available in the system
        if len(components) < 2:
            raise ValueError(
                "At least two components are required to form a mixture.")

        # NOTE: reference_config check
        if not isinstance(reference_config, (dict, str)):
            raise TypeError(
                "reference config must be a dictionary or a string")

        # SECTION: COMPONENT ID
        # extract component names
        component_names = [c.name.strip() for c in components]

        # >> set id based on key
        component_idx = [
            set_component_id(
                component=c,
                component_key=component_key
            ) for c in components
        ]

        # >> create mixture ids
        mixture_ids = create_mixture_ids(
            components=components,
            mixture_key=mixture_key,
            delimiter=delimiter
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
            # >> based on mixture key
            reference_config = look_up_mixture_reference_config(
                components=components,
                reference_config=reference_config_,
                reference_config_default_check=reference_config_default_check,
                mixture_key=mixture_key,
                delimiter=delimiter,
            )

        # reference_config check
        if not isinstance(reference_config, dict):
            raise TypeError("property must be a dictionary")

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

        # SECTION: set column name based on key
        column_name = 'Mixture' if column_name is None else column_name
        # >> check column name
        if not isinstance(column_name, str):
            raise TypeError("column_name must be a string")

        # NOTE: databook list
        databook_list = thermodb.list_databooks(res_format='list')
        # >> check
        if not isinstance(databook_list, list):
            raise TypeError("Databook list must be a list")

        # check both databook and table
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

            # tables
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

            # ! table info
            table_info_ = thermodb.table_info(
                databook=databook_,
                table=table_,
                res_format='dict'
            )

            # check table info
            if not isinstance(table_info_, dict):
                raise TypeError("Table info must be a dictionary")

            # ! data type
            table_data_type = table_info_.get('Type', None)
            # >> check
            if table_data_type != 'Matrix-Data':
                # log
                logging.error(
                    f"Table '{table_}' for property '{prop_name}' is not a matrix data table."
                )
                # skip if table is not matrix data
                continue

            # ! label/labels
            # NOTE: >> check labels
            labels_ = prop_idx.get(
                'labels', None) or prop_idx.get('symbols', None)
            # >> check
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

            # SECTION: ignore component state if specified
            try:
                # >> check mixture
                component_checker_ = thermodb.is_binary_mixture_available(
                    components=components,
                    databook=databook_,
                    table=table_,
                    column_name=column_name,
                    component_key=component_key,
                    mixture_key=mixture_key,
                    delimiter=delimiter,
                    ignore_component_state=ignore_component_state,
                    res_format='dict'
                )

                # check
                if not isinstance(component_checker_, dict):
                    raise TypeError("Component checker must be a dictionary")

                if not component_checker_['availability']:
                    # log
                    logging.error(
                        f"Components '{component_idx}' for property '{prop_name}' are not found in the table '{table_}' of databook '{databook_}' while setting ignore_component_state={ignore_component_state}, component_key='{component_key}', mixture_key='{mixture_key}', delimiter='{delimiter}'."
                    )
                    continue  # skip if component is not available in the table
            except Exception as e:
                logging.error(
                    f"Checking components '{component_idx}' for property '{prop_name}' failed! {e}")
                continue

            # SECTION: build thermodb items
            # ! create Tables [TableMatrixData]
            # >> build thermo based on Component object (consider state)
            try:
                item_ = thermodb.build_components_thermo_property(
                    components=components,
                    databook=databook_,
                    table=table_,
                    component_key=component_key,
                    mixture_key=mixture_key,
                    delimiter=delimiter,
                    ignore_component_state=ignore_component_state,
                    column_name=column_name,
                )

                # save
                res[prop_name] = item_
            except Exception as e:
                logging.error(
                    f"Building property '{prop_name}' for components '{component_idx}' failed! {e}")
                continue

            # NOTE: reset loop vars
            # ! ignore state
            if len(ignore_state_props) > 0:
                ignore_component_state = False

        # SECTION: build component thermodb
        # NOTE: check thermodb_name
        if thermodb_name is None:
            thermodb_name = 'mixture '+'-'.join(component_idx)

        # NOTE: check message
        if message is None:
            prop_names_list = ', '.join(list(reference_config.keys()))
            component_names_ = [c.strip() for c in component_names]
            message = f"Thermodb including {prop_names_list} for components: {component_names_}"

        # NOTE: init thermodb
        thermodb_comp = build_thermodb(
            thermodb_name=thermodb_name,
            message=message
        )

        # add items to thermodb
        for prop_name, prop_value in res.items():
            # add item to thermodb
            thermodb_comp.add_data(
                name=prop_name,
                value=prop_value
            )

        # SECTION: build and save thermodb
        if thermodb_save:
            # check path
            thermodb_save_path = check_file_path(
                file_path=thermodb_save_path,
                default_path=None,
                create_dir=True
            )
            # save
            save_res_ = thermodb_comp.save(
                filename=thermodb_name,
                file_path=thermodb_save_path
            )

            # >> log
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
            thermodb_comp.build()

        # return
        return thermodb_comp
    except Exception as e:
        raise Exception(f"Building {component_names} thermodb failed! {e}")


def check_and_build_mixture_thermodb(
    components: List[Component],
    reference_config: Union[
        Dict[str, Dict[str, str]],
        Dict[str, ComponentConfig],
        str
    ],
    custom_reference: Optional[CustomReference] = None,
    component_key: Literal[
        'Name-State', 'Formula-State'
    ] = 'Name-State',
    mixture_key: Literal[
        'Name', 'Formula'
    ] = 'Name',
    column_name: Optional[str] = None,
    delimiter: str = '|',
    mixture_names: Optional[List[str]] = None,
    thermodb_name: Optional[str] = None,
    message: Optional[str] = None,
    reference_config_default_check: Optional[bool] = True,
    thermodb_save: Optional[bool] = False,
    thermodb_save_path: Optional[str] = None,
    verbose: bool = False,
    **kwargs
) -> CompBuilder | None:
    '''
    Check and build `multi-component mixture` thermodynamic databook (thermodb) including matrix-data. The mixture is defined by a list of Component objects. For instance, three components can form a ternary mixture. Thus, the matrix table containing binary parameters for the three binary pairs will be checked and built in the thermodb.

    Parameters
    ----------
    components : List[Component]
        List of Component objects to build thermodynamic databook for. Each Component includes name, formula, and state.
    reference_config : Union[Dict[str, Dict[str, str]], str, Dict[str, ComponentConfig]]
        Dictionary containing properties of the components to be included in the thermodynamic databook.
    custom_reference : Optional[CustomReference], optional
        Custom reference dictionary for external references, by default None
    component_key : Literal['Name-State', 'Formula-State'], optional
        Key to identify the component in the reference content, by default 'Name-State'
    mixture_key : Literal['Name', 'Formula'], optional
        Key to identify the components in the mixture, by default 'Name'
        - If 'Name', it will use component names to identify the components in the mixture.
        - If 'Formula', it will use component formulas to identify the components in the mixture.
    column_name : Optional[str], optional
        Column name to identify the mixture in the table, by default None
        - If None, it will use 'Mixture' as the default column name.
    delimiter : str, optional
        Delimiter to separate component names/formulas in the mixture, by default '|'
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
    verbose : bool, optional
        Whether to enable verbose logging, by default False
    **kwargs
        Additional keyword arguments.
        - ignore_state_props: Optional[List[str]]
            List of property names to ignore state during the build. By default, None.
        - ignore_state_all_props: Optional[bool]
            Whether to ignore state for all properties during the build. By default, False.

    Returns
    -------
    CompBuilder : object | None
        CompBuilder object used for building component thermodynamic databook, or None if no valid properties were found to build the thermodb.

    Notes
    -----
    1- Property dict should contain the following format:
    ```python
    # Dict[str, Dict[str, str]]
    reference_config = {
        'NRTL': {
            'databook': 'CUSTOM-REF-1',
            'table': 'Activity-Coefficient',
            'labels': {
                'g12': 'g12',
                'g21': 'g21',
                'alpha': 'alpha',
                }
        },
    }

    # or str format yaml
    reference_config_yaml = """
    mixture_id:
        property_name_1:
            databook: DATABOOK_NAME
            table: TABLE_NAME
            labels:
                label_key: LABEL_NAME
        property_name_2:
            databook: DATABOOK_NAME
            table: TABLE_NAME
            label: LABEL_NAME
    """
    ```

    2- This method should be used for binary systems only to build matrix-data thermodb. Such tables are usually used to store binary parameters for activity coefficient models (e.g., NRTL, UNIQUAC).

    3- The table should contain columns including `Name` and `Formula` to identify the components. Otherwise during the check, it will raise an error.

    4- The `state` can be considered or ignored based on the `ignore_state_props` and `ignore_state_all_props` kwargs.

    - ignore_state_props: List of property names to ignore state during the build. For example, if you want to ignore state for a thermo property such as vapor pressure and use only component name and formula, set `ignore_state_props=['VaPr']`.
    - ignore_state_all_props: Boolean to ignore state for all properties during the build. Default is False. If True, it will ignore state for all properties.

    5- The `column_name` is used to identify the mixture in the table. If None, it will use 'Mixture' as the default column name.

    6- The `mixture_key` is used to identify the components in the mixture. If 'Name', it will use component names to identify the components in the mixture. If 'Formula', it will use component formulas to identify the components in the mixture.

    7- The `delimiter` is used to separate component names/formulas in the mixture. Default is '|'.

    8- Components combination in the mixture is not order-dependent. For example, 'Water|Ethanol' is considered the same as 'Ethanol|Water'.

    9- All binary combinations of the provided components will be checked in the table. For example, if you provide components A, B, and C, the method will check for mixtures A|B, A|C, and B|C in the table.
    '''
    try:
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
        if not isinstance(components, list):
            raise TypeError("components must be a list")
        if not all(isinstance(c, Component) for c in components):
            raise TypeError("All components must be Component objects")

        # ? check at least one mixture available in the system
        if len(components) < 2:
            raise ValueError(
                "At least two components are required to form a mixture.")

        # NOTE: reference_config check
        if not isinstance(reference_config, (dict, str)):
            raise TypeError(
                "reference config must be a dictionary or a string")

        # SECTION: COMPONENT ID
        # extract component names
        component_names = [c.name.strip() for c in components]

        # NOTE: >> set id based on key
        component_idx = [
            set_component_id(
                component=c,
                component_key=component_key
            ) for c in components
        ]

        # NOTE: >> create mixture ids
        mixture_ids = create_mixture_ids(
            components=components,
            mixture_key=mixture_key,
            delimiter=delimiter
        )

        # check mixture names are valid
        if mixture_names is not None:
            if not isinstance(mixture_names, list):
                raise TypeError("mixture_names must be a list of strings")
            if not all(isinstance(m, str) for m in mixture_names):
                raise TypeError("All mixture names must be strings")
            # strip whitespace
            mixture_names = [m.strip() for m in mixture_names]

            # mixture std
            mixture_names_std = []

            # standardize mixture names
            for i in range(len(mixture_names)):
                # split by delimiter
                parts = [
                    part.strip() for part in mixture_names[i].split(delimiter) if part.strip() != ''
                ]
                # sort parts
                parts_sorted = sorted(parts)
                # join back
                mixture_name_std = delimiter.join(parts_sorted)
                mixture_names_std.append(mixture_name_std)

        # NOTE: mixture type
        mixture_type = 'BINARY' if len(components) == 2 else 'MULTI-COMPONENT'

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
            # >> based on mixture key
            reference_config = look_up_mixture_reference_config(
                components=components,
                reference_config=reference_config_,
                reference_config_default_check=reference_config_default_check,
                mixture_key=mixture_key,
                delimiter=delimiter,
            )

        # reference_config check
        if not isinstance(reference_config, dict):
            raise TypeError("property must be a dictionary")

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

        # SECTION: set column name based on key
        column_name = 'Mixture' if column_name is None else column_name
        # >> check column name
        if not isinstance(column_name, str):
            raise TypeError("column_name must be a string")

        # NOTE: databook list
        databook_list = thermodb.list_databooks(res_format='list')
        # >> check
        if not isinstance(databook_list, list):
            raise TypeError("Databook list must be a list")

        # check both databook and table
        for prop_name, prop_idx in reference_config.items():
            # ! property name
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

            # ! tables
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

            # ! table info
            table_info_ = thermodb.table_info(
                databook=databook_,
                table=table_,
                res_format='dict'
            )

            # check table info
            if not isinstance(table_info_, dict):
                raise TypeError("Table info must be a dictionary")

            # ! data type
            table_data_type = table_info_.get('Type', None)
            # >> check
            if table_data_type != 'Matrix-Data':
                # log
                logging.error(
                    f"Table '{table_}' for property '{prop_name}' is not a matrix data table."
                )
                # skip if table is not matrix data
                continue

            # ! label/labels
            # NOTE: >> check labels
            labels_ = prop_idx.get('labels', None) or \
                prop_idx.get('symbols', None)
            # >> check
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

            # SECTION: ignore component state if specified
            try:
                # NOTE: binary mixture only
                if mixture_type == 'BINARY':
                    # >> check mixture::binary
                    mixture_checker_ = thermodb.is_binary_mixture_available(
                        components=components,
                        databook=databook_,
                        table=table_,
                        column_name=column_name,
                        component_key=component_key,
                        mixture_key=mixture_key,
                        delimiter=delimiter,
                        ignore_component_state=ignore_component_state,
                        res_format='dict'
                    )
                elif mixture_type == 'MULTI-COMPONENT':
                    # >> check mixture::multi-component
                    mixtures_checker_ = thermodb.check_mixtures_availability(
                        components=components,
                        databook=databook_,
                        table=table_,
                        mixture_names=mixture_names,
                        column_name=column_name,
                        component_key=component_key,
                        mixture_key=mixture_key,
                        delimiter=delimiter,
                        ignore_component_state=ignore_component_state,
                        res_format='dict'
                    )

                    # >> check availability for all binary pairs
                    if not isinstance(mixtures_checker_, dict):
                        raise TypeError(
                            "Mixtures checker must be a dictionary."
                        )

                    # NOTE: overall availability
                    overall_availability = []

                    # >> iterate over mixtures
                    for mix_id, mix_check in mixtures_checker_.items():
                        if not isinstance(mix_check, dict):
                            raise TypeError(
                                f"Mixture checker for mixture '{mix_id}' must be a dictionary."
                            )

                        # check availability
                        if mix_check['availability'] is True:
                            overall_availability.append(True)
                        else:
                            overall_availability.append(False)

                            # >> log
                            if verbose:
                                logging.warning(
                                    f"Mixture '{mix_id}' for property '{prop_name}' is not found in the table '{table_}' of databook '{databook_}' while setting ignore_component_state={ignore_component_state}, component_key='{component_key}', mixture_key='{mixture_key}', delimiter='{delimiter}'."
                                )

                    # >> set overall availability
                    mixture_checker_ = {
                        'availability': all(overall_availability)
                    }

                else:
                    raise ValueError(
                        f"Mixture type '{mixture_type}' is not supported."
                    )

                # check
                if not isinstance(mixture_checker_, dict):
                    raise TypeError("mixture checker must be a dictionary.")

                if not mixture_checker_['availability']:
                    # log
                    logging.error(
                        f"Components '{component_idx}' for property '{prop_name}' are not found in the table '{table_}' of databook '{databook_}' while setting ignore_component_state={ignore_component_state}, component_key='{component_key}', mixture_key='{mixture_key}', delimiter='{delimiter}'."
                    )
                    continue  # skip if component is not available in the table
            except Exception as e:
                logging.error(
                    f"Checking components '{component_idx}' for property '{prop_name}' failed! {e}")
                continue

            # SECTION: build thermodb items
            # ! create Tables [TableMatrixData]
            # >> build thermo based on Component object (consider state)
            try:
                item_ = thermodb.build_components_thermo_property(
                    components=components,
                    databook=databook_,
                    table=table_,
                    component_key=component_key,
                    mixture_key=mixture_key,
                    delimiter=delimiter,
                    ignore_component_state=ignore_component_state,
                    column_name=column_name,
                    mixture_names=mixture_names
                )

                # save
                res[prop_name] = item_
            except Exception as e:
                logging.error(
                    f"Building property '{prop_name}' for components '{component_idx}' failed! {e}")
                continue

            # NOTE: reset loop vars
            # ! ignore state
            if len(ignore_state_props) > 0:
                ignore_component_state = False

        # SECTION: build component thermodb
        # NOTE: check thermodb_name
        if thermodb_name is None:
            thermodb_name = 'mixture '+'-'.join(component_idx)

        # NOTE: check message
        if message is None:
            prop_names_list = ', '.join(list(reference_config.keys()))
            component_names_ = [c.strip() for c in component_names]
            message = f"Thermodb including {prop_names_list} for components: {component_names_}"

        # SECTION: thermodb configuration
        # >> check results
        if len(res) == 0:
            logger.error(
                f"No valid properties found to build the thermodb for components: {component_names}."
            )
            return None

        # NOTE: init thermodb
        thermodb_comp = build_thermodb(
            thermodb_name=thermodb_name,
            message=message
        )

        # >> log
        if verbose:
            logging.info(
                f"Building thermodb '{thermodb_name}' including properties: {list(res.keys())} for components: {component_names}."
            )

        # add items to thermodb
        for prop_name, prop_value in res.items():
            # add item to thermodb
            add_data_res_ = thermodb_comp.add_data(
                name=prop_name,
                value=prop_value
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
            # check path
            thermodb_save_path = check_file_path(
                file_path=thermodb_save_path,
                default_path=None,
                create_dir=True
            )
            # save
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

        # return
        return thermodb_comp
    except Exception as e:
        raise Exception(f"Building {component_names} thermodb failed! {e}")


def build_component_thermodb_from_reference(
    component_name: str,
    component_formula: str,
    component_state: str,
    reference_content: str,
    component_key: Literal[
        'Name-State', 'Formula-State'
    ] = 'Formula-State',
    add_label: Optional[bool] = True,
    check_labels: Optional[bool] = True,
    thermodb_name: Optional[str] = None,
    message: Optional[str] = None,
    thermodb_save: Optional[bool] = False,
    thermodb_save_path: Optional[str] = None,
    **kwargs
) -> ComponentThermoDB:
    '''
    Build component thermodynamic databook (thermodb) including data and equations.

    Parameters
    ----------
    component_name : str
        Name of the component to build thermodynamic databook for.
    component_formula : str
        Chemical formula of the component.
    component_state : str
        Physical state of the component (e.g., 'liquid', 'gas').
    reference_content : str
        String content of the reference (YAML format) containing databook and tables.
    component_key : Literal['Name-State', 'Formula-State'], optional
        Key to identify the component in the reference content, by default 'Formula-State'
    add_label : Optional[bool], optional
        Whether to add labels to the component reference config, by default True
    check_labels : Optional[bool], optional
        Whether to check labels in the component reference config, by default True
    thermodb_name : Optional[str], optional
        Name of the thermodynamic databook to be built, by default None
    message : Optional[str], optional
        A short description of the component thermodynamic databook, by default None
    thermodb_save : Optional[bool], optional
        Whether to save the built thermodb to a file, by default False
    thermodb_save_path : Optional[str], optional
        Path to save the built thermodb file, by default None. If None, it will save to the current directory with the name `{thermodb_name}.pkl`.
    **kwargs
        Additional keyword arguments.
        - ignore_state_props: Optional[List[str]]
            List of property names to ignore state during the build. By default, None.

    Returns
    -------
    ComponentThermoDB : object
        ComponentThermoDB object used for building component thermodynamic databook

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
            'ignore_state_props',
            None
        )
        # set default if None
        if ignore_state_props is None:
            ignore_state_props = []

        # NOTE: check inputs
        if not isinstance(component_name, str):
            raise TypeError("component_name must be a string")
        if not isinstance(component_formula, str):
            raise TypeError("component_formula must be a string")
        if not isinstance(component_state, str):
            raise TypeError("component_state must be a string")

        # NOTE: check component_state
        component_state = cast(DEFAULT_COMPONENT_STATES, component_state)

        # init component
        component_ = Component(
            name=component_name,
            formula=component_formula,
            state=component_state,
        )

        # SECTION: create ReferenceChecker instance
        ReferenceChecker_ = ReferenceChecker(reference_content)

        # NOTE: load all databooks
        databooks: List[str] = ReferenceChecker_.get_databook_names()

        # check databooks
        if not isinstance(databooks, list) or not databooks:
            raise ValueError("No databooks found in the reference content.")

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

        # SECTION: build thermodb
        # set reference
        reference: CustomReference = {'reference': [reference_content]}

        thermodb = init(
            custom_reference=reference
        )

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

            # NOTE: check component
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
                raise TypeError("Component checker must be a dictionary")

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
                        components=[component_],
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

        # add items to thermodb
        for prop_name, prop_value in res.items():
            # add item to thermodb
            thermodb_comp.add_data(
                prop_name,
                prop_value
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
            thermodb_comp.save(
                filename=thermodb_name,
                file_path=thermodb_save_path
            )
        else:
            # build
            thermodb_comp.build()

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
            component=component_,
            thermodb=thermodb_comp,
            reference_thermodb=reference_thermodb,
        )

        # return
        return component_thermodb
    except Exception as e:
        raise Exception(f"Building {component_name} thermodb failed! {e}")


def build_components_thermodb_from_reference(
    components: List[Component],
    reference_content: str,
    component_key: Literal[
        'Name-State', 'Formula-State'
    ] = 'Name-State',
    mixture_key: Literal[
        'Name', 'Formula'
    ] = 'Name',
    delimiter: str = '|',
    add_label: Optional[bool] = True,
    check_labels: Optional[bool] = True,
    thermodb_name: Optional[str] = None,
    message: Optional[str] = None,
    thermodb_save: Optional[bool] = False,
    thermodb_save_path: Optional[str] = None,
    **kwargs
):
    '''
    Build components (binary mixture) thermodynamic databook (thermodb) including matrix-data.

    Parameters
    ----------
    components : List[Component]
        List of two Component objects to build thermodynamic databook for. Each Component includes name, formula, and state.
    reference_content : str
        String content of the reference (YAML format) containing databook and tables.
    component_key : Literal['Name-State', 'Formula-State'], optional
        Key to identify the component in the reference content, by default 'Name-State'
    mixture_key : Literal['Name', 'Formula'], optional
        Key to identify the components in the mixture, by default 'Name'
        - If 'Name', it will use component names to identify the components in the mixture.
        - If 'Formula', it will use component formulas to identify the components in the mixture.
    delimiter : str, optional
        Delimiter to separate component names/formulas in the mixture, by default '|'
    add_label : Optional[bool], optional
        Whether to add labels to the component reference config, by default True
    check_labels : Optional[bool], optional
        Whether to check labels in the component reference config, by default True
    thermodb_name : Optional[str], optional
        Name of the thermodynamic databook to be built, by default None
    message : Optional[str], optional
        A short description of the component thermodynamic databook, by default None
    thermodb_save : Optional[bool], optional
        Whether to save the built thermodb to a file, by default False
    thermodb_save_path : Optional[str], optional
        Path to save the built thermodb file, by default None. If None, it will save to the current directory with the name `{thermodb_name}.pkl`.
    **kwargs
        Additional keyword arguments.
        - delimiter: str
            Delimiter to separate component names in mixture_id, by default '|'
        - mixture_key: Literal['Name', 'Formula']
            Key to identify the mixture property in the reference content, by default 'Name'
        - ignore_state_props: Optional[List[str]]
            List of property names to ignore state during the build. By default, None.

    Returns
    -------
    MixtureThermoDB : object
        MixtureThermoDB object used for building binary mixture thermodynamic databook

    Notes
    -----
    - The `reference_content` should be a valid YAML string containing the necessary databook and table information.
    - The function utilizes the `ReferenceChecker` class to parse and validate the reference content.
    - The built `ComponentThermoDB` object includes the component details, the thermodynamic databook, and the reference configuration used.
    - The `add_label` and `check_labels` parameters help in managing the reference configuration for the component. In this context, labels defined in the reference are compared with the PyThermoDB labels (symbols) to ensure consistency.
    '''
    try:
        # SECTION: kwargs
        ignore_state_props: Optional[List[str]] = kwargs.get(
            'ignore_state_props',
            None
        )
        # set default if None
        if ignore_state_props is None:
            ignore_state_props = []

        # NOTE: check inputs
        if not isinstance(components, list):
            raise TypeError("components must be a list")

        if not all(isinstance(c, Component) for c in components):
            raise TypeError("All components must be Component objects")

        # create binary system
        if len(components) != 2:
            raise ValueError(
                "Only binary systems are supported, provide exactly two components."
            )

        # ! >> mixture
        mixture_id = create_binary_mixture_id(
            component_1=components[0],
            component_2=components[1],
            mixture_key=mixture_key,
            delimiter=delimiter
        )

        # SECTION: create ReferenceChecker instance
        ReferenceChecker_ = ReferenceChecker(reference_content)

        # NOTE: load all databooks
        databooks: List[str] = ReferenceChecker_.get_databook_names()

        # check databooks
        if not isinstance(databooks, list) or not databooks:
            raise ValueError("No databooks found in the reference content.")

        # init component reference config
        component_reference_configs = ReferenceChecker_.get_binary_mixture_reference_configs(
            components=components,
            add_label=add_label,
            check_labels=check_labels,
            component_key=component_key,
            mixture_key=mixture_key,
            delimiter=delimiter,
            ignore_state_props=ignore_state_props
        )

        # NOTE: check if reference_config is a dict
        if not isinstance(component_reference_configs, dict) or not component_reference_configs:
            raise ValueError(
                f"No reference config found for '{mixture_id}' in the provided reference content."
            )

        # SECTION: generate reference rules (link)
        reference_rules = ReferenceChecker_.generate_binary_mixture_reference_rules(
            reference_configs=component_reference_configs
        )

        # SECTION: build thermodb
        # set reference
        reference: CustomReference = {'reference': [reference_content]}

        thermodb = init(
            custom_reference=reference
        )

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
            mixture_checker_ = ReferenceChecker_.check_binary_mixture_availability(
                components=components,
                databook_name=databook_,
                table_name=table_,
                component_key=component_key,
                mixture_key=mixture_key,
                delimiter=delimiter,
                ignore_component_state=ignore_component_state,
                ignore_state_props=ignore_state_props
            )

            # check
            if not isinstance(mixture_checker_, dict):
                raise TypeError("Mixture checker must be a dictionary")

            if not mixture_checker_[table_]:
                continue  # skip if component is not available in the table

            # availability
            table_check = mixture_checker_[table_]
            if isinstance(table_check, dict):
                availability_ = table_check.get('available', False)
            else:
                availability_ = False

            if not availability_:
                continue  # skip if component is not available in the table

            # SECTION: build thermodb items
            # ! create Tables [TableMatrixData]
            # NOTE: ignore state during the build if specified
            try:
                # ! build_components_thermo_property
                item_ = thermodb.build_components_thermo_property(
                    components=components,
                    databook=databook_,
                    table=table_,
                    component_key=component_key,
                    mixture_key=mixture_key,
                    delimiter=delimiter,
                    ignore_component_state=ignore_component_state,
                    column_name=None
                )

                # save
                res[prop_name] = item_
            except Exception as e:
                logging.error(
                    f"Building property '{prop_name}' for mixture '{mixture_id}' failed! {e}")
                continue

            # NOTE: reset loop vars
            if len(ignore_state_props) > 0:
                ignore_state_props_check = False
                ignore_component_state = False

        # SECTION: build components thermodb
        # NOTE: check thermodb_name
        if thermodb_name is None:
            thermodb_name = 'mixture '+'-'.join([c.name for c in components])
        # NOTE: check message
        if message is None:
            prop_names_list = ', '.join(
                list(component_reference_configs.keys()))
            message = f"Thermodb including {prop_names_list} for mixture: {mixture_id}"

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

        # add items to thermodb
        for prop_name, prop_value in res.items():
            # add item to thermodb
            thermodb_comp.add_data(
                prop_name,
                prop_value
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

            # log
            if save_res_:
                logging.info(
                    f"Mixture thermodb '{thermodb_name}' saved successfully at '{thermodb_save_path}'."
                )
            else:
                logging.warning(
                    f"Saving mixture thermodb '{thermodb_name}' at '{thermodb_save_path}' failed."
                )
        else:
            # build
            thermodb_comp.build()

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
        component_thermodb = MixtureThermoDB(
            components=components,
            thermodb=thermodb_comp,
            reference_thermodb=reference_thermodb,
        )

        # return
        return component_thermodb
    except Exception as e:
        raise Exception(f"Building {mixture_id} thermodb failed! {e}")
