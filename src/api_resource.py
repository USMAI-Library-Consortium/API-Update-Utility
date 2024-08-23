

class ApiResource:
    """Class to hold information about a resource from the API (e.g., a user). This is
    how resource state is carried through the program."""
    def __init__(self, identifier: str, api_url: str, update_values: list[str] = [], status: str | None = "pending"):
        self.identifier = identifier
        self.update_values = update_values
        self.status = status
        self.api_url = api_url

        self.xml_from_get_request: bytes = None
        self.xml_for_update_request: bytes | None = None
        self.update_response: bytes | None = None

    def mark_successful(self):
        """Mark the API resource as successful."""
        self.status = "success"

    def mark_failed(self):
        """Mark the API resource as failed."""
        self.status = "failed"
