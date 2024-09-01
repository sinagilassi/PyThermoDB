# import packages/modules
import pandas as pd


class TableEquation:
    def __init__(self, table_name, equations):
        self.table_name = table_name
        self.equations = equations

    def eq_info(self, id):
        '''
        Display equation details

        Parameters
        ----------
        id : int
            equation id

        Returns
        -------
        None.

        '''
        # equation id
        equation = self.equations[id]
        # equation body
        _body = equation['BODY']
        # equation args
        _args = equation['ARGS']
        # equation params
        _parms = equation['PARMS']
        # equation src
        _return = equation['RETURNS']

        # eq summary
        eq_summary = {
            'id': id,
            'body': _body,
            'args': _args,
            'parms': _parms,
            'return': _return
        }

        return eq_summary
