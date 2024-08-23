from lxml import etree
import requests

from .api_resource import ApiResource

def retrieve_resource(api_resource: ApiResource) -> ApiResource:
    """Get the resource XML from the API, and pretty-print it.
    
    Errors are thrown, to be handled elsewhere."""
    response = requests.get(api_resource.api_url, headers={"Accept": "application/xml"})
    api_resource.xml_from_get_request = etree.tostring(etree.fromstring(response.content), pretty_print=True)

    return api_resource