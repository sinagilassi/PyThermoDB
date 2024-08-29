# import packages/modules
# external

# internal
from .config import __version__
from .docs import SettingDatabook


def desc():
    print(f'pyThermoDB v-{__version__} is a lightweight and user-friendly\
          Python package designed to provide quick access to essential \
          thermodynamic data.')


def get_version():
    return __version__


def thermo_databook():
    '''
    return thermodynamics databook reference
    '''
    SettingDatabookC = SettingDatabook()
    return SettingDatabookC


if __name__ == '__main__':
    desc()
