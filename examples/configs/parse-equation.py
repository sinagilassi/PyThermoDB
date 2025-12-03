# import libs
from typing import List
from pyThermoDB.manager import parse_equation_body
from pyThermoDB.models import EquationDefinition
from rich import print
# locals

# SECTION: parse equation body
equation_body = """
- parms['C1 | C1 | 1'] = parms['C1 | C1 | 1']/1
- parms['C2 | C2 | 1'] = parms['C2 | C2 | 1']/1
- parms['C3 | C3 | 1'] = parms['C3 | C3 | 1']/1
- parms['C4 | C4 | 1'] = parms['C4 | C4 | 1']/1
- parms['C5 | C5 | 1'] = parms['C5 | C5 | 1']/1
- a = parms['C1 | C1 | 1'] + math.pow(parms['C2 | C2 | 1'], 2)
- b = parms['C3 | C3 | 1'] * parms['C4 | C4 | 1']
- c = parms['C5 | C5 | 1'] / 2
- res['vapor-pressure | VaPr | Pa'] = math.exp(parms['C1 | C1 | 1'] + parms['C2 | C2 | 1']/args['temperature | T | K'] + parms['C3 | C3 | 1']*math.log(args['temperature | T | K']) + parms['C4 | C4 | 1']*(args['temperature | T | K']**parms['C5 | C5 | 1'])) + 100*a + 200*b + 300*c
"""

parsed_equation: List[EquationDefinition] = parse_equation_body(equation_body)
print(parsed_equation)
