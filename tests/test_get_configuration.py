import unittest
import sys

from src.get_configuration import get_configuration


class TestGetConfiguration(unittest.TestCase):

    def test_get_configuration(self):
        configuration = get_configuration("tests/testdata/proj_basic")

        self.assertEqual(configuration.xpaths, ["test_xpath"])
        self.assertEqual(configuration.xpath_operations, ["update"])
        self.assertEqual(configuration.xpath_for_get_response_verification, "test_verification_xpath")
        self.assertEqual(configuration.xpath_of_resource_in_put_response, "/status/vendor")
        self.assertEqual(configuration.dry_run, True)
        self.assertEqual(configuration.update_limit, None)
        self.assertEqual(configuration.retry_failed, False)
        self.assertEqual(configuration.update_file, "tests/testdata/proj_basic/input.csv")
        self.assertEqual(configuration.api_url_template, "https://alma.exlibrisgroup.com/users/<resource_id>")
        self.assertEqual(configuration.query_param_api_key, "apikey=1234")

    def test_get_configuration_mismatched_xpaths_and_operations(self):
        """If 'operations' is an array, there should be the same number of operations as xpaths"""
        with self.assertRaises(ValueError):
            get_configuration("tests/testdata/proj_mismatched_operations")
    
    def test_get_configuration_no_operations_raises_error(self):
        """If we're using the built-in xml body update function, we need operations"""
        with self.assertRaises(ValueError):
            get_configuration("tests/testdata/proj_no_operations")

    def test_get_configuration_no_operations_custom_function(self):
        # This should not throw an error. 
        get_configuration("tests/testdata/proj_no_operations_custom_function")