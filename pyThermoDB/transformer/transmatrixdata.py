# import packages/modules
# external

# internal


class TransMatrixData:
    '''
    Transform class to analyze data from API
    '''
    __data_type = ''

    def __init__(
            self,
            api_data_pack,
            component_delimiter: str = '-'
    ):
        # NOTE: set attributes
        self.api_data_pack = api_data_pack
        self.component_delimiter = component_delimiter.strip()
        self.eq_id = None

        # NOTE: transformed data
        self.data_trans_pack = {}

    @property
    def data_type(self):
        return self.__data_type

    @data_type.setter
    def data_type(self, value):
        self.__data_type = value

    def trans(self):
        '''
        Transform the data loaded from API,
        It consists of:
            step 1: display api data
                data['header'],['records'],['unit']
            step 2: transform to dict
        '''
        self.data_trans_pack = {}

        # SECTION: looping through api_data_pack
        for i, api_component_data in enumerate(self.api_data_pack):
            # NOTE: set
            component_name = api_component_data['component_name']
            api_data = api_component_data['data']
            # optional fields
            component_formula = api_component_data.get(
                'component_formula', None
            )
            component_state = api_component_data.get('component_state', None)

            # data trans
            data_trans = {}
            # looping through api_data
            for x, y, z, w in zip(
                api_data['header'], api_data['records'], api_data['unit'], api_data['symbol']
            ):
                # check eq exists
                if x == "Eq":
                    self.eq_id = y
                    # set data type
                    self.__data_type = 'matrix-equations'
                else:
                    self.__data_type = 'matrix-data'

                # set values
                data_trans[str(x)] = {
                    "value": y, "unit": z, "symbol": w
                }

            # NOTE: data table
            data_trans['matrix-data'] = api_data

            # SECTION: set name
            self.data_trans_pack[str(component_name)] = data_trans
            # >> name-state if available
            # set state
            if component_state is not None:
                key = f"{component_name}{self.component_delimiter}{component_state}"
                self.data_trans_pack[str(key)] = data_trans

            # SECTION: set formula and state if available
            if component_formula is not None:
                # >> save
                self.data_trans_pack[str(component_formula)] = data_trans

                # >> formula-state if available
                if component_state is not None:
                    key = f"{component_formula}{self.component_delimiter}{component_state}"
                    self.data_trans_pack[str(key)] = data_trans

        # res
        return self.data_trans_pack
