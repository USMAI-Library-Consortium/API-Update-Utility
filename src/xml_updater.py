from lxml import etree
from lxml.etree import Element
import logging

from .api_resource import ApiResource


def default_update_function(resource_id: str, xml_from_get_request: bytes, update_values: list, xpaths: str | None = None, operations: list[str] | None = None) -> bytes:
    tree = etree.fromstring(xml_from_get_request)

    for i, xpath in enumerate(xpaths):
        if operations[i] == "update":
            try:
                el_to_update = tree.xpath(xpath)[0]
                el_to_update.text = update_values[i]
            except:
                logging.warning(f"Element does not exist on resource {
                                resource_id}. Try the 'updateOrInsert' operation instead.")
                raise KeyError()
        if operations[i] == "updateOrInsert":
            xpath_results = tree.xpath(xpath)
            if len(xpath_results) > 0:
                el_to_update = xpath_results[0]
                el_to_update.text = update_values[i]
            else:
                # Insert the element
                # Remove the last xpath statement (e.g. 'hours' in /vendor/meta/gracePeriod/hours)
                child_el_name = xpath.split("/")[-1]
                parent_el_xpath = xpath.removesuffix(child_el_name).rstrip("/")
                parent_el = tree.xpath(parent_el_xpath)[0]

                el_to_add = Element(child_el_name)
                el_to_add.text = update_values[i]
                parent_el.insert(-1, el_to_add)

        elif operations[i] == "insert":
            el_to_update = tree.xpath(xpath)[0]
            el_to_add = etree.fromstring(update_values[i])
            el_to_update.insert(-1, el_to_add)
        elif operations[i] == "delete":
            el_to_update = tree.xpath(xpath)[0]
            for el_to_delete in tree.xpath(f"{xpath}/{update_values[i]}"):
                el_to_update.remove(el_to_delete)

    return etree.tostring(tree, pretty_print=True)


class XMLUpdater:
    def __init__(self, update_function: callable = None, xpaths: list[str] | None = None, operations: list[str] | str | None = None):
        if update_function == None:
            self.update_function = default_update_function
        else: self.update_function = update_function
        self.xpaths = xpaths
        self.operations = operations

    def run(self, api_resources: list[ApiResource]) -> list[ApiResource]:
        for api_resource in api_resources:
            if api_resource.status == "pending" and api_resource.xml_from_get_request:
                try:
                    api_resource.xml_for_update_request = self.update_function(
                        api_resource.identifier, api_resource.xml_from_get_request, api_resource.update_values, self.xpaths, self.operations)
                except KeyError:
                    api_resource.status = "failed"

        return api_resources
