import lxml.etree
import xmltodict
import json
from deepdiff.diff import DeepDiff
import lxml
import logging
from .api_resource import ApiResource

class Comparator:
    def __init__(self, xpath_of_resource_in_put_response: str | None = None):
        self.xpath_of_resource_in_put_response = xpath_of_resource_in_put_response

    def compare(self, api_resources: list[ApiResource], dry_run: bool=False) -> dict:
        results: dict = {}
        for api_resource in api_resources:
            updated_resource = None

            if dry_run:
                # Only run the process for api resources that are pending (failed would indicate
                # the GET response failed or updating the body XML failed)
                if api_resource.status != "pending":
                    continue

                if not api_resource.xml_for_update_request:
                    if api_resource.xml_from_get_request:
                        results[api_resource.identifier] = "Update will not be performed."
                    
                    continue

                updated_resource = api_resource.xml_for_update_request
            else:
                # Production run
                # Only run the process for api resources that were updated successfully
                if api_resource.status != "success":
                    continue

                if not api_resource.xml_for_update_request:
                    results[api_resource.identifier] = "Update was not run; XML update returned empty update body."
                    continue
                
                updated_resource = api_resource.update_response
                if self.xpath_of_resource_in_put_response:
                    try:
                        updated_resource = self.pull_xml_element_from_dict(updated_resource, self.xpath_of_resource_in_put_response, api_resource.identifier)
                    except ValueError as ve:
                        logging.exception(ve.__str__())
                        results[api_resource.identifier] = ve.__str__()
                        continue

            diff = DeepDiff(xmltodict.parse(api_resource.xml_from_get_request), xmltodict.parse(updated_resource))
            if diff: 
                diff = diff.to_json()
                diff = json.loads(diff)
            
            # If there is no difference between the two, add the string "No Difference" instead
            if len(diff.keys()) == 0:
                diff = "No Difference"
            
            results[api_resource.identifier] = diff
        
        return results
    
    @staticmethod
    def pull_xml_element_from_dict(xml: bytes, xpath: str, identifier: str) -> bytes:
        tree: lxml.etree._ElementTree = lxml.etree.fromstring(xml)
        
        try:
            resource = tree.xpath(xpath)[0]
        except IndexError:
            raise ValueError(f"Could not find xpath '{xpath}' in PUT response for resource '{identifier}'; skipping comparison.")

        return lxml.etree.tostring(resource, pretty_print=True)