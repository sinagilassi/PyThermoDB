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
        
    def component_list(self) -> list:
        # parameters
        reqtype = 'read'
        id = str(self.databook_id).strip()
        fid = str(self.table_id).strip() 
        parameters = f"?reqtype={reqtype}&id={id}&fid={fid}"
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
            for i, item in enumerate(header):
                if item.lower() == "name":
                    name_id = int(i)
            # component names
            component_names = [record[name_id] for record in records]
            return component_names
        else:
            print("error", response.status_code)
            return []
    
    def component_info(self, component_name):
        '''
        get component info
        '''
        # parameters
        reqtype = 'search'
        id = str(self.databook_id).strip()
        fid = str(self.table_id).strip() 
        parameters = f"?reqtype={reqtype}&id={id}&fid={fid}&name={component_name}"
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
            for i, item in enumerate(header):
                if item.lower() == "name":