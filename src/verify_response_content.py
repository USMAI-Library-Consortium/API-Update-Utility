import logging
from lxml import etree

from .api_resource import ApiResource

def verify_response_content(api_resources: list[ApiResource], test_xpath: str):
    """This method takes an xpath and verifies all ApiResources passed to it. The xpath is user-defined, and
    should point to an element that all API records of this type should have.
    
    In practice, this verifies that the correct response format has been returned by the API. This is in
    lieu of using the status code - it makes it a bit safer."""
    resources_verified: list[ApiResource] = []
    
    for api_resource in api_resources:
        tree = etree.fromstring(api_resource.xml_from_get_request)
        xpath_results = tree.xpath(test_xpath)

        if len(xpath_results) == 0:
            logging.warning(f"Malformed GET response from resource with ID {api_resource.identifier}.")
            api_resource.status = "failed"
        
        resources_verified.append(api_resource)

    return resources_verified