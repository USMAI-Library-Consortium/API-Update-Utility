# --------------- ALWAYS REQUIRED -----------------
# You MUST include the string '<resource_id> where you want the resource ID to be substituted
api_url_template: str = "https://example.com/resource/<resource_id>"
update_file: str = "input.csv"
xpath_for_get_response_verification: str = "REQUIRED"

# If you need it
# Example: "apikey=1234"
query_param_api_key: str | None = None

# REQUIRED unless using a custom XML update function
xpaths: list[str] | None = "REQUIRED"
xpath_operations: str | list[str] | None = "update"

# RECOMMENDED
# This allows the GET and PUT responses to be compared and their
# differences explained! 
xpath_of_resource_in_put_response: str | None = None

# Other settings
dry_run: bool = True
retry_failed: bool = False
update_limit: int | None = None

# Here, you can override the function that updates the resource XML if the built-in one (located in src.xml_updater.default_update_function) doesn't meet your needs.
use_custom_xml_update_function: bool = False
def custom_xml_update_function(resource_id: str, xml_from_get_request: bytes, update_values: list[str], xpaths: list[str] | None = None, operations: str | list[str] | None = None) -> bytes | None:
    # LEAVE THE PARAMETERS BE - this is what this program will pass to this function! 
    # The function is run PER API resource. The output should be a bytes XML object. I suggest using pretty print. Example: etree.tostring(tree, pretty_print=True)
    pass


