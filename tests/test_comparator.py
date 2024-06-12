import unittest

from src.comparator import Comparator
from src.api_resource import ApiResource

class TestComparator(unittest.TestCase):
    def test_comparison_format_correct(self):
        api_resource = ApiResource("BRILL", "https://url.com")
        api_resource.status = "success"
        with open("tests/testdata/test_vendor_from_get.xml", "rb") as f:
            api_resource.xml_from_get_request = f.read()
        
        with open ("tests/testdata/test_vendor_from_put.xml", "rb") as f:
            api_resource.update_response = f.read()

        c = Comparator(xpath_of_resource_in_put_response=None)
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
    
    def test_comparator_resource_nested(self):
        api_resource = ApiResource("BRILL", "https://url.com")
        api_resource.status = "success"
        with open("tests/testdata/test_vendor_from_get.xml", "rb") as f:
            api_resource.xml_from_get_request = f.read()
        
        with open ("tests/testdata/test_vendor_from_put_nested.xml", "rb") as f:
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
        api_resource.status = "failed"
        c = Comparator(xpath_of_resource_in_put_response="/results/vendor")
        result = c.compare([api_resource])

        self.assertDictEqual(result, {})

    def test_comparator_no_difference_str_result(self):
        api_resource = ApiResource("BRILL", "https://url.com")
        api_resource.status = "success"
        with open("tests/testdata/test_vendor_from_get.xml", "rb") as f:
            api_resource.xml_from_get_request = f.read()
        
        # Use the same vendor XML again to simulate no change.
        with open ("tests/testdata/test_vendor_from_get.xml", "rb") as f:
            api_resource.update_response = f.read()

        c = Comparator()
        result = c.compare([api_resource])

        self.assertDictEqual(result, {
                "BRILL": "No Difference"
            }
        )

    def test_comparator_dry_run(self):
        api_resource = ApiResource("BRILL", "https://url.com")
        with open("tests/testdata/test_vendor_from_get.xml", "rb") as f:
            api_resource.xml_from_get_request = f.read()
        
        # This time we're setting the xml FOR update request, as this is a comparator 
        # for the dry run
        with open ("tests/testdata/test_vendor_from_put.xml", "rb") as f:
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