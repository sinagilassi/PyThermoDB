# import libs
from typing import List, Literal
# internal

# NOTE: api url
API_URL = "https://script.google.com/macros/s/"

# SECTION: reference config keys
REFERENCE_CONFIG_KEYS = [
    'ALL',
    'DEFAULT'
]


# SECTION: default component states
DEFAULT_COMPONENT_STATES = Literal[
    's',  # solid
    'l',  # liquid
    'g',  # gas
    'aq'  # aqueous
]
