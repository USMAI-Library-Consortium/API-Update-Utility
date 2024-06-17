import csv 

from .api_resource import ApiResource
from .get_configuration import Settings

def read_input(settings: Settings, api_resources_to_exclude: list[str]) -> list[ApiResource]:
    api_resources: list[ApiResource] = []
        
    with open(settings.update_file, "r", encoding="utf-8-sig") as uf:
        reader = csv.reader(uf)

        for index, row in enumerate(reader):
            if index == 0 and not settings.use_custom_xml_update_function:
                # Throw an error if the number of values does not correspond to the number of xpaths when NOT using a
                # custom XML updating function
                number_of_xpaths_provided = len(settings.xpaths)
                number_of_values_provided = len(row[1:])
                if not settings.use_custom_xml_update_function and (number_of_xpaths_provided != number_of_values_provided):
                    raise ValueError("The number of values does not correspond to the number of xpaths.")
                continue

            identifier = row[0]
            if identifier not in api_resources_to_exclude:

                api_url = settings.api_url_template.replace("<resource_id>", identifier)
                if type(settings.query_param_api_key) == str:
                    api_url = api_url + "?" + settings.query_param_api_key.lstrip("?")

                api_resource = ApiResource(identifier, api_url, row[1:])
                api_resources.append(api_resource)
        
    return api_resources