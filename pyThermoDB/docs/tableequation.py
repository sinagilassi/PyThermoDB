# import packages/modules
import pandas as pd
import math


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

    def eq(self, id, parms, args):
        '''
        Build an equation

        Parameters
        ----------
        id : int
            equation id

        Returns
        -------
        Eq : object
            executable equation as: eq(parms,args)
        '''
        try:
            # select the equation
            selected_eq = self.eq_info(id)
            # function body
            body = selected_eq['body']
            # build equation
            res = self.eq_exe(body, parms=parms, args=args)
            return res
        except Exception as e:
            raise Exception(f'building equation error {e}')

    def eq_exe(self, body, parms, args):
        '''
        Execute the function having args, parameters and body

        Parameters
        ----------
        body : str
            function body
        parms : dict
            parameters
        args : dict
            args

        Returns
        -------
        res : float
            calculation result
        '''
        # Define a namespace dictionary for eval
        namespace = {'args': args, "parms": parms}
        # Import math module within the function
        namespace['math'] = math
        # Execute the body within the namespace
        exec(body, namespace)
        # Return the result
        return namespace['res']
