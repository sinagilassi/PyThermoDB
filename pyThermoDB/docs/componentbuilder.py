# import packages/modules
import pandas as pd


class ComponentBuilder:

    # vars
    properties = {}
    functions = {}

    def __init__(self):
        pass

    def add(self, name, value):
        '''
        Add a new property/functions

        Parameters
        ----------
        name : str
            name of the property
        value : str
            value of the property

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            self.properties[name] = value
            return True
        except Exception as e:
            raise Exception("Adding a new property failed!, ", e)

    def remove(self, name):
        '''
        Remove a property/functions

        Parameters
        ----------
        name : str
            name of the property

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            self.properties.pop(name)
            return True
        except Exception as e:
            raise Exception("Removing a property failed!, ", e)

    def update(self, name, value):
        '''
        Update a property/functions

        Parameters
        ----------
        name : str
            name of the property
        value : str
            value of the property

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            self.properties[name] = value
            return True
        except Exception as e:
            raise Exception("Updating a property failed!, ", e)

    def rename(self, name, new_name):
        '''
        Rename a property/functions

        Parameters
        ----------
        name : str
            name of the property
        new_name : str
            new name of the property

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            self.properties[new_name] = self.properties.pop(name)
            return True
        except Exception as e:
            raise Exception("Renaming a property failed!, ", e)
