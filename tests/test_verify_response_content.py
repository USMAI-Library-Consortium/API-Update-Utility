import unittest

from src.api_resource import ApiResource
from src.verify_response_content import verify_response_content


class TestVerifyResponseContent(unittest.TestCase):

    def test_simple_verify_response_content_passes(self):
        with open("tests/testdata/xml/xml_resource.xml", "rb") as f:
            test_xml = f.read()
        test_resource = ApiResource("1234", "https://google.com")

        test_resource.xml_from_get_request = test_xml

        api_resources = [test_resource]
        verified_resources = verify_response_content(
            api_resources, "/vendor/meta/gracePeriod/days")
        self.assertEqual(len(api_resources), 1)

    def test_simple_verify_response_content_fails(self):
        with open("tests/testdata/xml/xml_resource.xml", "rb") as f:
            test_xml = f.read()
        test_resource = ApiResource("1234", "https://google.com")

        test_resource.xml_from_get_request = test_xml

        api_resources = [test_resource]
        verify_response_content(api_resources, "/vendor/gracePeriod/hours")

        self.assertEqual(len(api_resources), 1)
        self.assertEqual(api_resources[0].status, "failed")

    def test_verify_response_content_pending_no_get_info_passes(self):
        test_resource = ApiResource("1234", "https://google.com")

        api_resources = [test_resource]
        verify_response_content(api_resources, "/vendor/meta/gracePeriod/days")
