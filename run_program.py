import argparse
import os
import logging
import shutil
import requests
import json

from src.get_configuration import get_configuration
from src.read_input import read_input
from src.retrieve_resource import retrieve_resources
from src.backup import Backup
from src.xml_updater import XMLUpdater
from src.progress_manager import ProgressManager
from src.verify_response_content import verify_response_content
from src.comparator import Comparator


def main(project_name: str):
    project_path = f"projects/{project_name}"
    if not os.path.exists(project_path):
        raise FileNotFoundError(
            f"Project '{project_name}' has not been initialized.")

    # Initialize logger
    logging.basicConfig(filename=f"{project_path}/logs.log",
                        format='%(levelname)s:%(asctime)s: %(message)s', level=logging.INFO)
    logging.info("Starting API Update Utility...")
    logging.info(f"Project: {project_name}")

    # Read the configuration
    settings = get_configuration(f"projects/{project_name}")

    # Initialize the progress manager, which takes care of managing which updates are
    # done, which are in progress, and which have failed.
    pm = ProgressManager(
        project_path, retry_failed=settings.retry_failed)

    # Get the API resources from the CSV, excluding ones that were done previously
    api_resources = read_input(
        settings, api_resources_to_exclude=pm.previously_completed_api_resources)

    if len(api_resources) == 0:
        logging.info(f"Exiting - no resources to update.{
                     " (retryFailed is set to false, there may be failed resources. Check 'progress.csv')" if not settings.retry_failed else " Congrats!"}")
        return

    # Log some basic init information
    logging.info(f"Resources to update: {settings.update_limit}")
    logging.info(f"Dry run mode: {settings.dry_run}")

    # Retrieve the resources
    logging.info("Beginning API GET retrievals")
    api_resources = retrieve_resources(
        api_resources, settings.update_limit)
    logging.info("Done")

    # Verify the responses
    logging.info("Beginning GET response verification...")
    verify_response_content(api_resources, settings.xpath_for_get_response_verification)
    logging.info("Done")

    # Backup the responses that passed
    if settings.dry_run == False:
        logging.info("Beginning backup process...")
        backuper = Backup(project_path=project_path)
        for api_resource in api_resources:
            if api_resource.status == "pending" and api_resource.xml_from_get_request:
                result = backuper.backup(
                    api_resource.identifier, api_resource.xml_from_get_request)
                if result == -1:
                    logging.error(f"Could not back up vendor {
                                  api_resource.identifier}")
                    api_resource.status = "failed"
            else:
                logging.info(f"Skipping backup of resource {
                             api_resource.identifier} due to status '{api_resource.status}'.")
        logging.info("Done")

    # Update the XML bodies
    logging.info("Beginning body update process...")
    xu = XMLUpdater(update_function=settings.custom_xml_update_function if settings.use_custom_xml_update_function else None,
                    xpaths=settings.xpath, operations=settings.xpath_operations)
    api_resources = xu.run(api_resources)
    logging.info("Done")

    comparator = Comparator(settings.xpath_of_resource_in_put_response)

    if settings.dry_run == True:
        dry_run_folder = f"{project_path}/dryRun"
        logging.info(f"Dry run mode: saving resources to {dry_run_folder}.")
        # Reset dry run folder
        if os.path.exists(dry_run_folder):
            shutil.rmtree(dry_run_folder)
        os.mkdir(dry_run_folder)

        for api_resource in api_resources:
            if api_resource.status == "pending" and api_resource.xml_for_update_request:
                resource_file_path = f"{
                    dry_run_folder}/{Backup.normalize_identifier(api_resource.identifier)}.xml"
                with open(resource_file_path, "wb") as f:
                    f.write(api_resource.xml_for_update_request)

        with open(f"{dry_run_folder}/comparisons.json", "w") as f:
            json.dump(comparator.compare(api_resources, dry_run=True), f, indent=2)

        logging.info("Dry run complete.")
        return
    else:
        logging.info("Beginning production update process...")
        # Run the actual utility
        session = requests.Session()
        try:
            for api_resource in api_resources:
                # only run on resources that are pending and have XML ready
                if api_resource.status == "pending" and api_resource.xml_for_update_request:
                    response = session.put(api_resource.api_url, data=api_resource.xml_for_update_request, headers={
                                           "Content-Type": "application/xml"})
                    if response.status_code == 200:
                        api_resource.status = "success"
                        logging.info(
                            f"Resource {api_resource.identifier} updated successfully.")
                    else:
                        api_resource.status = "failed"
                        logging.warning(f"Resource {api_resource.identifier} NOT UPDATED SUCCESSFULLY. Status code: {
                                        response.status_code}")
                    api_resource.update_response = response.content

            logging.info("Done")

            # Compare the resource in the GET to that of the PUT, to see
            # what changed.
            if settings.xpath_of_resource_in_put_response:
                logging.info("Beginning comparison of GET / PUT responses...")
                with open(f"{project_path}/comparisons.json", "w") as f:
                    logging.info(f"Saving comparison to {
                                project_path}/comparisons.json")
                    json.dump(comparator.compare(api_resources), f, indent=2)
                    logging.info("Done.")
            else:
                print("Skipping Comparator - no 'xpath_of_resource_in_put_response'")
        finally:
            logging.info("Saving state...")
            pm.save_state(api_resources)
            logging.info("Done.")
        logging.info("Production update done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "project_name", help="The name of the project to generate.", type=str)
    args = parser.parse_args()

    main(args.project_name)