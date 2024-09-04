# import packages/modules
# external
import os
# internal
from .config import __version__
from .docs import SettingDatabook
from .docs import TableReference
from .docs import CustomRef


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


def ref():
    '''
    Building references object including databook and tables to display data
    '''
    try:
        # init
        TableReferenceC = TableReference()
        return TableReferenceC
    except Exception as e:
        raise Exception(f'Building reference failed! {e}')


if __name__ == '__main__':
    desc()
