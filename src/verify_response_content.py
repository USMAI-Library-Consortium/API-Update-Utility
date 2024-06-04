import logging
from lxml import etree

from .api_resource import ApiResource

def verify_response_content(api_resources: list[ApiResource], test_xpath: str, xml_to_verify_str: str = "xml_from_get_request"):
    """This method takes an xpath and verifies all ApiResources passed to it. The xpath is user-defined, and
    should point to an element that all API records of this type should have.
    
    In practice, this verifies that the correct response format has been returned by the API. This is in
    lieu of using the status code - it makes it a bit safer."""
    resources_verified: list[ApiResource] = []
    
    for api_resource in api_resources:
        xml_to_verify = None
        if xml_to_verify_str == "xml_from_get_request":
            xml_to_verify = api_resource.xml_from_get_request
        elif xml_to_verify_str == "xml_for_update_resquest":
            xml_to_verify = api_resource.xml_for_update_resquest
        elif xml_to_verify_str == "update_response":
            xml_to_verify = api_resource.update_response

        tree = etree.fromstring(xml_to_verify)
        xpath_results = tree.xpath(test_xpath)

        if len(xpath_results) == 0:
            logging.warning(f"Malformed response from resource with ID {api_resource.identifier}. (Run on: {xml_to_verify_str})")
            api_resource.status = "failed"
        
        resources_verified.append(api_resource)

    return resources_verified