# import packages/modules
import pickle
import yaml
import os
from typing import Optional, Union, Literal

# local
from .compexporter import CompExporter
from .tabledata import TableData
from .tableequation import TableEquation
from .tablematrixdata import TableMatrixData
from .tablematrixequation import TableMatrixEquation
from ..config import __version__


class CompBuilder(CompExporter):
    """Used to build thermodb library"""

    # vars
    __data = {}
    # thermodb name (optional)
    __thermodb_name: str | None = None
    # thermodb version
    build_version = __version__

    def __init__(self, thermodb_name: Optional[str] = None):
        '''
        Initialize CompBuilder object
        
        Parameters
        ----------
        thermodb_name : str
            name of the thermodb (default is None)
        '''
        # init class
        super().__init__()
        # set name
        self.__thermodb_name = thermodb_name
        
    @property
    def thermodb_name(self) -> str | None:
        '''
        Get thermodb name
        
        Returns
        -------
        str
            thermodb name
        '''
        # check name
        if self.__thermodb_name is None:
            # return default name
            return 'thermodb'
        return self.__thermodb_name
        
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

    def check_property(self, thermo_name: str) -> TableData | TableMatrixData:
        '''
        Check properties

        Parameters
        ----------
        thermo_name : str
            name of the thermodynamic property

        Returns
        -------
        TableMatrixData | TableData
            property registered
        '''
        try:
            # check library
            return self.properties[thermo_name]
        except Exception as e:
            raise Exception('Checking properties failed!, ', e)
        
    def select_property(self, thermo_name: str) -> TableData | TableMatrixData:
        '''
        Select a thermodynamic property
        
        Parameters
        ----------
        thermo_name : str
            name of the thermodynamic property
            
        Returns
        -------
        TableMatrixData | TableData
            property registered in the thermodb
        '''
        try:
            # check library
            return self.properties[thermo_name]
        except Exception as e:
            raise Exception('Selecting a property failed!, ', e)

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
            function registered in the thermodb
        '''
        try:
            # check library
            return self.functions[name]
        except Exception as e:
            raise Exception('Checking functions failed!, ', e)
        
    def select_function(self, function_name: str) -> TableEquation | TableMatrixEquation:
        '''
        Select a thermodynamic function
        
        Parameters
        ----------
        function_name : str
            name of the thermodynamic function
            
        Returns
        -------
        TableMatrixEquation | TableEquation
            function registered in the thermodb
        '''
        try:
            # check library
            return self.functions[function_name]
        except Exception as e:
            raise Exception('Selecting a function failed!, ', e)
        
    def select(self, thermo_name: str) -> TableData | TableMatrixData | TableEquation | TableMatrixEquation:
        '''
        Select a thermodynamic property used for both functions and properties registered in the thermodb

        Parameters
        ----------
        thermo_name : str
            name of the thermodynamic property

        Returns
        -------
        TableMatrixData | TableData | TableEquation | TableMatrixEquation
            property defined in the thermodb 
        '''
        try:
            # SECTION 1: check if the property exists in both functions and properties
            if thermo_name in self.functions and thermo_name in self.properties:
                # raise
                raise Exception('Property exists in both functions and properties!')
            
            # SECTION 2: check if the property is a function or a property
            if thermo_name in self.functions:
                # check if the property is a function
                return self.functions[thermo_name]
            elif thermo_name in self.properties:
                # check if the property is a property
                return self.properties[thermo_name]
            else:
                # check if the property is a property in the thermodb
                raise Exception('Property not found in the thermodb!')
        except Exception as e:
            raise Exception('Selecting a thermodynamic property failed!, ', e)

    def retrieve(self, property_source: str, message: Optional[str] = None, symbol_format: Literal['alphabetic', 'numeric'] = 'alphabetic'):
        '''
        Retrieve a thermodynamic property from the thermodb for only TableData and TableMatrixData
        
        Parameters
        ----------
        property_source : str
            source of the property to retrieve such as 'general-data | dH_IG'
        message : str
            message to display (default is None)
        symbol_format : str
            symbol format to use (default is 'alphabetic'), needed for TableMatrixData
            
        Returns
        -------
        prop: DataResult
            property object
            
        Notes
        -----
        The property source is a string containing the name of the property source and the name of the property separated by a pipe (|) character.
        For example, 
        
        1- 'general-data | dH_IG' means that the property is in the general-data source and the name of the property is dH_IG.
        2- 'nrtl-data | alpha_ij | methanol | ethanol' means that the property is in the nrtl-data source and the name of the property is alpha_ij and the components are methanol and ethanol.
        '''
        try:
            # split source
            source = property_source.split('|')
            
            
            # SECTION: check message
            message = message if message is not None else f'Retrieving used for {property_source}!'

            # SECTION: property source
            prop_src = self.select(source[0].strip())

            # SECTION: property name
            # check
            if isinstance(prop_src, TableData):
                # check length
                if len(source) != 2:
                    raise ValueError(f"Invalid source format! {property_source}")
                # get property
                prop = prop_src.get_property(source[1].strip(), message=message)
                # return
                return prop
            elif isinstance(prop_src, TableMatrixData):
                # get components
                component_names = source[2:]
                # trim
                component_names = [name.strip() for name in component_names]
                # check length
                if len(component_names) != 2:
                    raise ValueError(f"Invalid source format! {property_source}, components are required!")
                # get property
                prop = prop_src.get_matrix_property(source[1].strip(), component_names=component_names, 
                                                    symbol_format=symbol_format, message=message)
                # return
                return prop
            else:
                raise Exception(
                    f"Property source is not a TableData object! {prop_src}")
                
        except Exception as e:
            raise Exception("Retrieving failed!, ", e)
        
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
