import unittest
import json

from src.comparator import Comparator
from src.api_resource import ApiResource


class TestComparator(unittest.TestCase):
    def test_comparison_format_correct(self):
        api_resource = ApiResource("BRILL", "https://url.com")
        api_resource.status = "success"
        api_resource.xml_for_update_request = "FILLER"
        with open("tests/testdata/xml/test_vendor_from_get.xml", "rb") as f:
            api_resource.xml_from_get_request = f.read()

        with open("tests/testdata/xml/test_vendor_from_put.xml", "rb") as f:
            api_resource.update_response = f.read()

        c = Comparator(xpath_of_resource_in_put_response="/vendor")
        result = c.compare([api_resource])

        self.assertDictEqual(result, {
            "BRILL": {
                'values_changed': {
                    "root['vendor']['status']['@desc']": {'new_value': 'Inactive', 'old_value': 'Active'},
                    "root['vendor']['status']['#text']": {'new_value': 'INACTIVE', 'old_value': 'ACTIVE'}
                }
            }
        }
        )

        with open ("tests/testdata/xml/test_comparator_output.json", "w") as f:
            json.dump(result, f, indent=2)

    def test_comparator_resource_nested(self):
        api_resource = ApiResource("BRILL", "https://url.com")
        api_resource.status = "success"
        api_resource.xml_for_update_request = "FILLER"
        with open("tests/testdata/xml/test_vendor_from_get.xml", "rb") as f:
            api_resource.xml_from_get_request = f.read()

        with open("tests/testdata/xml/test_vendor_from_put_nested.xml", "rb") as f:
            api_resource.update_response = f.read()

        c = Comparator(xpath_of_resource_in_put_response="/results/vendor")
        result = c.compare([api_resource])

        self.assertDictEqual(result, {
            "BRILL": {
                'values_changed': {
                    "root['vendor']['status']['@desc']": {'new_value': 'Inactive', 'old_value': 'Active'},
                    "root['vendor']['status']['#text']": {'new_value': 'INACTIVE', 'old_value': 'ACTIVE'}
                }
            }
        }
        )

    def test_comparator_skip_api_resource_not_successful(self):
        api_resource = ApiResource("XLLSM", "https://example.com")
        api_resource.mark_failed()
        api_resource.xml_for_update_request = "FILLER"
        c = Comparator(xpath_of_resource_in_put_response="/results/vendor")
        result = c.compare([api_resource])

        self.assertDictEqual(result, {})

    def test_comparator_no_difference_str_result(self):
        api_resource = ApiResource("BRILL", "https://url.com")
        api_resource.status = "success"
        api_resource.xml_for_update_request = "FILLER"
        with open("tests/testdata/xml/test_vendor_from_get.xml", "rb") as f:
            api_resource.xml_from_get_request = f.read()

        # Use the same vendor XML again to simulate no change.
        with open("tests/testdata/xml/test_vendor_from_get.xml", "rb") as f:
            api_resource.update_response = f.read()

        c = Comparator()
        result = c.compare([api_resource])

        self.assertDictEqual(result, {
            "BRILL": "No Difference"
        })

    def test_comparator_one_resource_failed_xpath(self):
        """If the xpath of the resource could not be found (this is likely due to an 
        error message slipping through or a wrong user-inputted xpath), say so in the returned dict but continue processing."""
        c = Comparator(xpath_of_resource_in_put_response="/vendor")

        # This one should show no change
        api_resource_1 = ApiResource("RESOURCE_1", "https://url.com")
        api_resource_1.status = "success"
        api_resource_1.xml_for_update_request = "FILLER"
        with open("tests/testdata/xml/test_vendor_from_get.xml", "rb") as f:
            api_resource_1.xml_from_get_request = f.read()

        with open("tests/testdata/xml/test_vendor_from_get.xml", "rb") as f:
            api_resource_1.update_response = f.read()

        # This resource has the wrong xpath.
        api_resource_2 = ApiResource("RESOURCE_2", "https://url.com")
        api_resource_2.status = "success"
        api_resource_2.xml_for_update_request = "FILLER"
        with open("tests/testdata/xml/test_vendor_from_get.xml", "rb") as f:
            api_resource_2.xml_from_get_request = f.read()

        with open("tests/testdata/xml/test_error_message.xml", "rb") as f:
            api_resource_2.update_response = f.read()

        # This one should show a change.
        api_resource_3 = ApiResource("BRILL", "https://url.com")
        api_resource_3.status = "success"
        api_resource_3.xml_for_update_request = "FILLER"
        with open("tests/testdata/xml/test_vendor_from_get.xml", "rb") as f:
            api_resource_3.xml_from_get_request = f.read()

        with open("tests/testdata/xml/test_vendor_from_put.xml", "rb") as f:
            api_resource_3.update_response = f.read()

        result = c.compare([api_resource_1, api_resource_2, api_resource_3])

        self.assertDictEqual(result, {
            "RESOURCE_1": "No Difference",
            "RESOURCE_2": "Could not find xpath '/vendor' in PUT response for resource 'RESOURCE_2'; skipping comparison.",
            "BRILL": {
                'values_changed': {
                    "root['vendor']['status']['@desc']": {'new_value': 'Inactive', 'old_value': 'Active'},
                    "root['vendor']['status']['#text']": {'new_value': 'INACTIVE', 'old_value': 'ACTIVE'}
                }
            }
        })


    def test_comparator_dry_run(self):
        api_resource = ApiResource("BRILL", "https://url.com")
        with open("tests/testdata/xml/test_vendor_from_get.xml", "rb") as f:
            api_resource.xml_from_get_request = f.read()

        # This time we're setting the xml FOR update request, as this is a comparator
        # for the dry run
        with open("tests/testdata/xml/test_vendor_from_put.xml", "rb") as f:
            api_resource.xml_for_update_request = f.read()

        c = Comparator(xpath_of_resource_in_put_response=None)
        result = c.compare([api_resource], dry_run=True)

        self.assertDictEqual(result, {
            "BRILL": {
                'values_changed': {
                    "root['vendor']['status']['@desc']": {'new_value': 'Inactive', 'old_value': 'Active'},
                    "root['vendor']['status']['#text']": {'new_value': 'INACTIVE', 'old_value': 'ACTIVE'}
                }
            }
        }
        )
