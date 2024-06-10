import requests

from .api_resource import ApiResource
from .backup import Backup

def retrieve_resources(api_resources: list[ApiResource], request_limit: int, backuper: Backup):
    api_resources_with_get: list[ApiResource] = [] 
    final_request_limit = None
    if request_limit and request_limit > 0:
        final_request_limit = request_limit

    for index, api_resource in enumerate(api_resources):
        if (index + 1) > final_request_limit:
            break

        response = requests.get(api_resource.api_url, headers={"Accept": "application/xml"})
        api_resource.xml_from_get_request = response.content

        backuper.backup(api_resource.identifier, api_resource.xml_from_get_request)

    return api_resources_with_get