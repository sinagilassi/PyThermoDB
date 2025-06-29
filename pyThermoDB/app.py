# import packages/modules
from typing import (
    Optional,
    Dict,
    List,
    Union
)
# internal
from .docs import (
    ThermoDB,
    TableReference,
    CustomRef,
    CompBuilder,
)
from .references import ReferenceConfig


def init(
    custom_reference: Optional[Dict[str, List[str]]] = None
) -> ThermoDB:
    '''
    Initialize thermodb app to check and build thermodynamic data and equations.

    Parameters
    ----------
    custom_reference : dict
        set-up external reference (custom reference) dict for databook and tables (check examples)

    Returns
    -------
    ThermoDB : object
        ThermoDB object used for checking and building data and equation objects

    Notes
    ------
    ### Set-up external reference dict for databook and tables

    - `format ref_external = {'yml':[yml files], 'csv':[csv files]}`
    - `format ref_external = {'reference':[yml files], 'tables':[csv files]}`

    ### Examples

    ```python
    # custom ref
    custom_reference = {
    'reference': [yml_path],
    'tables': [csv_path_1, csv_path_2]
    }

    # init app
    tdb = ptdb.init(custom_reference=custom_reference)
    ```
    '''
    try:
        # check new custom ref
        check_ref = False
        if custom_reference:
            CustomRefC = CustomRef(custom_reference)
            # check ref
            check_ref = CustomRefC.init_ref()

        # check
        if check_ref:
            return ThermoDB(CustomRefC)
        else:
            return ThermoDB()
    except Exception as e:
        raise Exception(f"Initializing app failed! {e}")


def ref(
    custom_reference: Optional[Dict[str, List[str]]] = None
) -> TableReference:
    '''
    Checking references (custom reference) object including databook and tables to display data

    Parameters
    ----------
    custom_reference : dict
        set-up external reference dict for databook and tables, format `ref_external = {'yml':[yml files], 'csv':[csv files]}`

    Returns
    -------
    TableReferenceC : object
        TableReference object used for checking references

    Notes
    ------
    ### Check external reference dict for databook and tables

    - `format ref_external = {'yml':[yml files], 'csv':[csv files]}`
    - `format ref_external = {'reference':[yml files], 'tables':[csv files]}`

    ### Examples

    ```python
    # custom ref
    custom_reference = {
    'reference': [yml_path],
    'tables': [csv_path_1, csv_path_2]
    }

    # init app
    tdb = ptdb.ref(custom_reference=custom_reference)
    ```
    '''
    try:
        # check new custom ref
        check_ref = False
        if custom_reference:
            CustomRefC = CustomRef(custom_reference)
            # check ref
            check_ref = CustomRefC.init_ref()

        # check
        if check_ref:
            return TableReference(custom_ref=CustomRefC)
        else:
            # init
            return TableReference()

    except Exception as e:
        raise Exception(f'Building reference failed! {e}')


def build_thermodb(
    thermodb_name: Optional[str] = None,
    message: Optional[str] = None
) -> CompBuilder:
    '''
    Build thermodb object to check and build thermodynamic data and equations

    Parameters
    ----------
    thermodb_name : str
        name of the thermodb object
        - `thermodb_name` : str, name of the thermodb object
    message : str, optional
        a short description of the thermodb object, by default None

    Returns
    -------
    CompBuilder : object
        CompBuilder object used for building thermodynamic data and equations
    '''
    try:
        # init class
        return CompBuilder(thermodb_name=thermodb_name, message=message)
    except Exception as e:
        raise Exception("Building thermodb failed!, ", e)


def load_thermodb(thermodb_file: str) -> CompBuilder:
    '''
    Load thermodb object to read thermodynamic data and equations

    Parameters
    ----------
    thermodb_file : str
        filename path

    Returns
    -------
    CompBuilder : object
        CompBuilder object used for loading thermodynamic data and equations
    '''
    try:
        # init class
        return CompBuilder.load(thermodb_file)
    except Exception as e:
        raise Exception("Loading thermodb failed!, ", e)


def build_component_thermodb(
    component_name: str,
    reference_config: Union[Dict[str, Dict[str, str]], str],
    thermodb_name: Optional[str] = None,
    custom_reference: Optional[Dict[str, List[str]]] = None,
    message: Optional[str] = None
):
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
    custom_reference : Optional[Dict[str, List[str]]], optional
        Custom reference dictionary for external references, by default None
    message : Optional[str], optional
        A short description of the component thermodynamic databook, by default None

    Notes
    -----
    Property dict should contain the following format:

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
    ```
    '''
    try:
        # NOTE: check inputs
        if not isinstance(component_name, str):
            raise TypeError("component_name must be a string")

        # reference_config check
        if not isinstance(reference_config, (dict, str)):
            raise TypeError("property must be a dictionary or a string")

        # NOTE: check if reference_config is a string
        if isinstance(reference_config, str):
            # ! init ReferenceConfig
            ReferenceConfig_ = ReferenceConfig()
            # convert to dict
            reference_config = \
                ReferenceConfig_.set_reference_config(
                    reference_config
                )

            # SECTION: build thermodb
        thermodb = init(custom_reference=custom_reference)

        # init res
        res = {}

        # NOTE: databook list
        databook_list = thermodb.list_databooks(res_format='list')
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
                databook=databook_, res_format='dict')
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

            # NOTE: check component
            component_checker_ = thermodb.check_component(
                component_name=component_name,
                databook=databook_,
                table=table_,
                res_format='dict'
            )

            # check
            if not isinstance(component_checker_, dict):
                raise TypeError("Component checker must be a dictionary")

            if not component_checker_['availability']:
                continue  # skip if component is not available in the table

            # NOTE: build thermodb items
            item_ = thermodb.build_thermo_property(
                [component_name],
                databook_,
                table_,
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

        # NOTE: build
        thermodb_comp.build()

        # return
        return thermodb_comp

        # SECTION: init
    except Exception as e:
        raise Exception(f"Building {component_name} thermodb failed! {e}")


def build_components_thermodb(
    component_names: List[str],
    reference_config: Dict[str, Dict[str, str]],
    thermodb_name: Optional[str] = None,
    custom_reference: Optional[Dict[str, List[str]]] = None,
    message: Optional[str] = None
):
    '''
    Build components thermodynamic databook (thermodb) including matrix-data.

    Parameters
    ----------
    component_names : List[str]
        List of component names (binary system) to build thermodynamic databook for.
    reference_config : Dict[str, Dict[str, Any]]
        Dictionary containing properties of the components to be included in the thermodynamic databook.
    thermodb_name : Optional[str], optional
        Name of the thermodynamic databook to be built, by default None
    custom_reference : Optional[Dict[str, List[str]]], optional
        Custom reference dictionary for external references, by default None
    message : Optional[str], optional
        A short description of the component thermodynamic databook, by default None

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
        if not isinstance(reference_config, dict):
            raise TypeError("property must be a dictionary")

        # property names
        property_names = list(reference_config.keys())

        # SECTION: build thermodb
        thermodb = init(custom_reference=custom_reference)

        # init res
        res = {}

        # NOTE: databook list
        databook_list = thermodb.list_databooks(res_format='list')
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
                databook=databook_, res_format='dict')
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

            table_data_type = table_info_.get('Type', None)
            # check
            if table_data_type != 'Matrix-Data':
                raise ValueError(
                    f"Table '{table_}' for property '{prop_name}' is not a matrix data table.")

            # NOTE: check component
            component_checker_ = thermodb.check_component(
                component_name=component_names,
                databook=databook_,
                table=table_,
                res_format='dict'
            )

            # check
            if not isinstance(component_checker_, dict):
                raise TypeError("Component checker must be a dictionary")

            if not component_checker_['availability']:
                continue  # skip if component is not available in the table

            # NOTE: build thermodb items
            item_ = thermodb.build_thermo_property(
                component_names,
                databook_,
                table_,
            )

            # save
            res[prop_name] = item_

        # SECTION: build component thermodb
        # NOTE: check thermodb_name
        if thermodb_name is None:
            thermodb_name = '-'.join(component_names)
        # NOTE: check message
        if message is None:
            prop_names_list = ', '.join(property_names)
            component_names_ = [c.strip() for c in component_names]
            message = f"Thermodb including {prop_names_list} for components: {component_names_}"

        # init thermodb
        thermodb_comp = build_thermodb(
            thermodb_name=thermodb_name,
            message=message
        )

        # add items to thermodb
        for prop_name, prop_value in res.items():
            # add item to thermodb
            thermodb_comp.add_data(
                prop_name, prop_value
            )

        # NOTE: build
        thermodb_comp.build()
        # return
        return thermodb_comp
    except Exception as e:
        raise Exception(f"Building {component_names} thermodb failed! {e}")
