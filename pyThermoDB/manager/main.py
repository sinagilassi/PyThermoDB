# import libs
from typing import Dict
# locals
from ..utils import EquationParser


def parse_equation_body(
    equation_body: str | Dict
) -> list:
    '''
    Parse equation body string into structured dictionary.

    Parameters
    ----------
    equation_body : str or Dict
        The equation body string to parse.

    Returns
    -------
    list
        A list of parsed equations in structured format.
    '''
    try:
        # create parser instance
        parser = EquationParser(equation_body)
        # parse equation
        parse_res = parser.eq_formatter()

        return parse_res
    except Exception as e:
        raise Exception(f"parse_equation_body error! {e}")
