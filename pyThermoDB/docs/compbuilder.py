# import packages/modules
import pickle
import yaml
import os
from typing import Optional, Union

# local
from .compexporter import CompExporter
from .tabledata import TableData
from .tableequation import TableEquation
from .tablematrixdata import TableMatrixData
from .tablematrixequation import TableMatrixEquation


class CompBuilder(CompExporter):

    # vars
    __data = {}

    def __init__(self):
        # init class
        super().__init__()

    def add_data(self, name: str, value: Union[TableData, TableEquation, dict, TableMatrixData, TableMatrixEquation]):
        '''
        Add TableData/TableEquation

        Parameters
        ----------
        name : str
            data name
        value : TableData | TableEquation | dict
            value of the property/function

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            # check
            if value is None:
                raise Exception('Value is required')

            # check
            if name is None:
                raise Exception('Name is required')

            # check TableData | TableEquation | dict | TableMatrixData | TableMatrixEquation
            allowed_types = (TableData, TableEquation, dict,
                             TableMatrixData, TableMatrixEquation)

            # check allowed types
            if isinstance(value, allowed_types):
                self.__data[name] = value
                return True
            else:
                raise Exception('Value must be TableData or TableEquation')
        except Exception as e:
            raise Exception('Adding new data failed!, ', e)

    def delete_data(self, name: str):
        '''
        Delete data

        Parameters
        ----------
        name : str
            data name

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            if name in self.__data:
                del self.__data[name]
                #
                return True
            else:
                raise Exception('Data not found')
        except Exception as e:
            raise Exception('Deleting data failed!, ', e)

    def rename_data(self, name: str, new_name: str):
        '''
        Rename data

        Parameters
        ----------
        name : str
            data name
        new_name : str
            new data name

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            if name in self.__data:
                self.__data[new_name] = self.__data.pop(name)
                return True
            else:
                raise Exception('Data not found')
        except Exception as e:
            raise Exception('Renaming data failed!, ', e)

    def list_data(self):
        '''
        List the thermo data added `before saving`

        Parameters
        ----------
        None

        Returns
        -------
        data : dict
            data dictionary

        Notes
        -----
        The thermo objects are created by

        1. thermo_db.build_data()
        2. thermo_db.build_equations()
        '''
        try:
            return self.__data
        except Exception as e:
            raise Exception('Listing data failed!, ', e)

    def build(self):
        '''
        Build thermodb

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            # build library
            for name, value in self.__data.items():
                self._add(name, value)

            return True
        except Exception as e:
            raise Exception('Building library failed!, ', e)

    def export_yml(self, component_name: str):
        '''
        Export thermodb

        Parameters
        ----------
        component_name : str
            component name

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            # data
            _to_comp = {}

            _data_yml = {
                'DATA': {},
                'EQUATIONS': {},
                'MATRIX-DATA': {},
                'MATRIX-EQUATIONS': {}
            }
            # get TableData
            for i, (name, value) in enumerate(self.properties.items()):
                if isinstance(value, TableData):
                    _yml = value.to_dict()
                    # add chunk
                    _data_yml['DATA'][str(name)] = _yml

            # get TableMatrixData
            for i, (name, value) in enumerate(self.properties.items()):
                if isinstance(value, TableMatrixData):
                    _yml = value.to_dict()
                    # add chunk
                    _data_yml['MATRIX-DATA'][str(name)] = _yml

            # get TableEquation
            for i, (name, value) in enumerate(self.functions.items()):
                if isinstance(value, TableEquation):
                    _yml = value.to_dict()
                    # add chunk
                    _data_yml['EQUATIONS'][str(name)] = _yml

            # get TableMatrixEquation
            for i, (name, value) in enumerate(self.functions.items()):
                if isinstance(value, TableMatrixEquation):
                    _yml = value.to_dict()
                    # add chunk
                    _data_yml['MATRIX-EQUATIONS'][str(name)] = _yml

            # for component
            _to_comp[component_name] = _data_yml

            # convert to yml
            res = yaml.dump(_to_comp)

            # save
            with open(f"{component_name}.yml", "w") as f:
                f.write(res)

            # return
            return True

        except Exception as e:
            raise Exception('Exporting library failed!, ', e)

    def export_data_structure(self, component_name: str):
        '''
        Export yml of thermodb containing TableData and TableEquation objects

        Parameters
        ----------
        component_name : str
            component name

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            # build
            self.build()

            # yml
            return self.export_yml(component_name)
        except Exception as e:
            raise Exception('Exporting library failed!, ', e)

    def check(self) -> dict:
        '''
        Check library

        Returns
        -------
        res : dict
            list of all properties and functions registered 
        '''
        try:
            # res
            res = {}
            # check properties
            res = {**self.check_properties(), **self.check_functions()}
            return res
        except Exception as e:
            raise Exception('Checking library failed!, ', e)

    def check_properties(self) -> dict[str, TableData | TableMatrixData]:
        '''
        Check properties

        Returns
        -------
        dict
            all properties registered
        '''
        try:
            # check library
            return self.properties
        except Exception as e:
            raise Exception('Checking properties failed!, ', e)

    def check_property(self, name: str) -> TableData | TableMatrixData:
        '''
        Check properties

        Parameters
        ----------
        name : str
            name of the property to check

        Returns
        -------
        TableMatrixData | TableData
            property registered
        '''
        try:
            # check library
            return self.properties[name]
        except Exception as e:
            raise Exception('Checking properties failed!, ', e)

    def check_functions(self) -> dict[str, TableEquation | TableMatrixEquation]:
        '''
        Check all functions

        Returns
        -------
        dict
            all functions registered
        '''
        try:
            # check library
            return self.functions
        except Exception as e:
            raise Exception('Checking functions failed!, ', e)

    def check_function(self, name: str) -> TableEquation | TableMatrixEquation:
        '''
        Check functions

        Parameters
        ----------
        name : str
            function name

        Returns
        -------
        TableEquation | TableMatrixEquation
            function registered
        '''
        try:
            # check library
            return self.functions[name]
        except Exception as e:
            raise Exception('Checking functions failed!, ', e)

    def save(self, filename: str, file_path: Optional[str] = None) -> bool:
        """
        Saves the instance to a file using pickle

        Parameters
        ----------
        filename : str
            filename
        file_path : str
            file path (default is None)

        Returns
        -------
        res : bool
            True if success
        """
        try:
            # check filename
            if filename is None:
                raise Exception("Filename is required!")

            # build
            self.build()

            # file path setting
            if file_path is None:
                file_path = os.getcwd()

            # file full name
            filename = os.path.join(file_path, filename)

            # file name path
            if not filename.endswith('.pkl'):
                filename += '.pkl'

            # save
            with open(f'{filename}', 'wb') as f:
                pickle.dump(self, f)
            # res
            return True
        except Exception as e:
            raise Exception("Saving CompBuilder instance failed!", e)

    @classmethod
    def load(cls, filename: str):
        """
        Loads a saved instance from a file using pickle

        Parameters
        ----------
        filename : str
            filename path

        Returns
        -------
        thermodb : object
            thermodb instance
        """
        try:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            raise Exception("Loading CompBuilder instance failed!", e)

    def clean(self) -> bool:
        '''
        Clean all data including properties/functions

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            # clean
            # data
            self.__data = {}
            # properties/functions
            self._clean()
            return True
        except Exception as e:
            raise Exception("Cleaning properties/functions failed!", e)
