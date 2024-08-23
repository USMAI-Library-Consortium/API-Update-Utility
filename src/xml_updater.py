from lxml import etree
from lxml.etree import Element
import logging

from .api_resource import ApiResource

def default_update_function(resource_id: str, xml_from_get_request: bytes, update_values: list[str] | None, xpaths: list[str] | None = None, operations: str | list[str] | None = None) -> bytes | None:
    """A function that handles updating one or more sections of an XML resource. Should return None IF there's nothing
    to update in this function"""
    tree = etree.fromstring(xml_from_get_request)

    # ---------- OPERATE ON EACH XPATH --------------
    for i, xpath in enumerate(xpaths):
        operation_for_this_xpath = operations[i]
        value_for_this_xpath = update_values[i]

        # ----------- LOGIC FOR UPDATE OPERATION ---------------
        if operation_for_this_xpath == "update":
            try:
                els_to_update = tree.xpath(xpath)

                # Update each element matching the xpath
                for el_to_update in els_to_update:
                    el_to_update.text = value_for_this_xpath
            except:
                logging.warning(f"Element does not exist on resource {resource_id}. Try the 'updateOrInsert' operation instead.")
                raise KeyError()
            
        # -------------- LOGIC FOR UPDATE OR INSERT OPERATION ------------------
        elif operation_for_this_xpath == "updateOrInsert":
            # Remove the last xpath element from the user-defined xpath 
            # (e.g. 'hours' in /vendor/meta/gracePeriod/hours)
            # to get the name of the child element
            child_el_name = xpath.split("/")[-1]

            # Get the parent element. We want to perform updates / insertions for all parent elements.
            parent_el_xpath = xpath.removesuffix(child_el_name).rstrip("/")
            parent_els = tree.xpath(parent_el_xpath)

            for i, parent_el in enumerate(parent_els):
                new_xpath = f"{parent_el_xpath}/{child_el_name}"
                xpath_results = tree.xpath(new_xpath)

                # If there's already one or more elements, update them.
                if len(xpath_results) > 0:
                    for el_to_update in xpath_results:
                        el_to_update.text = value_for_this_xpath

                # If there's no elements, insert the element
                else:
                    # Create the child element
                    el_to_add = Element(child_el_name)
                    el_to_add.text = value_for_this_xpath

                    # Add the child element to the parent element.
                    parent_el.append(el_to_add)

        # ----------- LOGIC FOR INSERT OPERATION --------------
        elif operation_for_this_xpath == "insert":
            # Remove the last xpath element from the user-defined xpath 
            # (e.g. 'hours' in /vendor/meta/gracePeriod/hours)
            # This gets us the element name we want to create.
            el_to_create_name = xpath.split("/")[-1]
            # Create the child element
            el_to_add = Element(el_to_create_name)
            el_to_add.text = value_for_this_xpath

            # Get the parent element, into which we want to insert the child element.
            parent_el_xpath = xpath.removesuffix(el_to_create_name).rstrip("/")
            parent_el = tree.xpath(parent_el_xpath)[0]
            
            # Add the child element to the parent element
            parent_el.append(el_to_add)

        # ------------- LOGIC FOR DELETE OPERATION --------------
        elif operation_for_this_xpath == "delete":
            # The name of the element to delete is the value. This is set for clarity 
            xpath_of_el_to_delete = value_for_this_xpath

            for i, el_to_update in enumerate(tree.xpath(xpath)):
                # Add an index to perform this operation on all elements returned by the xpath
                # UNLESS a specific index was specified by the user.
                index = "" if xpath.endswith("]") else f"[{i+1}]"
                for el_to_delete in tree.xpath(f"{xpath}{index}{"/" if not xpath_of_el_to_delete.startswith("/") else ""}{xpath_of_el_to_delete}"):
                    el_to_update.remove(el_to_delete)

    return etree.tostring(tree, pretty_print=True)


class XMLUpdater:
    """Class that holds the settings for the XML update, including which xpaths are used, which update
    function is used, and which operation should be done on each xpath."""
    def __init__(self, custom_update_function: callable = None, xpaths: list[str] | None = None, operations: list[str] | str | None = None):
        self.update_function = custom_update_function if custom_update_function else default_update_function
        self.xpaths = xpaths
        self.operations = operations

    def update_resource(self, api_resource: ApiResource) -> ApiResource:
        """Create the updated XML for a resource."""

        # Run this operation on API resources that have pending status and have XML from the get request
        if api_resource.status == "pending" and api_resource.xml_from_get_request:
            try:
                logging.info(f"Updating XML for resource {api_resource.identifier}")
                updated_xml = self.update_function(
                    api_resource.identifier, api_resource.xml_from_get_request, api_resource.update_values, self.xpaths, self.operations)
                
                if updated_xml:
                    api_resource.xml_for_update_request = updated_xml
                else:
                    logging.info(f"Skipping update request for resource '{api_resource.identifier}' because the XML update function returned nothing. Marking it as complete.")
                    api_resource.mark_successful()
            except KeyError:
                api_resource.mark_failed()
            except:
                logging.exception(f"There was an exception in updating resource {api_resource.identifier}")
                api_resource.mark_failed()

        return api_resource
