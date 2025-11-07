# import libs
from typing import Dict, Literal, List, Optional
# locals
from ..utils import EquationParser


def parse_equation_body(
    equation_body: str | Dict,
    key_mode: Literal[
        'upper',
        'lower'
    ] = 'lower',
    key_names: Optional[List[str]] = None
) -> list:
    '''
    Parse equation body string into structured dictionary.

    Parameters
    ----------
    equation_body : str or Dict
        The equation body string to parse.
    key_mode : str, optional
        Key mode (upper or lower), by default 'lower'
    key_names : List[str], optional
        Custom key names for the parsed dictionary, by default None. It use default key names as ['id', 'body', 'args', 'parms', 'return'].

    Returns
    -------
    list
        A list of parsed equations in structured format.
    '''
    try:
        # create parser instance
        parser = EquationParser(
            equation_body=equation_body,
            key_mode=key_mode,
            key_names=key_names
        )

        # parse equation
        parse_res = parser.eq_formatter()

        return parse_res
    except Exception as e:
        raise Exception(f"parse_equation_body error! {e}")
