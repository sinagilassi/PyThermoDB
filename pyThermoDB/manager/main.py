# import libs
from typing import Dict, Any, List, Optional
# locals
from ..utils import EquationParser
from ..models import EquationDefinition


def parse_equation_body(
    equation_body: str | Dict[str, Any],
    key_names: Optional[List[str]] = None
) -> List[EquationDefinition]:
    '''
    Parse equation body string into structured dictionary (EquationDefinition).

    Parameters
    ----------
    equation_body : str or Dict
        The equation body string to parse.
    key_names : List[str], optional
        Custom key names for the parsed dictionary, by default None. It use default key names as ['id', 'body', 'args', 'parms', 'return'].

    Returns
    -------
    list[EquationDefinition]
        A list of parsed equations in structured format.

    Notes
    -----
    Example equation with structured format:

    ```python
    eq1 = {
    'EQ-1': {
        'BODY': [
            "parms['C1 | C1 | 1'] = parms['C1 | C1 | 1']/1",
            "parms['C2 | C2 | 1'] = parms['C2 | C2 | 1']/1",
            "parms['C3 | C3 | 1'] = parms['C3 | C3 | 1']/1",
            "parms['C4 | C4 | 1'] = parms['C4 | C4 | 1']/1",
            "parms['C5 | C5 | 1'] = parms['C5 | C5 | 1']/1",
            "res['vapor-pressure | VaPr | Pa'] = math.exp(parms['C1 | C1 | 1'] + parms['C2 | C2 | 1']/args['temperature | T | K'] + parms['C3 | C3 | 1']*math.log(args['temperature | T | K']) + parms['C4 | C4 | 1']*(args['temperature | T | K']**parms['C5 | C5 | 1']))"
        ],
        'BODY-INTEGRAL': 'None',
        'BODY-FIRST-DERIVATIVE': 'None',
        'BODY-SECOND-DERIVATIVE': 'None'
        }
    }

    eq2 = {
    'id': 0,
    'body': [
        "parms['C1'] = parms['C1']/1",
        "parms['C2'] = parms['C2']/1",
        "parms['C3'] = parms['C3']/1",
        "parms['C4'] = parms['C4']/1",
        "parms['C5'] = parms['C5']/1",
        "res = math.exp(parms['C1'] + parms['C2']/args['T'] + parms['C3']*math.log(args['T']) + parms['C4']*(args['T']**parms['C5']))"
    ],
    'args': {'Temperature': {'name': 'Temperature', 'symbol': 'T', 'unit': 'K'}},
    'parms': {
        'C1': {'name': 'C1', 'symbol': 'C1', 'unit': '1'},
        'C2': {'name': 'C2', 'symbol': 'C2', 'unit': '1'},
        'C3': {'name': 'C3', 'symbol': 'C3', 'unit': '1'},
        'C4': {'name': 'C4', 'symbol': 'C4', 'unit': '1'},
        'C5': {'name': 'C5', 'symbol': 'C5', 'unit': '1'}
    },
    'return': {'vapor-pressure': {'name': 'vapor-pressure', 'symbol': 'VaPr', 'unit': 'Pa'}},
    'body_integral': None,
    'body_first_derivative': None,
    'body_second_derivative': None,
    'custom_integral': None
    }
    ```
    '''
    try:
        # create parser instance
        parser = EquationParser(
            equation_body=equation_body,
            key_names=key_names
        )

        # parse equation
        return parser.eq_formatter()
    except Exception as e:
        raise Exception(f"parse_equation_body error! {e}")
