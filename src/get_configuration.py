import importlib

class Settings:
    """All user-defined settings required to run the utility."""
    def __init__(self):
        self.update_file: str = None

        self.xpath_for_get_response_verification: str = None
        self.xpath_of_resource_in_put_response: str | None = None
        self.api_url_template: str = None
        self.query_param_api_key: str | None = None

        self.xpaths: list[str] | None = None
        self.xpath_operations: str | list[str] | None = None

        self.dry_run: bool = None
        self.update_limit: int | None = None
        self.retry_failed: bool = None

        self.use_custom_xml_update_function: bool = None
        self.custom_xml_update_function: callable = None


def get_configuration(project_path: str):
    """Reads the user-defined settings from the module in their project folder. Also validates
    settings and sets defaults."""
    
    # ------------- IMPORT SETTINGS MODULE FOR THIS PROJECT ---------------

    # The program settings are in a Python module in the project folder. This allows for comments
    # and user-defined functions. Here, we import this settings module.
    project_settings = importlib.import_module(f"{project_path.replace("/", ".")}.project_settings") # type: ignore

    # -------------- VALIDATIONS AND SETTING DEFAULTS --------------------

    # We need xpaths to run the built-in update function. If the user does not include any, and
    # they're not using a custom xml update function, raise an error.
    if not project_settings.use_custom_xml_update_function and not project_settings.xpath_operations:
        raise ValueError("If you're not using a custom xml update function, operations cannot be None")
    
    xpaths = project_settings.xpaths
    if not isinstance(xpaths, list):
        xpaths = [xpaths]

    # This isn't super important functionally. It just allows the user to use a single xpath operation even 
    # if they want to work on multiple xpaths - it will set the operation for each xpath to that xpath operation.
    expanded_operations = []
    if isinstance(project_settings.xpath_operations, list):
        if not project_settings.use_custom_xml_update_function:
            # We need the number of xpath operations to equal the number of xpaths.
            if len(project_settings.xpath_operations) != len(xpaths):
                raise ValueError(
                    "If you include an array of xpathOperations, it must be equal to the number of xpaths.")
        expanded_operations = project_settings.xpath_operations
    elif isinstance(project_settings.xpath_operations, str):
        operation_to_do_for_all_xpaths = project_settings.xpath_operations
        for _ in xpaths:
            expanded_operations.append(operation_to_do_for_all_xpaths)
    else: expanded_operations = None

    # ---------------- INSTANTIATING THE SETTINGS OBJECT -----------------

    settings = Settings()
    settings.update_file = f"{project_path}/{project_settings.update_file}"
    settings.xpath_for_get_response_verification = project_settings.xpath_for_get_response_verification
    settings.xpath_of_resource_in_put_response = project_settings.xpath_of_resource_in_put_response
    settings.api_url_template = project_settings.api_url_template
    settings.query_param_api_key = project_settings.query_param_api_key
    settings.xpaths = xpaths
    settings.xpath_operations = expanded_operations
    settings.dry_run = project_settings.dry_run
    settings.update_limit = project_settings.update_limit
    settings.retry_failed = project_settings.retry_failed
    settings.use_custom_xml_update_function = project_settings.use_custom_xml_update_function
    settings.custom_xml_update_function = project_settings.custom_xml_update_function

    return settings