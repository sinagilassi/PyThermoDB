# import packages/modules
# external

# internal


class TransMatrixData:
    '''
    Transform class to analyze data from API
    '''
    __data_type = ''

    def __init__(self, api_data_pack):
        self.api_data_pack = api_data_pack
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

        # looping through api_data_pack
        for i, api_component_data in enumerate(self.api_data_pack):
            # set
            component_name = api_component_data['component_name']
            api_data = api_component_data['data']
            # data trans
            data_trans = {}
            # looping through api_data
            for x, y, z, w in zip(api_data['header'], api_data['records'], api_data['unit'], api_data['symbol']):
                # check eq exists
                if x == "Eq":
                    self.eq_id = y
                    # set data type
                    self.__data_type = 'matrix-equations'
                else:
                    self.__data_type = 'matrix-data'

                # set values
                data_trans[str(x)] = {"value": y, "unit": z, "symbol": w}

            # data table
            data_trans['matrix-data'] = api_data

            # save data
            self.data_trans_pack[str(component_name)] = data_trans

        # res
        return self.data_trans_pack
