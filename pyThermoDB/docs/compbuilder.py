# import packages/modules
import pickle
import yaml
# local
from .compexporter import CompExporter
from .tabledata import TableData
from .tableequation import TableEquation


class CompBuilder(CompExporter):

    # vars
    __data = {}

    def __init__(self):
        # init class
        super().__init__()

    def add_data(self, name: str, value):
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

            # check TableData | TableEquation
            if isinstance(value, TableData) or isinstance(value, TableEquation) or isinstance(value, dict):
                self.__data[name] = value
                return True
            else:
                raise Exception('Value must be TableData or TableEquation')
        except Exception as e:
            raise Exception('Adding new data failed!, ', e)

    def delete_data(self, name):
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
                return True
            else:
                raise Exception('Data not found')
        except Exception as e:
            raise Exception('Deleting data failed!, ', e)

    def rename_data(self, name, new_name):
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

    def export_yml(self, component_name):
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
                'EQUATIONS': {}
            }
            # get TableData
            for i, (name, value) in enumerate(self.properties.items()):
                if isinstance(value, TableData):
                    _yml = value.to_dict()
                    # add chunk
                    _data_yml['DATA'][str(name)] = _yml

            # get TableEquation
            for i, (name, value) in enumerate(self.functions.items()):
                if isinstance(value, TableEquation):
                    _yml = value.to_dict()
                    # add chunk
                    _data_yml['EQUATIONS'][str(name)] = _yml

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

    def export_data_structure(self, component_name):
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

    def check_properties(self):
        '''
        Check properties

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            # check library
            return self.properties
        except Exception as e:
            raise Exception('Checking properties failed!, ', e)

    def check_property(self, name) -> TableData:
        '''
        Check properties

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            # check library
            return self.properties[name]
        except Exception as e:
            raise Exception('Checking properties failed!, ', e)

    def check_functions(self):
        '''
        Check functions

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            # check library
            return self.functions
        except Exception as e:
            raise Exception('Checking functions failed!, ', e)

    def check_function(self, name) -> TableEquation:
        '''
        Check functions

        Returns
        -------
        res : bool
            True if success
        '''
        try:
            # check library
            return self.functions[name]
        except Exception as e:
            raise Exception('Checking functions failed!, ', e)

    def save(self, filename):
        """Save the instance to a file using pickle"""
        try:
            # build
            self.build()
            # save
            with open(filename, 'wb') as f:
                pickle.dump(self, f)
        except Exception as e:
            raise Exception("Saving CompBuilder instance failed!", e)

    @classmethod
    def load(cls, filename):
        """Load a saved instance from a file using pickle"""
        try:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            raise Exception("Loading CompBuilder instance failed!", e)