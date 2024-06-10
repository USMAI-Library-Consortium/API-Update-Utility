import argparse
import os
import logging

from src.read_configuration import read_configuration
from src.retrieve_resource import retrieve_resources
from src.backup import Backup
from src.xml_updater import XMLUpdater
from src.progress_manager import ProgressManager
from src.verify_response_content import verify_response_content

def main(project_name: str):
    project_path = f"projects/{project_name}"
    
    if not os.path.exists(project_path):
        raise FileNotFoundError(f"Project '{project_name}' has not been initialized.")
    
    # Get the information from the files
    pm = ProgressManager(project_path)
    configuration, api_resources = read_configuration(f"projects/{project_name}", pm.previously_completed_api_resources)

    # Retrieve the resources
    backuper = Backup(project_path=project_path)
    api_resources = retrieve_resources(api_resources, configuration["request_limit"], backuper)

    # Verify the responses
    api_resources = verify_response_content(api_resources, configuration["test_xpath"])

    # Update the XML bodies
    xu = XMLUpdater(xpaths=configuration["xpaths"], operations=configuration["xpath_operations"])
    api_resources = xu.run(api_resources)

    if configuration["dry_run"] == True:
        dry_run_folder = f"{project_path}/dryRun"
        if not os.path.exists(dry_run_folder):
            os.mkdir(dry_run_folder)
        
        for api_resource in api_resources:
            if api_resource.status == "pending":
                resource_file_path = f"{dry_run_folder}/{Backup.normalize_identifier(api_resource.identifier)}.xml"
                with open(resource_file_path, "wb") as f:
                    f.write(api_resource.xml_for_update_resquest)

        logging.info("Dry run complete.")
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", help="The name of the project to generate.", type=str)
    args = parser.parse_args()

    main(args.project_name)