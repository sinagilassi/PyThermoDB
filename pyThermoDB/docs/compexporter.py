# import packages/modules

# local
from .tabledata import TableData
from .tableequation import TableEquation


class CompExporter:

    # vars
    __properties = {}
    __functions = {}

    def __init__(self):
        self.__functions = {}
        self.__properties = {}

    @property
    def properties(self):
        return self.__properties

    @property
    def functions(self):
        return self.__functions

    def _add(self, name, value):
        '''
        Add a new property/functions

        Parameters
        ----------
        name : str
            name of the property/function
        value : TableData | TableEquation
            value of the property/function

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            # check value
            if value is None:
                raise Exception("Value is required")

            # check TableData | TableEquation
            if isinstance(value, TableData) or isinstance(value, dict):
                self.__properties[name] = value
            elif isinstance(value, TableEquation):
                self.__functions[name] = value
            else:
                raise Exception("Value must be TableData or TableEquation")
        except Exception as e:
            raise Exception("Adding a new property failed!, ", e)

    def _remove(self, name):
        '''
        Remove a property/functions

        Parameters
        ----------
        name : str
            name of the property/function

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            # check
            if name in self.__properties:
                del self.__properties[name]
                return True
            elif name in self.__functions:
                del self.__functions[name]
                return True
            else:
                raise Exception(f"{name} not found!")
        except Exception as e:
            raise Exception("Removing a property failed!, ", e)

    def _update(self, name, value):
        '''
        Update a property/functions

        Parameters
        ----------
        name : str
            name of the property/function
        value : TableData | TableEquation
            value of the property/function

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            # check TableData | TableEquation
            if isinstance(value, TableData) or isinstance(value, dict):
                if name in self.__properties:
                    self.__properties[name] = value
                    return True
                else:
                    raise Exception(f"{name} not found!")
            elif isinstance(value, TableEquation):
                if name in self.__functions:
                    self.__functions[name] = value
                    return True
                else:
                    raise Exception(f"{name} not found!")
            else:
                raise Exception("Value must be TableData or TableEquation")
        except Exception as e:
            raise Exception("Updating a property failed!, ", e)

    def _rename(self, name, new_name):
        '''
        Rename a property/functions

        Parameters
        ----------
        name : str
            name of the property/function
        new_name : str
            new name of the property/function

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            # check
            if name in self.__properties:
                self.__properties[new_name] = self.__properties.pop(name)
                return True
            elif name in self.__functions:
                self.__functions[new_name] = self.__functions.pop(name)
                return True
            else:
                raise Exception(f"{name} not found!")
        except Exception as e:
            raise Exception("Renaming a property failed!, ", e)

    def _clean(self):
        '''
        Clean properties/functions

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            self.__properties = {}
            self.__functions = {}
            return True
        except Exception as e:
            raise Exception("Cleaning properties/functions failed!, ", e)
