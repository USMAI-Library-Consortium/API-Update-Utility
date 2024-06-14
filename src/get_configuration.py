import importlib

def get_configuration(project_path: str):
    project_settings = importlib.import_module(f"{project_path.replace("/", ".")}.project_settings") # type: ignore

    # We need operations to run the built-in update function. If the user does not include any, raise an error
    if not project_settings.use_custom_xml_update_function and not project_settings.xpath_operations:
        raise ValueError("If you're not using a custom xml update function, operations cannot be None")

    # If the user just wants to do one type of operation (for example, "update"), then set that operation
    # true for all xpaths by creating an array with the same length as the xpaths.
    expanded_operations = []
    if isinstance(project_settings.xpath_operations, list):
        number_of_xpath_operations = len(project_settings.xpath_operations)
        print(project_settings.xpath_operations)
        number_of_xpaths = len(project_settings.xpaths)
        print(project_settings.xpaths)
        if number_of_xpath_operations != number_of_xpaths:
            raise ValueError(
                "If you include an array of xpathOperations, it must be equal to the number of xpaths.")

        expanded_operations = project_settings.xpath_operations
    else:
        operation_to_do_for_all_xpaths = project_settings.xpath_operations

        for _ in range(0, len(project_settings.xpaths)):
            expanded_operations.append(operation_to_do_for_all_xpaths)

    project_settings.xpath_operations = expanded_operations

    project_settings.update_file = f"{project_path}/{project_settings.update_file}"

    return project_settings