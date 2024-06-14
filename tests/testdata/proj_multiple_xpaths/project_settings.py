update_file: str = "input.csv"

xpath_for_get_response_verification: str = "test_verification_xpath"
xpath_of_resource_in_put_response: str | None = None
api_url_template: str = "https://alma.exlibrisgroup.com/users/<resource_id>"
query_param_api_key: str | None = "apikey=1234"

xpaths: list[str] = ["test_xpath", "test_xpath_2"]
xpath_operations: str | list[str] | None = ["update", "update"]

dry_run: bool = True
update_limit: int | None = None
retry_failed: bool = False

# Here, you can override the function that updates the resource XML if the built-in one (located in src.xml_updater.default_update_function) doesn't meet your needs.
use_custom_xml_update_function: bool = False
def custom_xml_update_function(resource_id: str, xml_from_get_request: bytes, update_values: list, xpaths: str | None = None, operations: list[str] | None = None) -> bytes:
    # LEAVE THE PARAMETERS BE - this is what this program will pass to this function! 
    # The function is run PER API resource. The output should be a bytes XML object. I suggest using pretty print. Example: etree.tostring(tree, pretty_print=True)
    pass


