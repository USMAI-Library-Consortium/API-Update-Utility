from lxml import etree

from .api_resource import ApiResource

def default_update_function(resource_id: str, xml_from_get_request: bytes, update_values: list, xpaths: str | None = None, operations: list[str] | None = None) -> bytes:
    tree = etree.fromstring(xml_from_get_request)

    for i, xpath in enumerate(xpaths):
        el_to_update = tree.xpath(xpath)[0]

        if operations[i] == "update":
            el_to_update.text = update_values[0]
        elif operations[i] == "insert":
            el_to_add = etree.fromstring(update_values[0])
            el_to_update.insert(-1, el_to_add)
        elif operations[i] == "delete":
            for el_to_delete in tree.xpath(f"{xpath}/{update_values[0]}"):
                el_to_update.remove(el_to_delete)

    return etree.tostring(tree)

class XMLUpdater:
    def __init__(self, update_function: callable = default_update_function, xpaths: list[str] | None = None, operations: list[str] | str | None = None):
        self.update_function = update_function
        self.xpaths = xpaths
        self.operations = operations

    def run(self, api_resources: list[ApiResource]) -> list[ApiResource]:
        for api_resource in api_resources:
            if api_resource.status == "pending":
                api_resource.xml_for_update_resquest = self.update_function(api_resource.identifier, api_resource.xml_from_get_request, api_resource.update_values, self.xpaths, self.operations)

        return api_resources

