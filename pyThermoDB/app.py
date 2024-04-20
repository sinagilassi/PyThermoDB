# import packages/modules
# external

# internal
from pyThermoDB.config import __version__


def main():
    print(f'pyThermoDB version: {__version__} is a lightweight and user-friendly Python package designed to provide quick access to essential thermodynamic data.')

def get_version():
    return __version__

if __name__ == '__main__':
    main()
