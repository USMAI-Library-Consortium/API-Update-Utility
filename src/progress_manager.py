from __future__ import annotations
import csv

from src.api_resource import ApiResource

class ProgressManager:

    def __init__(self, project_path: str, retry_failed: bool=False):
        self.progress_file_name = f"{project_path}/progress.csv"
        self.previously_completed_api_resources, self.previous_state = self._parse_application_progress(self.progress_file_name, retry_failed=retry_failed)

    def save_state(self, api_resources: list[ApiResource]):
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
        new_state = previous_state

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
        api_resources_finished: list[str] = []
        previous_state: list[dict] = []

        with open(progress_file_name, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                if retry_failed and row["Status"] == "failed": continue
                else: 
                    previous_state.append({
                        "ID": row["ID"],
                        "Status": row["Status"]
                    })
                    api_resources_finished.append(row["ID"])

        return api_resources_finished, previous_state

