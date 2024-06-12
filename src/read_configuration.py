import json


def read_configuration(project_path: str) -> dict:
    try:
        with open(f"{project_path}/config.json", "r") as f:
            unparsed_configuration = json.load(f)

        update_limit = None
        if unparsed_configuration["updateLimit"] and unparsed_configuration["updateLimit"] > 0:
            update_limit = unparsed_configuration["updateLimit"]

        # If the user just wants to do one type of operation (for example, "update"), then set that operation
        # true for all xpaths by creating an array with the same length as the xpaths.
        expanded_operations = []
        if isinstance(unparsed_configuration["xpathOperations"], str):
            operation_to_do_for_all_xpaths = unparsed_configuration["xpathOperations"]

            for _ in range(0, len(unparsed_configuration["xpaths"])):
                expanded_operations.append(operation_to_do_for_all_xpaths)
        else:
            number_of_xpath_operations = len(
                unparsed_configuration["xpathOperations"])
            number_of_xpaths = len(unparsed_configuration["xpaths"])
            if number_of_xpath_operations != number_of_xpaths:
                raise ValueError(
                    "If you include an array of xpathOperations, it must be equal to the number of xpaths.")

            expanded_operations = unparsed_configuration["xpathOperations"]

        configuration = {
            "xpaths": unparsed_configuration["xpaths"],
            "xpath_operations": expanded_operations,
            "test_xpath": unparsed_configuration["xpathForGetResponseVerification"],
            "xpath_of_resource_in_put_response": unparsed_configuration["xpathOfResourceInPutResponse"],
            "dry_run": unparsed_configuration["dryRun"],
            "update_limit": update_limit,
            "retry_failed": unparsed_configuration["retryFailed"],
            "update_file": f"{project_path}/{unparsed_configuration["updateFile"]}",
            "api_url_template": unparsed_configuration["apiUrlTemplate"],
            "query_param_api_key": unparsed_configuration["queryParamAPIKey"]
        }

        return configuration
    except KeyError as ke:
        raise ValueError(f"Required input not found: {ke.__str__()}")
