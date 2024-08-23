from __future__ import annotations
import csv
from copy import deepcopy

from src.api_resource import ApiResource

class ProgressManager:
    """Class to manage which API resources have already been acted on so that we don't try
     to perform a production update twice."""
    def __init__(self, project_path: str, retry_failed: bool = False):
        self.progress_file_name = f"{project_path}/progress.csv"
        self.previously_completed_api_resources, self.previous_state = self._parse_application_progress(
            self.progress_file_name, retry_failed=retry_failed)

    def save_state(self, api_resources: list[ApiResource]):
        """Saves the state of the production run. This will add any successful or failed production
        updates to the 'progress.csv' file."""

        # Create new state by adding successful or failed production updates to the state before the
        # program started.
        new_state = self._get_new_state(self.previous_state, api_resources)

        with open(self.progress_file_name, "w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["ID", "Status"])
            writer.writeheader()

            for api_resource in new_state:
                writer.writerow({
                    "ID": api_resource["ID"],
                    "Status": api_resource["Status"]
                })

    @staticmethod
    def _get_new_state(previous_state: list[dict], api_resources: list[ApiResource]):
        """Take the previous state and iterate through a list of API resources to create
        a new state. 
        
        This is done by adding the state of API resources that had production update 
        attempts during this run (identified by not having the status 'pending') 
        to a deep copy of the previous state."""
        new_state = deepcopy(previous_state)

        for completed_api_resource in api_resources:
            if completed_api_resource.status == "pending":
                continue
            else:
                new_state.append({
                    "ID": completed_api_resource.identifier,
                    "Status": completed_api_resource.status
                })

        return new_state

    @staticmethod
    def _parse_application_progress(progress_file_name: str, retry_failed: bool) -> tuple[list[str], list[dict]]:
        """Get the progress of the application prior to this run. This includes the previous state, as well
        as a list of the API resources that were finished.
        
        The definition of 'finished' depends on whether the user set retry_failed to True or False. If True,
        resources from progress.csv that are 'failed' will NOT be considered finished. Else, they will
        be considered finished. Successful resources are always considered finished."""
        api_resources_finished: list[str] = []
        previous_state: list[dict] = []

        with open(progress_file_name, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # This effectively removes all failed resources from the previous state, to be tried again.
                if retry_failed and row["Status"] == "failed":
                    continue

                previous_state.append({"ID": row["ID"], "Status": row["Status"]})
                api_resources_finished.append(row["ID"])

        return api_resources_finished, previous_state
