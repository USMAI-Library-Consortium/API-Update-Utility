import lxml.etree
import xmltodict
from deepdiff.diff import DeepDiff
import lxml

from .api_resource import ApiResource

class Comparator:
    def __init__(self, xpath_of_resource_in_put_response: str | None = None):
        self.xpath_of_resource_in_put_response = xpath_of_resource_in_put_response

    def compare(self, api_resources: list[ApiResource], dry_run: bool=False):
        results: dict = {}
        for api_resource in api_resources:
            resource_from_put_request = None
            if dry_run:
                # Only run the process for api resources that are pending (failed would indicate
                # the GET response failed or updating the body XML failed)
                if api_resource.status != "pending":
                    continue
                resource_from_put_request = api_resource.xml_for_update_request
            else:
                # Production run
                # Only run the process for api resources that were updated successfully
                if api_resource.status != "success":
                    continue
                
                resource_from_put_request = api_resource.update_response
                if self.xpath_of_resource_in_put_response:
                    resource_from_put_request = self.pull_xml_element_from_dict(resource_from_put_request, self.xpath_of_resource_in_put_response)

            diff = DeepDiff(xmltodict.parse(api_resource.xml_from_get_request), xmltodict.parse(resource_from_put_request))
            
            # If there is no difference between the two, add the string "No Difference" instead
            if len(diff.keys()) == 0:
                diff = "No Difference"
            
            results[api_resource.identifier] = diff
        
        return results
    
    @staticmethod
    def pull_xml_element_from_dict(xml: bytes, xpath: str) -> bytes:
        tree: lxml.etree._ElementTree = lxml.etree.fromstring(xml)
        
        try:
            resource = tree.xpath(xpath)[0]
        except IndexError:
            raise ValueError(f"Xpath for finding resource in PUT request is not valid: {xpath}")

        return lxml.etree.tostring(resource, pretty_print=True)