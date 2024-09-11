# import packages/modules
# external
import os
# internal
from .config import __version__
from .docs import SettingDatabook, TableReference, CustomRef, CompBuilder


def desc():
    print(f'pyThermoDB v-{__version__} is a lightweight and user-friendly\
          Python package designed to provide quick access to essential \
          thermodynamic data.')


def get_version():
    return __version__


def init(ref=None):
    '''
    Initialize thermodb app

    Parameters
    ----------
    ref : dict
        set-up external reference dict for databook and tables
        format ref_external = {'yml':[yml files], 'csv':[csv files]}

    Returns
    -------
    SettingDatabookC : object
        SettingDatabook object used for checking and building data and equation objects
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
            SettingDatabookC = SettingDatabook(CustomRefC)
        else:
            SettingDatabookC = SettingDatabook()
        return SettingDatabookC
    except Exception as e:
        raise Exception(f"Initializing app failed! {e}")


def ref(ref=None):
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
            TableReferenceC = TableReference(custom_ref=CustomRefC)
        else:
            # init
            TableReferenceC = TableReference()
        return TableReferenceC
    except Exception as e:
        raise Exception(f'Building reference failed! {e}')


def build_thermodb():
    '''
    Build thermodb
    '''
    try:
        # init class
        CompBuilderC = CompBuilder()
        return CompBuilderC
    except Exception as e:
        raise Exception("Building thermodb failed!, ", e)


if __name__ == '__main__':
    desc()
