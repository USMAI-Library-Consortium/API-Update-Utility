import json
import csv

from .api_resource import ApiResource

def read_configuration(project_path: str, api_resources_finished: list[str]) -> tuple[dict, list[ApiResource]]:
    try:
        with open(f"{project_path}/config.json", "r") as f:
            unparsed_configuration = json.load(f)

        request_limit = None
        if unparsed_configuration["requestLimit"] > 0:
            request_limit = unparsed_configuration["requestLimit"]

        # If the user just wants to do one type of operation (for example, "update"), then set that operation
        # true for all xpaths by creating an array with the same length as the xpaths.
        expanded_operations = []
        if isinstance(unparsed_configuration["xpathOperations"], str):
            operation_to_do_for_all_xpaths = unparsed_configuration["xpathOperations"]

            for _ in range(0,len(unparsed_configuration["xpaths"])):
                expanded_operations.append(operation_to_do_for_all_xpaths)
        else:
            number_of_xpath_operations = len(unparsed_configuration["xpathOperations"])
            number_of_xpaths = len(unparsed_configuration["xpaths"])
            if number_of_xpath_operations != number_of_xpaths:
                raise ValueError("If you include an array of xpathOperations, it must be equal to the number of xpaths.")
            expanded_operations = unparsed_configuration["xpathOperations"]

        configuration = {
            "xpaths": unparsed_configuration["xpaths"],
            "xpath_operations": expanded_operations,
            "test_xpath": unparsed_configuration["xpathForGetResponseVerification"],
            "dry_run": unparsed_configuration["dryRun"],
            "request_limit": request_limit,
        }

        api_resources: list[ApiResource] = []
        
        with open(f"{project_path}/{unparsed_configuration["updateFile"]}", "r", encoding="utf-8-sig") as uf:
            reader = csv.reader(uf)

            for index, row in enumerate(reader):
                if index == 0:
                    # Throw an error if the number of values does not correspond to the number of xpaths
                    number_of_xpaths_provided = len(configuration["xpaths"])
                    number_of_values_provided = len(row[1:])
                    if number_of_xpaths_provided != number_of_values_provided:
                        raise ValueError("The number of values does not correspond to the number of xpaths.")
                    continue

                identifier = row[0]
                if identifier not in api_resources_finished:
                    api_url = unparsed_configuration["apiUrlTemplate"].replace("<resource_id>", identifier)
                    api_resource = ApiResource(identifier, api_url, row[1:])
                    api_resources.append(api_resource)
            
        return configuration, api_resources
    except KeyError as ke:
        raise ValueError(f"Required input not found: {ke.__str__()}")