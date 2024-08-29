# MANAGE DATA
# ===============

# import packages/modules
import os
import yaml


class ManageData:
    __reference = {}

    def __init__(self):
        self.__reference = self.load_reference()

    @property
    def reference(self):
        return self.__reference

    def load_reference(self):
        '''
        load reference data from file
        '''
        config_path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), '..', 'config', 'reference.yml')

        with open(config_path, 'r') as f:
            reference = yaml.load(f, Loader=yaml.FullLoader)

        return reference

    def get_databook_list(self):
        '''
        Get databook list

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
                    if table_data is not None:
                        tables.append({
                            'table': table,
                            'equations': table_data.get('EQUATIONS', [])
                        })
                    else:
                        tables.append({
                            'table': table,
                            'equations': None
                        })

                databook_list[databook] = tables

            return databook_list
        except Exception as e:
            raise Exception(e)
