import unittest

from src.api_resource import ApiResource
from src.verify_response_content import verify_response_content

class TestVerifyResponseContent(unittest.TestCase):
    
    def test_simple_verify_response_content_passes(self):
        with open("tests/testdata/xml_resource.xml", "rb") as f:
            test_xml = f.read()
        test_resource = ApiResource("1234", "https://google.com")

        test_resource.xml_from_get_request = test_xml

        verified_resources = verify_response_content([test_resource], "/vendor/meta/gracePeriod/days")
        self.assertEqual(len(verified_resources), 1)

    def test_simple_verify_response_content_fails(self):
        with open("tests/testdata/xml_resource.xml", "rb") as f:
            test_xml = f.read()
        test_resource = ApiResource("1234", "https://google.com")

        test_resource.xml_from_get_request = test_xml

        verified_resources = verify_response_content([test_resource], "/vendor/gracePeriod/hours")
        
        self.assertEqual(len(verified_resources), 1)
        self.assertEqual(verified_resources[0].status, "failed")