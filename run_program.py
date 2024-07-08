import argparse
import os
import logging
import shutil
import requests
import json
from tqdm import tqdm

from src.get_configuration import get_configuration
from src.read_input import read_input
from src.retrieve_resource import retrieve_resource
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

    # Initialize the different components of the link updater
    pm = ProgressManager(
        project_path, retry_failed=settings.retry_failed)
    backuper = Backup(project_path=project_path)
    xu = XMLUpdater(update_function=settings.custom_xml_update_function if settings.use_custom_xml_update_function else None,
                        xpaths=settings.xpaths, operations=settings.xpath_operations)
    comparator = Comparator(settings.xpath_of_resource_in_put_response)

    # Create folders to save resources
    if settings.dry_run == True:
        dry_run_folder = f"{project_path}/dryRun"
        logging.info(f"Dry run mode: saving resources to {dry_run_folder}.")
        # Reset dry run folder
        if os.path.exists(dry_run_folder):
            shutil.rmtree(dry_run_folder)
        os.mkdir(dry_run_folder)

    session = requests.Session()

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

    final_update_limit = None
    if settings.update_limit and settings.update_limit > 0:
        final_update_limit = settings.update_limit

    try:
        for index in tqdm(range(final_update_limit)):
            logging.info(f"Working on resource {api_resources[index].identifier}...")
            logging.debug("Retrieving GET request...")
            api_resource_with_xml = retrieve_resource(api_resources[index])
            logging.debug("Done.")

            # Verify the responses
            logging.debug("Verifying response content...")
            verified_api_resource = verify_response_content(api_resource_with_xml, settings.xpath_for_get_response_verification)
            logging.debug("Done.")

            # Backup the response if it passed
            if settings.dry_run == False:
                if verified_api_resource.status == "pending" and verified_api_resource.xml_from_get_request:
                    logging.debug("Backing up resource...")
                    result = backuper.backup(
                        verified_api_resource.identifier, verified_api_resource.xml_from_get_request)
                    if result == -1:
                        logging.error(f"Could not back up vendor {
                                    verified_api_resource.identifier}")
                        verified_api_resource.status = "failed"
                    logging.debug("Done")
                else:
                    logging.debug(f"Skipping backup of resource {
                                verified_api_resource.identifier} due to status '{verified_api_resource.status}'.")

            logging.debug("Updating XML...")
            resource_with_updated_xml = xu.update_resource(verified_api_resource)
            logging.debug("Done.")

            if settings.dry_run == True:
                logging.debug("Saving dry run resource...")
                if resource_with_updated_xml.status == "pending" and resource_with_updated_xml.xml_for_update_request:
                    resource_file_path = f"{
                        dry_run_folder}/{Backup.normalize_identifier(resource_with_updated_xml.identifier)}.xml"
                    with open(resource_file_path, "wb") as f:
                        f.write(resource_with_updated_xml.xml_for_update_request)
                    logging.debug("Done")

                # with open(f"{dry_run_folder}/comparisons.json", "w") as f:
                #     json.dump(comparator.compare(resource_with_updated_xmls, dry_run=True), f, indent=2)
            else:
                logging.info("Running PUT update...")
                # only run on resources that are pending and have XML ready
                if resource_with_updated_xml.status == "pending" and resource_with_updated_xml.xml_for_update_request:
                    response = session.put(resource_with_updated_xml.api_url, data=resource_with_updated_xml.xml_for_update_request, headers={
                                            "Content-Type": "application/xml"})
                    if response.status_code == 200:
                        resource_with_updated_xml.status = "success"
                        logging.info(
                            f"Resource {resource_with_updated_xml.identifier} updated successfully.")
                    else:
                        resource_with_updated_xml.status = "failed"
                        logging.warning(f"Resource {resource_with_updated_xml.identifier} NOT UPDATED SUCCESSFULLY. Status code: {
                                        response.status_code}")
                    resource_with_updated_xml.update_response = response.content
    finally:
        # Compare the resource in the GET to that of the PUT, to see
        # what changed for the production run
        try:
            if settings.dry_run == False:
                if settings.xpath_of_resource_in_put_response:
                    logging.info("Beginning comparison of GET / PUT responses...")
                    with open(f"{project_path}/comparisons.json", "w") as f:
                        logging.info(f"Saving comparison to {
                                    project_path}/comparisons.json")
                        json.dump(comparator.compare(api_resources), f, indent=2)
                        logging.info("Done.")
                else:
                    print("Skipping Comparator - no 'xpath_of_resource_in_put_response'")
            else:
                # Do the comparison for the dry run
                logging.info("Beginning comparator...")

                # We want the comparisons to carry over from production run to production
                # run, so read the old ones first if they exist. 
                try:
                    with open(f"{dry_run_folder}/comparisons.json", "r") as f:
                        old_comparisons = json.load(f)
                except FileNotFoundError:
                    old_comparisons = None

                with open(f"{dry_run_folder}/comparisons.json", "w") as f:
                    comparisons = comparator.compare(api_resources, dry_run=True)
                    # Append the comparisons to the old comparisons if there is such
                    # thing as the old comparisons.
                    if old_comparisons:
                        comparisons = old_comparisons | comparisons
                    json.dump(comparisons, f, indent=2)
                logging.info("Done.")
        except Exception as e:
            logging.exception(e.__str__())

        if settings.dry_run == False:
            logging.info("Saving state...")
            pm.save_state(api_resources)
            logging.info("Done.")
        else:
            logging.info("Dry run done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "project_name", help="The name of the project to generate.", type=str)
    args = parser.parse_args()

    main(args.project_name)