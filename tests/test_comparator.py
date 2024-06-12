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