import requests

from .api_resource import ApiResource
from .backup import Backup
from .verify_response_content import verify_response_content

def retrieve_resources(api_resources: list[ApiResource], update_limit: int):
    final_update_limit = None
    if update_limit and update_limit > 0:
        final_update_limit = update_limit

    for index, api_resource in enumerate(api_resources):
        if final_update_limit and (index + 1) > final_update_limit:
            break

        response = requests.get(api_resource.api_url, headers={"Accept": "application/xml"})
        api_resource.xml_from_get_request = response.content

    return api_resources