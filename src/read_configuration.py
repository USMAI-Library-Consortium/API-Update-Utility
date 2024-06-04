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

        configuration = {
            "xpath": unparsed_configuration["xpath"],
            "xpath_operation": unparsed_configuration["xpathOperation"],
            "dry_run": unparsed_configuration["dryRun"],
            "request_limit": request_limit
        }

        api_resources: list[ApiResource] = []
        
        with open(f"{project_path}/{unparsed_configuration["updateFile"]}", "r", encoding="utf-8-sig") as uf:
            reader = csv.DictReader(uf)

            for row in reader:
                identifier = row["Resource ID"]
                if identifier not in api_resources_finished:
                    api_url = unparsed_configuration["apiUrl"].replace("<resource_id>", identifier)
                    api_resource = ApiResource(identifier, api_url, row["Value"], operation=configuration["xpath_operation"])
                    api_resources.append(api_resource)
            
        return configuration, api_resources
    except KeyError as ke:
        raise ValueError(f"Required input not found: {ke.__str__()}")