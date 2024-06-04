

class ApiResource:
    def __init__(self, identifier: str, api_url: str, update_value: str | None = None, status: str | None = "pending", operation: str = "update"):
        self.identifier = identifier
        self.update_value = update_value
        self.status = status
        self.api_url = api_url
        self.operation = operation

        self.xml_from_get_request: bytes = None
        self.xml_for_update_resquest: bytes = None
        self.update_response: bytes = None
    