import logging
import os

class Backup():
    """Class for backing up the XML retrieved from a GET request. This class also creates the backup
     folder if it does not exist and tracks how many files were written."""
    def __init__(self, project_path: str):
        self.backup_location = f"{project_path}/backups"

        if not os.path.exists(self.backup_location):
            os.mkdir(self.backup_location)

        self.files_written = 0

    def backup(self, identifier: str, xml_resource: bytearray) -> int:
        """
        Backup an XML resource to a backup folder. 
        Return -1 for errors, 0 for success.
        """
        resource_file_name = self.normalize_identifier(identifier)
        filepath = f"{self.backup_location}/{resource_file_name}.xml"

        logging.debug(f"Backing up resource {identifier} to {filepath}")

        try:
            with open(filepath, "wb") as f:
                f.write(xml_resource)
                self.files_written += 1
        except:
            logging.exception(f"Backup for resource {identifier} failed.")
            return -1
        return 0

    @staticmethod
    def normalize_identifier(identifier: str):
        """This takes a resource identifier (e.g., a user ID) and removes characters that
        are not allowed as part of file names. 
        
        This will allow the file names of backups to be more easily identifiable for spot 
        checking, and will ensure that they can be properly saved."""
        disallowed_chars: set = (
            "*", "/", "\\", ":", "?", '"', "'", ">", "<", "|", ".")

        normalized_identifier = identifier
        for char in disallowed_chars:
            normalized_identifier = normalized_identifier.replace(char, "_")

        return normalized_identifier
