# import packages/modules
# externals
import requests
# internal
from pyThermoDB.config import API_URL

class Manage:
    def __init__(self, api_url, databook_id, table_id):
        self.api_url = api_url
        self.databook_id = databook_id
        self.table_id = table_id
        
    def get_data(self):
        # parameters
        reqtype = 'read'
        fid = '1'
        parameters = f"reqtype={reqtype}&fid={fid}"
        # all data
        get_all = self.api_url + parameters
        response = requests.get(get_all)

        if response.status_code == 200:
            payload = response.json()
            data = payload['records']
            # header
            header = data[0]
            # records
            records = data[1:]
            # find the index
            name_id = header.index('Name')
            component_names = [record[name_id] for record in records]
            print(component_names)
        else:
            print("error", response.status_code)
    