import unittest

from src.api_resource import ApiResource
from src.verify_response_content import verify_response_content


class TestVerifyResponseContent(unittest.TestCase):

    def test_simple_verify_response_content_passes(self):
        with open("tests/testdata/xml/xml_resource.xml", "rb") as f:
            test_xml = f.read()
        test_resource = ApiResource("1234", "https://google.com")

        test_resource.xml_from_get_request = test_xml

        verify_response_content(test_resource, "/vendor/meta/gracePeriod/days")

    def test_simple_verify_response_content_fails(self):
        with open("tests/testdata/xml/xml_resource.xml", "rb") as f:
            test_xml = f.read()
        test_resource = ApiResource("1234", "https://google.com")

        test_resource.xml_from_get_request = test_xml

        api_resource = verify_response_content(test_resource, "/vendor/gracePeriod/hours")

        self.assertEqual(api_resource.status, "failed")

    def test_verify_response_content_pending_no_get_info_passes(self):
        test_resource = ApiResource("1234", "https://google.com")
        verify_response_content(test_resource, "/vendor/meta/gracePeriod/days")
