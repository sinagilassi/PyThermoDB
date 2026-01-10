# import packages/modules
import logging
import os
from typing import (
    Optional,
    Dict,
    List,
)
from pythermodb_settings.utils import measure_time
# local
from .docs import (
    ThermoDB,
    TableReference,
)
from .builder import CompBuilder
from .loader import CustomRef
from .models import CustomReference


# NOTE: logger
logger = logging.getLogger(__name__)


@measure_time
def init(
    custom_reference: Optional[
        CustomReference | str
    ] = None,
    **kwargs,
) -> ThermoDB:
    '''
    Initialize thermodb app to check and build thermodynamic data and equations.

    Parameters
    ----------
    custom_reference : Optional[CustomReference | str], optional
        set-up external reference (custom reference) dict for databook and tables (check examples)
    **kwargs
        Additional keyword arguments.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    ThermoDB : object
        ThermoDB object used for checking and building data and equation objects

    Notes
    ------
    ### Set-up external reference dict for databook and tables

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
        # NOTE: init vars
        # check new custom ref
        check_ref = False
        # init class
        CustomRefC = None

        # SECTION: init class
        if custom_reference:
            # NOTE: check both str and dict
            if not isinstance(custom_reference, (str, dict)):
                logger.error(
                    "`custom_reference` must be a string or dictionary!")
                raise TypeError(
                    "`custom_reference` must be a string or dictionary!")

            # NOTE: check if string (yml file)
            if isinstance(custom_reference, str):
                # set dict
                custom_reference = {'reference': [custom_reference]}

            # NOTE: check dict values
            if not all(isinstance(v, list) for v in custom_reference.values()):
                logger.error(
                    "All values in `custom_reference` dictionary must be lists!")
                raise TypeError(
                    "All values in `custom_reference` dictionary must be lists!")

            # NOTE: init class
            CustomRefC = CustomRef(custom_reference)

            # NOTE: initialize reference
            check_ref = CustomRefC.init_ref()

        # SECTION: check ref
        if check_ref:
            return ThermoDB(custom_ref=CustomRefC)
        else:
            return ThermoDB()
    except Exception as e:
        raise Exception(f"Initializing app failed! {e}")


def ref(
    custom_reference: Optional[
        Dict[str, List[str]]
    ] = None
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


@measure_time
def build_thermodb(
    thermodb_name: Optional[str] = None,
    message: Optional[str] = None,
    **kwargs,
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
        # NOTE: init class
        return CompBuilder(
            thermodb_name=thermodb_name,
            message=message
        )
    except Exception as e:
        raise Exception("Building thermodb failed!, ", e)


@measure_time
def load_thermodb(
    thermodb_file: str,
    **kwargs,
) -> CompBuilder:
    '''
    Load thermodb object to read thermodynamic data and equations

    Parameters
    ----------
    thermodb_file : str
        thermodb filename path
    **kwargs
        Additional keyword arguments.
        - mode : Literal['silent', 'log', 'attach'], optional
            Mode for time measurement logging. Default is 'log'.

    Returns
    -------
    CompBuilder : object
        CompBuilder object used for loading thermodynamic data and equations
    '''
    try:
        # NOTE: check file exists
        if not os.path.isfile(thermodb_file):
            raise FileNotFoundError(f"File '{thermodb_file}' does not exist!")

        # NOTE: init class
        return CompBuilder.load(thermodb_file)
    except Exception as e:
        raise Exception("Loading thermodb failed!, ", e)
