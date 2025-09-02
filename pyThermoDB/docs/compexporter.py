# import packages/modules
import logging
# local
from ..core import TableData
from ..core import TableEquation
from ..core import TableMatrixData
from ..core import TableMatrixEquation

# logger
logger = logging.getLogger(__name__)


class CompExporter:

    # vars
    __properties = {}
    __functions = {}

    def __init__(self):
        self.__functions = {}
        self.__properties = {}
        # allowed types
        # allowed types for properties
        self.allowed_types_properties = (TableData, dict, TableMatrixData)

        # allowed types for equations (functions)
        self.allowed_types_equations = (TableEquation, TableMatrixEquation)

    @property
    def properties(self):
        return self.__properties

    @property
    def functions(self):
        return self.__functions

    def _add(
        self,
        name: str,
        value: TableData | TableEquation | TableMatrixData | TableMatrixEquation
    ):
        '''
        Add a new property/functions

        Parameters
        ----------
        name : str
            name of the property/function
        value : TableData | TableEquation | TableMatrixData | TableMatrixEquation
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

            # allowed types for properties
            # _allowed_types_properties = (TableData, dict, TableMatrixData)

            # allowed types for equations (functions)
            # _allowed_types_equations = (TableEquation, TableMatrixEquation)

            # check TableData | TableEquation
            if isinstance(value, self.allowed_types_properties):
                self.__properties[name] = value
            elif isinstance(value, self.allowed_types_equations):
                self.__functions[name] = value
            else:
                raise Exception("Value must be TableData or TableEquation")

            return True
        except Exception as e:
            logger.error(f"Adding a new property failed!, {e}")
            return False

    def _remove(self, name: str) -> bool:
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
                logger.warning(f"{name} not found!")
                return False
        except Exception as e:
            logger.error(f"Removing a property failed!, {e}")
            return False

    def _update(
            self,
            name: str,
            value: TableData | TableEquation | TableMatrixData | TableMatrixEquation
    ):
        '''
        Update a property/functions

        Parameters
        ----------
        name : str
            name of the property/function
        value : TableData | TableEquation | TableMatrixData | TableMatrixEquation
            value of the property/function

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            # check TableData and TableMatrixData
            if isinstance(value, self.allowed_types_properties):
                if name in self.__properties:
                    self.__properties[name] = value
                    return True
                else:
                    logger.warning(f"{name} not found!")
                    return False

            # check TableEquation and TableMatrixEquation
            elif isinstance(value, self.allowed_types_equations):
                if name in self.__functions:
                    self.__functions[name] = value
                    return True
                else:
                    logger.warning(f"{name} not found!")
                    return False

            else:
                logger.error("Value must be TableData or TableEquation")
                return False

        except Exception as e:
            logger.error(f"Updating a property failed!, {e}")
            return False

    def _rename(
            self,
            name: str,
            new_name: str
    ) -> bool:
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
                logger.warning(f"{name} not found!")
                return False
        except Exception as e:
            raise Exception("Renaming a property failed!, ", e)

    def _clean(self):
        '''
        Clean properties/functions (dictionaries)

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
            logger.error(f"Cleaning properties/functions failed!, {e}")
            return False
