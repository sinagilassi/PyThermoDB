# import packages/modules
# external

# internal
from .config import __version__
from .docs import SettingDatabook
from .docs import TableReference


def desc():
    print(f'pyThermoDB v-{__version__} is a lightweight and user-friendly\
          Python package designed to provide quick access to essential \
          thermodynamic data.')


def get_version():
    return __version__


def init():
    '''
    Initialize thermodb app
    '''
    try:
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
