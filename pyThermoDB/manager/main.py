# import libs
from typing import Dict, Any, List, Optional
# locals
from ..utils import EquationParser, is_number
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


def parse_equation_body_with_table_structure(
    equation_body: str | Dict[str, Any],
    table_structure: Dict[str, List[Any]],
    key_names: Optional[List[str]] = None
) -> List[EquationDefinition]:
    '''
    Parse equation body string into structured dictionary (EquationDefinition) with respect to table structure for parms unit normalization.

    Parameters
    ----------
    equation_body : str
        The equation body string to normalize.
    table_structure : Dict[str, List[Any]]
        The table structure containing columns, symbol, unit information.
    key_names : List[str], optional
        Custom key names for the parsed dictionary, by default None. It use default key names as ['id', 'body', 'args', 'parms', 'return'].

    Returns
    -------
    str
        The normalized equation body string.
    '''
    try:
        def BODY_ELEMENT_MAKER(
                eq_parms: List[str],
                symbols: List[Any],
                units: List[Any]
        ) -> List[str]:
            # body config elements
            BODY_ELEMENTS = []

            # iterate over parms and unit
            for symbol, unit in zip(symbols, units):
                # check unit numeric
                if (
                    is_number(unit) and
                    symbol in eq_parms
                ):
                    # construct full key
                    element_ = f"parms['{symbol}'] = parms['{symbol}']/{unit}"

                    # >> add to body config elements
                    BODY_ELEMENTS.append(element_)

            # return body elements
            return BODY_ELEMENTS

        # SECTION: create parser instance
        parser = EquationParser(
            equation_body=equation_body,
            key_names=key_names
        )

        # parse equation
        eqs_ = parser.eq_formatter()

        # SECTION: parms unit normalization
        SYMBOL = table_structure.get('SYMBOL', [])
        UNIT = table_structure.get('UNIT', [])

        # SECTION: normalize equation body
        normalized_eqs: List[EquationDefinition] = []

        # iterate equations
        for eq in eqs_:
            # get body
            body_ = eq.body.copy()
            # get parms
            parms_ = eq.parms
            # >> check
            if parms_:
                eq_parms = list(parms_.keys())
            else:
                eq_parms = []

            # make body elements
            BODY_ELEMENTS = BODY_ELEMENT_MAKER(
                eq_parms=eq_parms,
                symbols=SYMBOL,
                units=UNIT
            )

            # prepend body elements
            body_ = BODY_ELEMENTS + body_

            # update body
            eq.body = body_

            # >> add to normalized equations
            normalized_eqs.append(eq)

        # return normalized equations
        return normalized_eqs
    except Exception as e:
        raise Exception(f"normalize_equation_body error! {e}")
