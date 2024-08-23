import logging
from lxml import etree
from lxml.etree import ElementTree

from .api_resource import ApiResource


def verify_response_content(api_resource: ApiResource, test_xpath: str):
    """This method takes an xpath and verifies all ApiResources passed to it. The xpath is user-defined, and
    should point to an element that all API records of this type should have.

    In practice, this verifies that the correct response format has been returned by the API. This is in
    lieu of using the status code - it makes it a bit safer."""

    # Verify the XML from the GET request is valid.
    if api_resource.xml_from_get_request:
        tree = etree.fromstring(api_resource.xml_from_get_request)
        xpath_results = tree.xpath(test_xpath)

        if len(xpath_results) == 0:
            logging.warning(f"Malformed GET response from resource with ID {api_resource.identifier}. URL: {api_resource.api_url}")
            api_resource.mark_failed()
        else:
            logging.debug(f"Verification for resource {api_resource.identifier} successful.")
            
    return api_resource
