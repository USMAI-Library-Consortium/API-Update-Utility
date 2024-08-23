import csv 

from .api_resource import ApiResource
from .get_configuration import Settings

def read_update_file(settings: Settings, api_resources_to_exclude: list[str]) -> list[ApiResource]:
    """Read the update file containing the resource IDs to update as well as the values to use
    during the update (one for each xpath).
    
    Takes 'api_resources_to_exclude', which is a list of resource IDs pulled from the previous state
    of the program. It is the same list as 'resources_finished'. This function will skip any of these
    resources."""
    # Resources that this run has available to work on. It may not run all of them if there's an error
    # or if the update limit is set lower.
    api_resources: list[ApiResource] = []
        
    with open(settings.update_file, "r", encoding="utf-8-sig") as uf:
        reader = csv.reader(uf)

        for index, row in enumerate(reader):
            if index == 0:
                # If we are using the built-in XML update function...
                if not settings.use_custom_xml_update_function:
                    # Throw an error if the number of values does not correspond to the number of xpaths
                    number_of_xpaths_provided = len(settings.xpaths)
                    number_of_values_provided = len(row[1:])
                    if number_of_xpaths_provided != number_of_values_provided:
                        raise ValueError("You must provide a value column for each xpath")
                
                # Skip the header
                continue

            identifier = row[0]
            # Skip resources that we set to exclude (they're finished, or they're failed an 'retry_failed'
            # is false)
            if identifier in api_resources_to_exclude:
                continue

            # Create the URL for this resource.
            api_url = settings.api_url_template.replace("<resource_id>", identifier)
            if type(settings.query_param_api_key) == str:
                # Add the Query param API key, stripping ? for safety.
                api_url = api_url + "?" + settings.query_param_api_key.lstrip("?")

            api_resource = ApiResource(identifier=identifier, api_url=api_url, update_values=row[1:])
            api_resources.append(api_resource)
        
    return api_resources