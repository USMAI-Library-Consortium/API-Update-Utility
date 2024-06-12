import logging
import os


class Backup():
    def __init__(self, project_path: str):
        self.backup_location = f"{project_path}/backups"

        if not os.path.exists(self.backup_location):
            os.mkdir(self.backup_location)

        self.files_written = 0

    def backup(self, identifier: str, xml_resource: bytearray) -> int:
        """
        Backup a resource to a filesystem. 
        Return -1 for errors, 0 for success.
        """
        resource_file_name = self.normalize_identifier(identifier)

        filepath = f"{self.backup_location}/{resource_file_name}.xml"
        logging.debug(f"Backing up resource {identifier} to {filepath}")

        try:
            with open(filepath, "wb") as f:
                f.write(xml_resource)
                self.files_written += 1
        except Exception as e:
            logging.error(f"Backup for resource {
                          identifier} failed: {e.__str__()}")
            return -1

        return 0

    @staticmethod
    def normalize_identifier(identifier: str):
        disallowed_chars: set = (
            "*", "/", "\\", ":", "?", '"', "'", ">", "<", "|", ".")

        normalized_identifier = identifier
        for char in disallowed_chars:
            normalized_identifier = normalized_identifier.replace(char, "_")

        return normalized_identifier
