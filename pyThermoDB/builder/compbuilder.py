# import packages/modules
import logging
import pickle
import yaml
import os
import datetime
import sys
import functools
from typing import Optional, Union, Literal, ClassVar
# local
from .compexporter import CompExporter
from .comp_tools import CompTools
from ..core import (
    TableEquation,
    TableMatrixEquation,
    TableData,
    TableMatrixData,
    TableConstants
)
from ..config import __version__
from ..models.configs import BuildType
# ! deps
from ..config.deps import get_config

# logger
logger = logging.getLogger(__name__)


class CompBuilder(CompExporter):
    """
    Used to build thermodb library, including thermodynamic data, functions, and constants.
    """

    # NOTE: # shared CompTools instance (lazy-created). Safe if CompTools is stateless.
    CompTools_: ClassVar[Optional[CompTools]] = None

    # NOTE: init attributes
    __data = {}
    # thermodb name (optional)
    __thermodb_name: str | None = None
    # message
    __message: str | None = None
    # ! thermodb version
    build_version = __version__

    # ! thermodb type
    _build_type: Optional[BuildType] = None

    # NOTE: build date/time/python version
    @functools.cached_property
    def build_date(self) -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    @functools.cached_property
    def build_timestamp(self) -> float:
        return datetime.datetime.now(datetime.timezone.utc).timestamp()

    @functools.cached_property
    def build_python(self) -> str:
        return sys.version.split()[0]

    # ! component identifiers
    _component_name: Optional[str] = None
    _component_formula: Optional[str] = None
    _component_state: Optional[str] = None

    # ! cache component identifiers as properties
    @functools.cached_property
    def component_name(self) -> Optional[str]:
        return self._component_name

    @functools.cached_property
    def component_formula(self) -> Optional[str]:
        return self._component_formula

    @functools.cached_property
    def component_state(self) -> Optional[str]:
        return self._component_state

    def __init__(
        self,
        thermodb_name: Optional[str] = None,
        message: Optional[str] = None
    ):
        '''
        Initialize CompBuilder object

        Parameters
        ----------
        thermodb_name : str
            name of the thermodb (default is None)
        message : str
            message (default is None)
        '''
        # SECTION: get config
        config = get_config()
        # ! set build type
        self._build_type = config.build_type
        # ! set component identifiers
        self._component_name = config.component_name
        self._component_formula = config.component_formula
        self._component_state = config.component_state

        # SECTION: super init
        CompExporter.__init__(self)

        # NOTE: ensure a shared CompTools_ exists and attach to the instance
        if CompBuilder.CompTools_ is None:
            try:
                CompBuilder.CompTools_ = CompTools()
            except Exception:
                CompBuilder.CompTools_ = None

        # SECTION: set attributes
        # set name
        self.__thermodb_name = thermodb_name
        # set message
        self.__message = message if message is not None else 'CompBuilder instance created!'

        # ! reset data
        self.__data = {}

    # SECTION: properties/functions accessors
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

    @property
    def message(self) -> str:
        '''
        Get message

        Returns
        -------
        str
            message
        '''
        # check message
        if self.__message is None:
            # return default message
            return 'CompBuilder instance created!'
        return self.__message

    @property
    def comp_tools(self) -> Optional[CompTools]:
        """
        Instance accessor for the shared CompTools_. Lazily creates the class-level
        CompTools_ if it does not exist yet.
        """
        if CompBuilder.CompTools_ is None:
            try:
                CompBuilder.CompTools_ = CompTools()
            except Exception:
                CompBuilder.CompTools_ = None
        return CompBuilder.CompTools_

    @property
    def build_type(self) -> Optional[BuildType]:
        '''
        Get build type

        Returns
        -------
        Optional[BuildType]
            build type such as 'single', 'mixture', or 'constants'
        '''
        return self._build_type

    # NOTE: add data
    def add_data(
        self,
        name: str,
        value: Union[
            TableData,
            TableEquation,
            dict,
            TableMatrixData,
            TableMatrixEquation,
            TableConstants
        ]
    ):
        '''
        Add TableData/TableEquation

        Parameters
        ----------
        name : str
            data name
        value : TableData | TableEquation | dict | TableMatrixData | TableMatrixEquation | TableConstants
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

            # check TableData | TableEquation | dict | TableMatrixData | TableMatrixEquation | TableConstants
            allowed_types = (
                TableData,
                TableEquation,
                dict,
                TableMatrixData,
                TableMatrixEquation,
                TableConstants
            )

            # check allowed types
            if isinstance(value, allowed_types):
                self.__data[name] = value
                return True
            else:
                logger.error(f'Invalid type: {type(value)}')
                return False
        except Exception as e:
            logger.error(f'Adding data failed!, {e}')
            return False

    # NOTE: delete data
    def delete_data(self, name: str) -> bool:
        '''
        Delete data by name

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
                logger.error('Data not found')
                return False
        except Exception as e:
            logger.error(f'Deleting data failed!, {e}')
            return False

    # NOTE: rename data
    def rename_data(
            self,
            name: str,
            new_name: str
    ):
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
                logger.error('Data not found')
                return False
        except Exception as e:
            logger.error(f'Renaming data failed!, {e}')
            return False

    # NOTE: list data
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
            logger.error(f'Listing data failed!, {e}')
            return {}

    # SECTION: build thermodb
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
            logger.error(f'Building library failed!, {e}')
            return False

    # NOTE: export yml
    def export_yml(
            self,
            component_name: str
    ) -> bool:
        '''
        Export thermodb

        Parameters
        ----------
        component_name : str
            component name

        Returns
        -------
        res : bool
            It returns True if the export is successful, and False otherwise.
        '''
        try:
            # data
            _to_comp = {}

            _data_yml = {
                'DATA': {},
                'EQUATIONS': {},
                'MATRIX-DATA': {},
                'MATRIX-EQUATIONS': {},
                'CONSTANTS': {}
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

            # get TableConstants
            for i, (name, value) in enumerate(self.properties.items()):
                if isinstance(value, TableConstants):
                    _data_yml['CONSTANTS'][str(name)] = value.to_dict()

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
            logger.error(f'Exporting yml failed!, {e}')
            return False

    # NOTE: export data structure
    def export_data_structure(
            self,
            component_name: str
    ) -> bool:
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
            logger.error(f'Exporting data structure failed!, {e}')
            return False

    # NOTE: check library
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
            logger.error(f'Checking library failed!, {e}')
            return {}

    # NOTE: check properties
    def check_properties(self) -> dict[str, TableData | TableMatrixData | TableConstants]:
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

    # NOTE: check property availability by name
    def is_property_available(
        self,
        thermo_name: str
    ) -> bool:
        '''
        Check if a property is available in the thermodb

        Parameters
        ----------
        thermo_name : str
            name of the thermodynamic property

        Returns
        -------
        res : bool
            True if available
        '''
        try:
            # check
            return thermo_name in self.properties
        except Exception as e:
            raise Exception('Checking property availability failed!, ', e)

    # NOTE: check property by name
    def check_property(
        self,
        thermo_name: str
    ) -> TableData | TableMatrixData | TableConstants:
        '''
        Check properties

        Parameters
        ----------
        thermo_name : str
            name of the thermodynamic property

        Returns
        -------
        TableMatrixData | TableData | TableConstants
            property registered
        '''
        try:
            # check library
            return self.properties[thermo_name]
        except Exception as e:
            raise Exception('Checking properties failed!, ', e)

    # NOTE: select property (case-sensitive)
    def select_property(
        self,
        thermo_name: str
    ) -> TableData | TableMatrixData | TableConstants:
        '''
        Select a thermodynamic property registered in the thermodb, case-sensitive.

        Parameters
        ----------
        thermo_name : str
            name of the thermodynamic property

        Returns
        -------
        TableMatrixData | TableData | TableConstants
            property registered in the thermodb
        '''
        try:
            # NOTE: case-sensitive
            # thermo_name normalize to lower case
            thermo_name = thermo_name.strip().lower()

            # SECTION: lookup
            selected_property = None
            for prop in self.properties.keys():
                if prop.lower().strip() == thermo_name:
                    selected_property = prop
                    break

            # NOTE: check
            if selected_property is not None:
                thermo_name = selected_property
            else:
                raise Exception('Property not found in the thermodb!')

            # check library
            return self.properties[thermo_name]
        except Exception as e:
            raise Exception('Selecting a property failed!, ', e)

    # NOTE: check constants
    def check_constants(self) -> dict[str, TableConstants]:
        '''
        Check all constants sources.

        Returns
        -------
        dict
            all TableConstants sources registered in the thermodb
        '''
        try:
            return {
                name: value for name, value in self.properties.items()
                if isinstance(value, TableConstants)
            }
        except Exception as e:
            raise Exception('Checking constants failed!, ', e)

    # NOTE: check constants source availability by name
    def is_constant_available(
        self,
        constant_name: str
    ) -> bool:
        '''
        Check if a constants source is available in the thermodb.

        Parameters
        ----------
        constant_name : str
            name of the constants source

        Returns
        -------
        bool
            True if available
        '''
        try:
            return constant_name in self.check_constants()
        except Exception as e:
            raise Exception('Checking constants availability failed!, ', e)

    # NOTE: check constants source by name
    def check_constant(
        self,
        constant_name: str
    ) -> TableConstants:
        '''
        Check a constants source by name.

        Parameters
        ----------
        constant_name : str
            name of the constants source

        Returns
        -------
        TableConstants
            constants source registered in the thermodb
        '''
        try:
            return self.check_constants()[constant_name]
        except Exception as e:
            raise Exception('Checking constants failed!, ', e)

    # NOTE: select constants source (case-insensitive)
    def select_constant(
        self,
        constant_name: str
    ) -> TableConstants:
        '''
        Select a constants source registered in the thermodb, case-insensitive.

        Parameters
        ----------
        constant_name : str
            name of the constants source

        Returns
        -------
        TableConstants
            constants source registered in the thermodb
        '''
        try:
            constant_name = constant_name.strip().lower()
            constants = self.check_constants()

            for name, value in constants.items():
                if name.lower().strip() == constant_name:
                    return value

            raise Exception('Constants source not found in the thermodb!')
        except Exception as e:
            raise Exception('Selecting constants failed!, ', e)

    # NOTE: check functions
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

    # NOTE: check function availability by name
    def is_function_available(
        self,
        function_name: str
    ) -> bool:
        '''
        Check if a function is available in the thermodb

        Parameters
        ----------
        function_name : str
            name of the thermodynamic function

        Returns
        -------
        res : bool
            True if available
        '''
        try:
            # check
            return function_name in self.functions
        except Exception as e:
            raise Exception('Checking function availability failed!, ', e)

    # NOTE: check function by name
    def check_function(
        self,
        name: str
    ) -> TableEquation | TableMatrixEquation:
        '''
        Check functions by name

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

    # NOTE: select function (case-sensitive)
    def select_function(
        self,
        function_name: str
    ) -> TableEquation | TableMatrixEquation:
        '''
        Select a function registered in the thermodb (case-sensitive).

        Parameters
        ----------
        function_name : str
            name of the thermodynamic function

        Returns
        -------
        TableMatrixEquation | TableEquation
            function registered in the thermodb

        Notes
        -----
        - The search is case-sensitive.
        '''
        try:
            # NOTE: case-sensitive
            # functions normalize to lower case
            function_name = function_name.strip().lower()

            # SECTION: lookup
            selected_function = None
            for func in self.functions.keys():
                if func.lower().strip() == function_name:
                    selected_function = func
                    break

            # NOTE: check
            if selected_function is not None:
                function_name = selected_function
            else:
                raise Exception('Function not found in the thermodb!')

            # check library
            return self.functions[function_name]
        except Exception as e:
            raise Exception('Selecting a function failed!, ', e)

    # SECTION: select property/function (case-sensitive)
    def select(
        self,
        thermo_name: str
    ) -> Union[
        TableData,
        TableMatrixData,
        TableConstants,
        TableEquation,
        TableMatrixEquation
    ]:
        '''
        Select a thermodynamic property or function registered in the thermodb (case-sensitive).

        Parameters
        ----------
        thermo_name : str
            name of the thermodynamic property

        Returns
        -------
        TableMatrixData | TableData | TableConstants | TableEquation | TableMatrixEquation
            property defined in the thermodb
        '''
        try:
            # SECTION: case-sensitive
            # thermo_name normalize to lower case
            thermo_name = thermo_name.strip()
            # normalize to lower case
            thermo_name_lower = thermo_name.lower()

            # SECTION 1: check if the property exists in both functions and properties
            check_list = list(self.functions.keys()) + \
                list(self.properties.keys())

            # NOTE: normalize to lower case
            check_list = [item.lower() for item in check_list]
            # NOTE: check_list may contain duplicates
            check_list = list(set(check_list))

            # ! check if the property exists in both functions and properties
            if (thermo_name_lower not in check_list):
                # raise
                raise Exception(
                    'Property exists in both functions and properties!')

            # SECTION: normalized names in functions and properties
            # NOTE: functions
            functions_keys_lower = [
                k for k in self.functions.keys() if k.lower() == thermo_name_lower
            ]
            # check
            if len(functions_keys_lower) == 1:
                thermo_name = functions_keys_lower[0]
                return self.functions[thermo_name]

            # NOTE: properties
            properties_keys_lower = [
                k for k in self.properties.keys() if k.lower() == thermo_name_lower
            ]
            # check
            if len(properties_keys_lower) == 1:
                thermo_name = properties_keys_lower[0]
                return self.properties[thermo_name]

            # NOTE: not found
            raise Exception('Property not found in the thermodb!')

        except Exception as e:
            raise Exception('Selecting a thermodynamic property failed!, ', e)

    # NOTE: retrieve property/function by source string
    def retrieve(
        self,
        property_source: str,
        message: Optional[str] = None,
        symbol_format: Literal[
            'alphabetic', 'numeric'
        ] = 'alphabetic'
    ):
        '''
        Retrieve a thermodynamic property from TableData, TableConstants, or TableMatrixData.

        Parameters
        ----------
        property_source : str
            source of the property to retrieve such as 'general-data | dH_IG'
        message : str
            message to display (default is None)
        symbol_format : str
            symbol format to use (default is 'alphabetic'), needed for `TableMatrixData`

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
            # num
            source_num = len(source)

            # SECTION: check message
            message = message if message is not None else f'Retrieving used for {property_source}!'

            # SECTION: property source
            prop_src = self.select(source[0].strip())

            # SECTION: property name
            # check
            if isinstance(prop_src, TableData):
                # check length
                if source_num != 2:
                    raise ValueError(
                        f"Invalid source format! {property_source}")
                # get property
                prop = prop_src.get_property(
                    source[1].strip(),
                    message=message
                )
                # return
                return prop
            elif isinstance(prop_src, TableConstants):
                if source_num != 2:
                    raise ValueError(
                        f"Invalid source format! {property_source}")
                return prop_src.get_constant(
                    source[1].strip(),
                    message=message
                )
            elif isinstance(prop_src, TableMatrixData):
                # NOTE: check string format
                if source_num == 2:
                    # property name full format
                    prop_name = source[1].strip()

                    # check if the property name is in the format of 'Alpha_i_j'
                    extracted = prop_name.split('_')
                    # count
                    if len(extracted) != 3:
                        raise ValueError(
                            f"Invalid source format! {property_source}, property name is required!")

                    # NOTE: get property (ij method)
                    prop = prop_src.ij(
                        prop_name,
                        symbol_format=symbol_format,
                        message=message
                    )
                    # return
                    return prop
                elif source_num == 4:
                    # get components
                    component_names = source[2:]
                    # trim
                    component_names = [
                        name.strip() for name in component_names
                    ]
                    # check length
                    if len(component_names) != 2:
                        raise ValueError(
                            f"Invalid source format! {property_source}, components are required!"
                        )

                    # NOTE: get property (get_matrix_property method)
                    prop = prop_src.get_matrix_property(
                        source[1].strip(),
                        component_names=component_names,
                        symbol_format=symbol_format,
                        message=message
                    )
                    # return
                    return prop
            else:
                raise Exception(
                    f"Property source is not a TableData object! {prop_src}")

        except Exception as e:
            raise Exception("Retrieving failed!, ", e)

    # SECTION: save/load using pickle
    def save(
        self,
        filename: str,
        file_path: Optional[str] = None,
    ) -> bool:
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

            # NOTE: build
            self.build()

            # NOTE: file path setting
            if file_path is None:
                file_path = os.getcwd()

            # file full name
            filename = os.path.join(
                file_path,
                filename
            )

            # file name path
            if not filename.endswith('.pkl'):
                filename += '.pkl'

            # save
            with open(f'{filename}', 'wb') as f:
                pickle.dump(self, f)
            # res
            return True
        except Exception as e:
            logger.error(f'Saving CompBuilder instance failed!, {e}')
            return False

    # NOTE: load using pickle
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

    # NOTE: clean all data including properties/functions/constants
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

            # res
            return True
        except Exception as e:
            logger.error(f'Cleaning properties/functions failed!, {e}')
            return False

    # NOTE: get all functions' structures
    def all_function_details(self):
        '''
        Retrieve all functions' structures in the thermodb.

        Returns
        -------
        res : dict
            functions' structure
        '''
        try:
            # NOTE: get functions
            all_functions = self.check_functions()

            # NOTE: get TableEquation objects
            functions = [
                fn for fn in all_functions.values()
                if isinstance(fn, TableEquation)
            ]

            # >> check
            if not functions:
                logger.warning(
                    'No TableEquation functions found in the thermodb!')
                return None

            # NOTE: get structure (use the instance accessor)
            tools = self.comp_tools
            if tools is None:
                logger.error(
                    'CompTools not available to get function structure')
                return None

            # NOTE: get structure
            return tools.get_fn_structure(functions)
        except Exception as e:
            logger.error(f'Getting equations structure failed!, {e}')
            return None

    # NOTE: get all functions' identifiers
    def all_function_identifiers(self):
        '''
        Retrieve all functions' identifiers in the thermodb.

        Returns
        -------
        res : list
            functions' identifiers
        '''
        try:
            # NOTE: get functions
            all_functions = self.check_functions()

            # NOTE: get TableEquation objects
            functions = [
                fn for fn in all_functions.values()
                if isinstance(fn, TableEquation)
            ]

            # >> check
            if not functions:
                logger.warning(
                    'No TableEquation functions found in the thermodb!')
                return None

            # NOTE: get structure (use the instance accessor)
            tools = self.comp_tools
            if tools is None:
                logger.error(
                    'CompTools not available to get function identifiers')
                return None

            # NOTE: get identifiers
            return tools.get_fn_identifier(functions)
        except Exception as e:
            logger.error(f'Getting equations identifiers failed!, {e}')
            return None

    # NOTE: get all data structures
    def all_data_details(self):
        '''
        Retrieve all data's structures in the thermodb.

        Returns
        -------
        res : dict
            data's structure
        '''
        try:
            # NOTE: get data
            all_data = self.check_properties()

            # NOTE: get TableData objects
            data = [
                dt for dt in all_data.values()
                if isinstance(dt, TableData)
            ]

            # >> check
            if not data:
                logger.warning(
                    'No TableData found in the thermodb!')
                return None

            # NOTE: get structure (use the instance accessor)
            tools = self.comp_tools
            if tools is None:
                logger.error(
                    'CompTools not available to get data structure')
                return None

            # NOTE: get structure
            return tools.get_data_structure(data)
        except Exception as e:
            logger.error(f'Getting data structure failed!, {e}')
            return None

    # NOTE: get all data identifiers
    def all_data_identifiers(self):
        '''
        Retrieve all data's identifiers in the thermodb.

        Returns
        -------
        res : list
            data's identifiers
        '''
        try:
            # NOTE: get data
            all_data = self.check_properties()

            # NOTE: get TableData objects
            data = [
                dt for dt in all_data.values()
                if isinstance(dt, TableData)
            ]

            # >> check
            if not data:
                logger.warning(
                    'No TableData found in the thermodb!')
                return None

            # NOTE: get structure (use the instance accessor)
            tools = self.comp_tools
            if tools is None:
                logger.error(
                    'CompTools not available to get data identifiers')
                return None

            # NOTE: get identifiers
            return tools.get_data_identifier(data)
        except Exception as e:
            logger.error(f'Getting data identifiers failed!, {e}')
            return None

    # NOTE: get all data symbol labels
    def all_data_id_labels(self):
        '''
        Retrieve all data's symbol labels in the thermodb.

        Returns
        -------
        res : list
            data's symbol labels
        '''
        try:
            # NOTE: get data
            all_data = self.check_properties()

            # NOTE: get TableData objects
            data = [
                dt for dt in all_data.values()
                if isinstance(dt, TableData)
            ]

            # >> check
            if not data:
                logger.warning(
                    'No TableData found in the thermodb!')
                return None

            # NOTE: get structure (use the instance accessor)
            tools = self.comp_tools
            if tools is None:
                logger.error(
                    'CompTools not available to get data symbol labels')
                return None

            # NOTE: get symbol labels
            return tools.get_data_id_labels(data)
        except Exception as e:
            logger.error(f'Getting data symbol labels failed!, {e}')
            return None

    # NOTE: get all constants structures
    def all_constants_details(self):
        '''
        Retrieve all constants' structures in the thermodb.

        Returns
        -------
        res : dict
            constants' structure
        '''
        try:
            all_data = self.check_properties()
            constants = [
                const for const in all_data.values()
                if isinstance(const, TableConstants)
            ]

            if not constants:
                logger.warning(
                    'No TableConstants found in the thermodb!')
                return None

            tools = self.comp_tools
            if tools is None:
                logger.error(
                    'CompTools not available to get constants structure')
                return None

            return tools.get_constants_structure(constants)
        except Exception as e:
            logger.error(f'Getting constants structure failed!, {e}')
            return None

    # NOTE: get all constants identifiers
    def all_constants_identifiers(self):
        '''
        Retrieve all constants' identifiers in the thermodb.

        Returns
        -------
        res : list
            constants' identifiers
        '''
        try:
            all_data = self.check_properties()
            constants = [
                const for const in all_data.values()
                if isinstance(const, TableConstants)
            ]

            if not constants:
                logger.warning(
                    'No TableConstants found in the thermodb!')
                return None

            tools = self.comp_tools
            if tools is None:
                logger.error(
                    'CompTools not available to get constants identifiers')
                return None

            return tools.get_constants_identifier(constants)
        except Exception as e:
            logger.error(f'Getting constants identifiers failed!, {e}')
            return None

    # NOTE: get all constants symbol labels
    def all_constants_id_labels(self):
        '''
        Retrieve all constants' symbol labels in the thermodb.

        Returns
        -------
        res : list
            constants' symbol labels
        '''
        try:
            all_data = self.check_properties()
            constants = [
                const for const in all_data.values()
                if isinstance(const, TableConstants)
            ]

            if not constants:
                logger.warning(
                    'No TableConstants found in the thermodb!')
                return None

            tools = self.comp_tools
            if tools is None:
                logger.error(
                    'CompTools not available to get constants symbol labels')
                return None

            return tools.get_constants_id_labels(constants)
        except Exception as e:
            logger.error(f'Getting constants symbol labels failed!, {e}')
            return None

    # NOTE: get all matrix data structures
    def all_matrix_data_details(self):
        '''
        Retrieve all matrix data's structures in the thermodb.

        Returns
        -------
        res : dict
            matrix data's structure
        '''
        try:
            all_data = self.check_properties()
            data = [
                dt for dt in all_data.values()
                if isinstance(dt, TableMatrixData)
            ]

            if not data:
                logger.warning(
                    'No TableMatrixData found in the thermodb!')
                return None

            tools = self.comp_tools
            if tools is None:
                logger.error(
                    'CompTools not available to get matrix data structure')
                return None

            return tools.get_matrix_data_structure(data)
        except Exception as e:
            logger.error(f'Getting matrix data structure failed!, {e}')
            return None

    # NOTE: get all matrix data identifiers
    def all_matrix_data_identifiers(self):
        '''
        Retrieve all matrix data's identifiers in the thermodb.

        Returns
        -------
        res : list
            matrix data's identifiers
        '''
        try:
            all_data = self.check_properties()
            data = [
                dt for dt in all_data.values()
                if isinstance(dt, TableMatrixData)
            ]

            if not data:
                logger.warning(
                    'No TableMatrixData found in the thermodb!')
                return None

            tools = self.comp_tools
            if tools is None:
                logger.error(
                    'CompTools not available to get matrix data identifiers')
                return None

            return tools.get_matrix_data_identifier(data)
        except Exception as e:
            logger.error(f'Getting matrix data identifiers failed!, {e}')
            return None

    # NOTE: get all matrix data symbol labels
    def all_matrix_data_id_labels(self):
        '''
        Retrieve all matrix data's symbol labels in the thermodb.

        Returns
        -------
        res : list
            matrix data's symbol labels
        '''
        try:
            all_data = self.check_properties()
            data = [
                dt for dt in all_data.values()
                if isinstance(dt, TableMatrixData)
            ]

            if not data:
                logger.warning(
                    'No TableMatrixData found in the thermodb!')
                return None

            tools = self.comp_tools
            if tools is None:
                logger.error(
                    'CompTools not available to get matrix data symbol labels')
                return None

            return tools.get_matrix_data_id_labels(data)
        except Exception as e:
            logger.error(f'Getting matrix data symbol labels failed!, {e}')
            return None

    # NOTE: get all matrix functions' structures
    def all_matrix_function_details(self):
        '''
        Retrieve all matrix functions' structures in the thermodb.

        Returns
        -------
        res : dict
            matrix functions' structure
        '''
        try:
            all_functions = self.check_functions()
            functions = [
                fn for fn in all_functions.values()
                if isinstance(fn, TableMatrixEquation)
            ]

            if not functions:
                logger.warning(
                    'No TableMatrixEquation functions found in the thermodb!')
                return None

            tools = self.comp_tools
            if tools is None:
                logger.error(
                    'CompTools not available to get matrix function structure')
                return None

            return tools.get_matrix_fn_structure(functions)
        except Exception as e:
            logger.error(f'Getting matrix equations structure failed!, {e}')
            return None

    # NOTE: get all matrix functions' identifiers
    def all_matrix_function_identifiers(self):
        '''
        Retrieve all matrix functions' identifiers in the thermodb.

        Returns
        -------
        res : list
            matrix functions' identifiers
        '''
        try:
            all_functions = self.check_functions()
            functions = [
                fn for fn in all_functions.values()
                if isinstance(fn, TableMatrixEquation)
            ]

            if not functions:
                logger.warning(
                    'No TableMatrixEquation functions found in the thermodb!')
                return None

            tools = self.comp_tools
            if tools is None:
                logger.error(
                    'CompTools not available to get matrix function identifiers')
                return None

            return tools.get_matrix_fn_identifier(functions)
        except Exception as e:
            logger.error(f'Getting matrix equations identifiers failed!, {e}')
            return None

    # NOTE: get build metadata
    def build_details(self):
        '''
        Retrieve thermodb build metadata and registered object counts.

        Returns
        -------
        res : dict
            build metadata
        '''
        try:
            properties = self.check_properties()
            functions = self.check_functions()

            constants_count = sum(
                isinstance(value, TableConstants)
                for value in properties.values()
            )
            data_count = sum(
                isinstance(value, TableData)
                for value in properties.values()
            )
            matrix_data_count = sum(
                isinstance(value, TableMatrixData)
                for value in properties.values()
            )
            equations_count = sum(
                isinstance(value, TableEquation)
                for value in functions.values()
            )
            matrix_equations_count = sum(
                isinstance(value, TableMatrixEquation)
                for value in functions.values()
            )

            return {
                "thermodb_name": self.thermodb_name,
                "message": self.message,
                "build_version": self.build_version,
                "build_date": self.build_date,
                "build_timestamp": self.build_timestamp,
                "build_python": self.build_python,
                "build_type": self.build_type,
                "component_name": self.component_name,
                "component_formula": self.component_formula,
                "component_state": self.component_state,
                "properties_count": len(properties),
                "functions_count": len(functions),
                "constants_count": constants_count,
                "data_count": data_count,
                "matrix_data_count": matrix_data_count,
                "equations_count": equations_count,
                "matrix_equations_count": matrix_equations_count
            }
        except Exception as e:
            logger.error(f'Getting build details failed!, {e}')
            return None
