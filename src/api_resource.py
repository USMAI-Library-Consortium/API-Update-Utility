

class ApiResource:
    def __init__(self, identifier: str, api_url: str, update_values: list[str] = [], status: str | None = "pending"):
        self.identifier = identifier
        self.update_values = update_values
        self.status = status
        self.api_url = api_url

        self.xml_from_get_request: bytes = None
        self.xml_for_update_request: bytes = None
        self.update_response: bytes = None
