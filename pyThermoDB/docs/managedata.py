# MANAGE DATA
# ===============

# import packages/modules
import os
import yaml


class ManageData:
    # main data
    __reference = {}
    # databook bulk
    __databook_bulk = []
    # databook
    __databook = []
    # table
    __tables = []

    def __init__(self):
        # load reference
        self.__reference = self.load_reference()

        # databook bulk
        self.__databook_bulk = self.get_databook_bulk()

        # databook
        self.__databook = list(self.__databook_bulk.keys())

    @property
    def reference(self):
        return self.__reference

    @property
    def databook(self):
        return self.__databook

    @databook.setter
    def databook(self, value):
        self.__databook = []
        self.__databook = value

    @property
    def tables(self):
        return self.__tables

    @tables.setter
    def tables(self, value):
        self.__tables = []
        self.__tables = value

    def load_reference(self):
        '''
        load reference data from file
        '''
        config_path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), '..', 'config', 'reference.yml')

        with open(config_path, 'r') as f:
            reference = yaml.load(f, Loader=yaml.FullLoader)

        return reference

    def get_databook_bulk(self):
        '''
        Get databook bulk

        Returns
        -------
        databook_list : list
            databook list
        '''
        try:
            databook_list = {}
            references = self.__reference['REFERENCES']

            for databook, databook_data in references.items():
                tables = []
                for table, table_data in databook_data.get('TABLES', {}).items():
                    # check EQUATIONS exists
                    if 'EQUATIONS' in table_data:
                        for eq, eq_data in table_data['EQUATIONS'].items():
                            # save
                            tables.append({
                                'table': table,
                                'equations': [eq_data]
                            })
                    else:
                        tables.append({
                            'table': table,
                            'equations': None
                        })
                databook_list[databook] = tables
            # return
            return databook_list
        except Exception as e:
            raise Exception(e)

    def get_tables(self, databook):
        '''
        Get 
        '''
