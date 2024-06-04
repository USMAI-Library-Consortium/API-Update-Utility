from lxml import etree

from .api_resource import ApiResource

def default_update_function(resource_id: str, xml_from_get_request: bytes, update_value: any, xpath: str | None = None, operation: str | None = None) -> bytes:
    tree = etree.fromstring(xml_from_get_request)
    el_to_update = tree.xpath(xpath)[0]

    if operation == "update":
        el_to_update.text = update_value
    elif operation == "insert":
        el_to_add = etree.fromstring(update_value)
        el_to_update.insert(-1, el_to_add)
    elif operation == "delete":
        for el_to_delete in tree.xpath(f"{xpath}/{update_value}"):
            el_to_update.remove(el_to_delete)

    return etree.tostring(tree)

class XMLUpdater:
    def __init__(self, update_function: callable = default_update_function, xpath: str | None = None):
        self.update_function = update_function
        self.xpath = xpath

    def run(self, api_resources: list[ApiResource]) -> list[ApiResource]:
        for api_resource in api_resources:
            api_resource.xml_for_update_resquest = self.update_function(api_resource.identifier, api_resource.xml_from_get_request, api_resource.update_value, self.xpath, api_resource.operation)

        return api_resources

