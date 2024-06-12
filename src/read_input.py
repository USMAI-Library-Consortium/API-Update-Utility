import csv 

from .api_resource import ApiResource

def read_input(configuration, api_resources_finished: list[str]) -> list[ApiResource]:
    api_resources: list[ApiResource] = []
        
    with open(configuration["update_file"], "r", encoding="utf-8-sig") as uf:
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

                api_url = configuration["api_url_template"].replace("<resource_id>", identifier)
                if "query_param_api_key" in configuration.keys() and type(configuration["query_param_api_key"]) == str:
                    api_url = api_url + "?" + configuration["query_param_api_key"].lstrip("?")

                api_resource = ApiResource(identifier, api_url, row[1:])
                api_resources.append(api_resource)
        
    return api_resources