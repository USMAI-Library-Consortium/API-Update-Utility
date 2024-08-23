import argparse
import os
import logging
import shutil
import requests
from tqdm import tqdm
from datetime import datetime

from src.get_configuration import get_configuration
from src.read_update_file import read_update_file
from src.retrieve_resource import retrieve_resource
from src.backup import Backup
from src.xml_updater import XMLUpdater
from src.progress_manager import ProgressManager
from src.verify_response_content import verify_response_content
from src.comparator import Comparator


def main(project_name: str):
    """The function that runs the actual update utility."""
    # ------------------------------- LOOK FOR PROJECT -------------------------------------

    project_path = f"projects/{project_name}"
    if not os.path.exists(project_path):
        raise FileNotFoundError(
            f"Project '{project_name}' has not been initialized.")

    # -------------------- INITIALIZE LOGGER; PRINT INIT MESSAGES ------------------------

    # Timestamp for logfile
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    logging.basicConfig(filename=f"{project_path}/logs_{timestamp}.log",
                        format='%(levelname)s:%(asctime)s: %(message)s', level=logging.INFO)
    logging.info("Starting API Update Utility...")
    logging.info(f"Project: {project_name}")

    # ---------------------------- HANDLE USER CONFIGURATION --------------------------------

    settings = get_configuration(f"projects/{project_name}")

    final_update_limit = None
    if settings.update_limit and settings.update_limit > 0:
        final_update_limit = settings.update_limit

    # ------------------------- INITIALIZE THE NEEDED COMPONENTS --------------------------

    pm = ProgressManager(project_path, retry_failed=settings.retry_failed)
    backuper = Backup(project_path=project_path)
    xu = XMLUpdater(custom_update_function=settings.custom_xml_update_function if settings.use_custom_xml_update_function else None,
                        xpaths=settings.xpaths, operations=settings.xpath_operations)
    session = requests.Session()

    # ------------------------ CREATE DRY RUN FOLDER IF NEEDED ---------------------------

    if settings.dry_run == True:
        dry_run_folder = f"{project_path}/dryRun"
        logging.info(f"Dry run mode: saving resources to {dry_run_folder}.")
        # Reset dry run folder
        if os.path.exists(dry_run_folder):
            shutil.rmtree(dry_run_folder)
        os.mkdir(dry_run_folder)

    # ------------------------- GET API RESOURCES FROM UPDATE FILE --------------------------

    api_resources = read_update_file(settings, api_resources_to_exclude=pm.previously_completed_api_resources)

    if len(api_resources) == 0:
        logging.info(f"Exiting - no resources to update.{
                     " (retryFailed is set to false, there may be failed resources. Check 'progress.csv')" if not settings.retry_failed else " Congrats!"}")
        return

    logging.info(f"Resources to update: {settings.update_limit}")
    logging.info(f"Dry run mode: {settings.dry_run}")

    # ----------------------- START THE ACTUAL API WORK -----------------------------

    try:
        # Progress bar.
        for index in tqdm(range(final_update_limit)):

            # GET THE XML FOR EACH RESOURCE ---------------------------
            logging.info(f"Working on resource {api_resources[index].identifier}...")
            logging.debug("Retrieving GET request...")
            api_resource_with_xml = retrieve_resource(api_resources[index])
            logging.debug("Done.")

            # VERIFY THE XML IS VALID ---------------------------------
            logging.debug("Verifying response content...")
            verified_api_resource = verify_response_content(api_resource_with_xml, settings.xpath_for_get_response_verification)
            logging.debug("Done.")

            # BACK UP XML IF VALID AND NOT DRY RUN --------------------
            if settings.dry_run == False:
                if verified_api_resource.status != "failed":
                    logging.debug("Backing up resource...")
                    result = backuper.backup(verified_api_resource.identifier, verified_api_resource.xml_from_get_request)
                    if result == -1:
                        logging.error(f"Could not back up vendor {verified_api_resource.identifier}")
                        verified_api_resource.mark_failed()
                    logging.debug("Done")
                else:
                    logging.debug(f"Skipping backup of resource {verified_api_resource.identifier} due to status '{verified_api_resource.status}'.")

            # UPDATE THE XML -----------------------------------------------------
            logging.debug("Updating XML...")
            resource_with_updated_xml = xu.update_resource(verified_api_resource)
            logging.debug("Done.")

            # IF THIS IS A DRY RUN, SAVE THE UPDATED XML -------------------------
            if settings.dry_run == True:
                # Only save resources if they have updated XML (i.e, are still pending a production update)
                if resource_with_updated_xml.status == "pending":
                    resource_file_path = f"{dry_run_folder}/{Backup.normalize_identifier(resource_with_updated_xml.identifier)}.xml"
                    with open(resource_file_path, "wb") as f:
                        f.write(resource_with_updated_xml.xml_for_update_request)
                    logging.debug("Done")
            
            # IF THIS IS A PRODUCTION RUN, RUN THE API UPDATE --------------------
            else:
                # Only run on resources that are pending.
                if resource_with_updated_xml.status == "pending":
                    response = session.put(resource_with_updated_xml.api_url, data=resource_with_updated_xml.xml_for_update_request, headers={
                                            "Content-Type": "application/xml"})
                    if response.status_code == 200:
                        resource_with_updated_xml.mark_successful()
                        logging.info(f"Resource {resource_with_updated_xml.identifier} updated successfully.")
                    else:
                        resource_with_updated_xml.mark_failed()
                        logging.warning(f"Resource {resource_with_updated_xml.identifier} NOT UPDATED SUCCESSFULLY. Status code: {response.status_code}")
                    resource_with_updated_xml.update_response = response.content
    finally:
        # --------------- RUN COMPARATOR ----------------

        try:
            if settings.dry_run == False and settings.xpath_of_resource_in_put_response:
                # Initialize comparator
                comparator = Comparator(settings.xpath_of_resource_in_put_response)

                # Compare the resource from the GET request to what the PUT response return, to see
                # what changed during the API update.
                comparison_filepath = f"{project_path}/comparisons.json"
                past_comparison_dict = Comparator.get_past_comparisons(comparison_filepath)

                # Run the comparator
                cumulative_comparisons = comparator.compare(past_comparison_dict, api_resources)

                # Write the results to the file
                Comparator.write_comparisons(comparison_filepath, cumulative_comparisons)
            elif settings.dry_run == False and not settings.xpath_of_resource_in_put_response:
                logging.warning(f"Skipping comparisions as there's no xpath_of_resource_in_put_response")
            else:
                # Intitalize comparator
                comparator = Comparator()

                # Perform the operation for the dry run
                comparison_filepath = f"{dry_run_folder}/comparisons.json"

                # Run the comparator. NOTE there is no cumulative comparisons for dry run because the folder is
                # deleted each time.
                comparisons = comparator.compare({}, api_resources)

                # Write the results to the file
                Comparator.write_comparisons(comparison_filepath, comparisons)
        except:
            logging.exception("Something went wrong in running the comparator.")

        # --------------------- SAVE STATE ------------------------

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