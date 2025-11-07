# import libs
import logging
from typing import List, Dict, Any, Literal, Optional
import re
import os
import yaml
# locals
from ..models import EquationDefinition


# NOTE: logger
logger = logging.getLogger(__name__)


class EquationParser:
    '''
    Equation parser class used to parse equation (equation body) strings into structured format
    and extract arguments, parameters, and return values.

    Example equation body:

    ```python
    - parms['C1 | C1 | 1'] = parms['C1 | C1 | 1']/1
    - parms['C2 | C2 | 1'] = parms['C2 | C2 | 1']/1
    - parms['C3 | C3 | 1'] = parms['C3 | C3 | 1']/1
    - parms['C4 | C4 | 1'] = parms['C4 | C4 | 1']/1
    - parms['C5 | C5 | 1'] = parms['C5 | C5 | 1']/1
    - res['vapor-pressure | VaPr | Pa'] = math.exp(parms['C1 | C1 | 1'] + parms['C2 | C2 | 1']/args['temperature | T | K'] + parms['C3 | C3 | 1']*math.log(args['temperature | T | K']) + parms['C4 | C4 | 1']*(args['temperature | T | K']**parms['C5 | C5 | 1']))
    ```

    Example equation with structured format:

    ```python
    {
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
    ```
    '''

    def __init__(
            self,
            equation_body: str | dict,
            key_names: Optional[List[str]] = None
    ):
        # NOTE: set equation body
        self.equation_body = equation_body
        self.key_names = key_names if key_names is not None else [
            'id', 'body', 'args', 'parms', 'returns',
        ]

        # capitalize key names
        self.key_names_upper = [k.upper() for k in self.key_names]
        # lowercase key names
        self.key_names_lower = [k.lower() for k in self.key_names]

        # SECTION: process equation body
        if isinstance(self.equation_body, dict):
            # set mode
            self.mode = 'dict'
            # NOTE: already dict
            # create equation holder
            self.equation_holder = self._create_equation_holder()
        elif isinstance(self.equation_body, str):
            # set mode
            self.mode = 'str'
            # NOTE: convert body string to dict
            self.equation_body_list = self._body_str_to_list()
            # NOTE: create equation body dict
            self.equation_holder = self._create_equation_holder()
        else:
            raise ValueError("equation_body must be str or dict!")

    def _body_str_to_list(self):
        '''
        Convert equation body string to dictionary
        '''
        try:
            # NOTE: process body string
            if not isinstance(self.equation_body, str):
                raise ValueError("equation_body must be str!")

            # NOTE: split by lines
            lines = self.equation_body.strip().split('\n')

            # NOTE: clean lines
            lines = [
                line.strip() for line in lines if line.strip().startswith('-')
            ]
            # return as dict
            return lines
        except Exception as e:
            raise Exception(f"body_str_to_dict error! {e}")

    def _create_equation_holder(self):
        '''
        Create equation structure
        '''
        try:
            # SECTION: equation body
            if self.mode == 'str':
                eq = {
                    'EQ-1': {
                        'BODY': self.equation_body_list
                    }
                }
            elif self.mode == 'dict':
                # >> check
                if not isinstance(self.equation_body, dict):
                    raise ValueError("equation_body must be dict!")

                eq = {k: v for k, v in self.equation_body.items()}
            else:
                raise ValueError("Unsupported mode for creating equation!")

            return eq
        except Exception as e:
            raise Exception(f"create_equation error! {e}")

    def parse_equation(
            self,
            eq_data: List[str]
    ):
        '''
        Parse equation data into a dictionary including equation args, parameters, returns

        Parameters
        ----------
        eq_data : dict
            equation data
        '''
        try:
            # check
            if not isinstance(eq_data, list):
                raise ValueError("eq_data must be a list!")

            # init
            eq_dict = {}
            eq_dict['ARGS'] = {}
            eq_dict['PARMS'] = {}
            eq_dict['RETURNS'] = {}
            eq_dict['BODY'] = []

            # NOTE: value generator
            def val_generator(d):
                '''Generate value'''
                # check 3 |
                if "|" in d:
                    # split
                    match_res = d.split("|")
                    # check
                    if len(match_res) != 3:
                        raise ValueError(
                            f"{d} must be 3 elements!")

                    # key
                    key = match_res[0].strip()
                    # name
                    name = key
                    # symbol
                    symbol = match_res[1].strip()
                    # unit
                    unit = match_res[2].strip()

                    # set
                    val = {
                        'name': name,
                        'symbol': symbol,
                        'unit': unit
                    }
                else:
                    raise Exception(
                        f"Invalid value format! {d} must be 3 elements!")

                return key, val

            # SECTION: parse equation data
            # loop through eq_data
            for eq in eq_data:
                # check
                if isinstance(eq, str):
                    # parse equation body
                    body_ = eq

                    # NOTE: parse to extract args
                    # regex
                    regex = r"args\['([^']+)'\]"
                    # find all matches
                    matches = re.findall(regex, body_)
                    # check
                    if matches:
                        # loop through matches
                        for match in matches:
                            # ! val generator
                            key, val = val_generator(match)
                            symbol = val['symbol']
                            # check
                            if match not in eq_dict['ARGS']:
                                # set
                                eq_dict['ARGS'][key] = val
                                # set body
                                body_ = body_.replace(
                                    f"'{match}'", f"'{symbol}'")

                    # NOTE: parse to extract parameters
                    # regex
                    regex = r"parms\['([^']+)'\]"
                    # find all matches
                    matches = re.findall(regex, body_)
                    # check
                    if matches:
                        # loop through matches
                        for match in matches:
                            # ! val generator
                            key, val = val_generator(match)
                            symbol = val['symbol']
                            # check
                            if match not in eq_dict['PARMS']:
                                # set
                                eq_dict['PARMS'][key] = val
                                # set body
                                body_ = body_.replace(
                                    f"'{match}'", f"'{symbol}'")

                    # NOTE: parse to extract returns
                    # regex
                    regex = r"res\['([^']+)'\]"
                    # find all matches
                    matches = re.findall(regex, body_)
                    # check
                    if matches:
                        # loop through matches
                        for match in matches:
                            # ! val generator
                            key, val = val_generator(match)
                            symbol = val['symbol']
                            # check
                            if match not in eq_dict['RETURNS']:
                                # set
                                eq_dict['RETURNS'][key] = val
                                # set body
                                body_ = body_.replace(f"res['{match}']", "res")

                # updated body
                # set body
                eq_dict['BODY'].append(body_)
            # return
            return eq_dict
        except Exception as e:
            raise Exception(f"parse_equation error! {e}")

    def eq_formatter(
        self,
    ) -> List[EquationDefinition]:
        '''
        Format equations

        Parameters
        ----------
        None

        Returns
        -------
        list[EquationDefinition]
            A list of formatted equations.
        '''
        try:
            # NOTE: eqs
            eqs_formatted = []

            # get eqs
            eqs: List[Dict[str, Any]] = list(self.equation_holder.values())

            # NOTE: check eqs
            for i, eq in enumerate(eqs):
                # check type
                if not isinstance(eq, dict):
                    logger.error("Equation must be a dictionary!")
                    continue

                # extract keys
                keys_ = list(eq.keys())
                # lower keys
                keys_lower = [k.lower() for k in keys_]
                # upper keys
                keys_upper = [k.upper() for k in keys_]

                # check keys
                if (
                    "args" not in keys_lower or
                    "parms" not in keys_lower or
                    "returns" not in keys_lower or
                    "return" not in keys_lower
                ):
                    # NOTE: parse eq to generate equation structure
                    eq_ = self.equation_formatter(eq)

                    # add id key
                    if (
                        'id' not in keys_lower and
                        'id' in self.key_names_lower
                    ):
                        eq_['id'] = i

                    # >> keys formatting
                    eq_ = {
                        k.lower(): v for k, v in eq_.items()
                        if k.lower() in self.key_names_lower
                    }

                    # NOTE: convert to EquationDefinition
                    eq_ = EquationDefinition(**eq_)

                    # NOTE: append
                    eqs_formatted.append(eq_)
                else:
                    # check and add id key
                    if (
                        'id' not in keys_lower and
                        'id' in self.key_names_lower
                    ):
                        eq['id'] = i

                    # >> keys formatting
                    eq = {
                        k.lower(): v for k, v in eq.items()
                        if k.lower() in self.key_names_lower
                    }

                    # NOTE: convert to EquationDefinition
                    eq = EquationDefinition(**eq)

                    # NOTE: append
                    eqs_formatted.append(eq)

            # res
            return eqs_formatted
        except Exception as e:
            raise Exception(f"equation formatting error! {e}")

    def equation_formatter(
            self,
            equation_src: Dict | str
    ) -> Dict[str, Any]:
        '''
        Check equation format

        Parameters
        ----------
        equation_src : str | dict
            equation source (file path string or dict)
        '''
        try:
            # SECTION: path check
            if isinstance(equation_src, str):
                # check file
                if not os.path.isfile(equation_src):
                    raise FileNotFoundError(f"File not found: {equation_src}")

                # NOTE: load equation file (yml format)
                with open(equation_src, 'r') as f:
                    equations = yaml.load(f, Loader=yaml.FullLoader)
            elif isinstance(equation_src, dict):
                # NOTE: check if dict
                equations = equation_src

            # SECTION: check equation format
            # NOTE: check
            if 'BODY' not in equations.keys():
                raise ValueError("equation key `BODY` not found!")

            # NOTE: get equation body
            body_ = equations['BODY']

            # NOTE: parse
            parse_res = self.parse_equation(body_)

            # NOTE: check other equations
            body_integral = equations.get(
                'BODY-INTEGRAL',
                None
            )
            body_first_derivative = equations.get(
                'BODY-FIRST-DERIVATIVE',
                None
            )
            body_second_derivative = equations.get(
                'BODY-SECOND-DERIVATIVE',
                None
            )

            # check
            if body_integral is not None:
                # check
                if body_integral != 'None' and body_integral != 'NONE':
                    # parse
                    parse_ = self.parse_equation(body_integral)
                    # add to res
                    parse_res['BODY-INTEGRAL'] = parse_['BODY']
            else:
                parse_res['BODY-INTEGRAL'] = None

            if body_first_derivative is not None:
                # check
                if body_first_derivative != 'None' and body_first_derivative != 'NONE':
                    # parse
                    parse_ = self.parse_equation(body_first_derivative)
                    # add to res
                    parse_res['BODY-FIRST-DERIVATIVE'] = parse_['BODY']
            else:
                parse_res['BODY-FIRST-DERIVATIVE'] = None

            if body_second_derivative is not None:
                # check
                if body_second_derivative != 'None' and body_second_derivative != 'NONE':
                    # parse
                    parse_ = self.parse_equation(body_second_derivative)
                    # add to res
                    parse_res['BODY-SECOND-DERIVATIVE'] = parse_['BODY']
            else:
                parse_res['BODY-SECOND-DERIVATIVE'] = None

            # res
            return parse_res
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {equation_src}")
        except Exception as e:
            raise Exception(f"equation format checker error! {e}")
