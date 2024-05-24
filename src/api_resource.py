

class ApiResource:
    def __init__(self, identifier: str):
        self.identifier = identifier

        self.xml_from_get_request: bytearray = None
        self.xml_for_update_resquest: bytearray = None
        self.update_response: bytearray = None
    