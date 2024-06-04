

class ApiResource:
    def __init__(self, identifier: str, update_url: str, update_value: str | None = None, status: str | None = "pending", operation: str = "update"):
        self.identifier = identifier
        self.update_value = update_value
        self.status = status
        self.update_url = update_url
        self.operation = operation

        self.xml_from_get_request: bytes = None
        self.xml_for_update_resquest: bytes = None
        self.update_response: bytes = None
    