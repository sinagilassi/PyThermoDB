# import packages/modules
# external
from typing import Optional, Dict, List
# internal
from .config import __version__, __author__, __description__
from .docs import (
    ThermoDB, TableReference, CustomRef, CompBuilder,
    TableData, TableEquation, TableMatrixData, TableMatrixEquation
)


def desc() -> None:
    print(f'pyThermoDB v-{__version__} is a lightweight and user-friendly\
          Python package developed by {__author__} designed to provide quick access to essential \
          thermodynamic data.')


def init(custom_reference: Optional[Dict[str, List[str]]] = None) -> ThermoDB:
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


def ref(custom_reference: Optional[Dict[str, List[str]]] = None) -> TableReference:
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


def build_thermodb(thermodb_name: Optional[str] = None) -> CompBuilder:
    '''
    Build thermodb object to check and build thermodynamic data and equations
    
    Parameters
    ----------
    thermodb_name : str
        name of the thermodb object
        - `thermodb_name` : str, name of the thermodb object
    
    Returns
    -------
    CompBuilder : object
        CompBuilder object used for building thermodynamic data and equations
    '''
    try:
        # init class
        return CompBuilder(thermodb_name=thermodb_name)
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

