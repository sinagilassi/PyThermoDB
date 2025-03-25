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


def get_version() -> str:
    return __version__


def init(ref: Optional[Dict[str, List[str]]] = None) -> ThermoDB:
    '''
    Initialize thermodb app to check and build thermodynamic data and equations.

    Parameters
    ----------
    ref : dict
        set-up external reference dict for databook and tables (check examples)

    Returns
    -------
    ThermoDB : object
        ThermoDB object used for checking and building data and equation objects
    
    Notes
    ------
    ### Set-up external reference dict for databook and tables
    
    - format ref_external = {'yml':[yml files], 'csv':[csv files]} or
    - format ref_external = {'reference':[yml files], 'tables':[csv files]} 
    
    ### Examples
    
    ```python
    # custom ref
    ref = {
    'reference': [yml_path],
    'tables': [csv_path_1, csv_path_2]
    }
    
    # init app
    tdb = ptdb.init(ref=ref)
    ```
    '''
    try:
        # check new custom ref
        check_ref = False
        if ref:
            CustomRefC = CustomRef(ref)
            # check ref
            check_ref = CustomRefC.init_ref()

        # check
        if check_ref:
            return ThermoDB(CustomRefC)
        else:
            return ThermoDB()
    except Exception as e:
        raise Exception(f"Initializing app failed! {e}")


def ref(ref=None) -> TableReference:
    '''
    Building references object including databook and tables to display data

    Parameters
    ----------
    ref : dict
        set-up external reference dict for databook and tables
        format ref_external = {'yml':[yml files], 'csv':[csv files]}

    Returns
    -------
    TableReferenceC : object
        TableReference object used for checking references
    '''
    try:
        # check new custom ref
        check_ref = False
        if ref:
            CustomRefC = CustomRef(ref)
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


def build_thermodb() -> CompBuilder:
    '''
    Build thermodb
    '''
    try:
        # init class
        CompBuilderC = CompBuilder()
        return CompBuilderC
    except Exception as e:
        raise Exception("Building thermodb failed!, ", e)


def load_thermodb(thermodb_file: str) -> CompBuilder:
    '''
    Load thermodb

    Parameters
    ----------
    thermodb_file : str
        filename path

    Returns
    -------
    CompBuilderC : object
        CompBuilder object
    '''
    try:
        # init class
        CompBuilderC = CompBuilder.load(thermodb_file)
        return CompBuilderC
    except Exception as e:
        raise Exception("Loading thermodb failed!, ", e)


if __name__ == '__main__':
    desc()
