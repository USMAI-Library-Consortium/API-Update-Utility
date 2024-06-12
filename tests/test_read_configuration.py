import unittest

from src.read_configuration import read_configuration


class TestReadConfiguration(unittest.TestCase):

    def test_read_configuration(self):
        configuration = read_configuration("tests/testdata/testprojectconfig")

        self.assertEqual(configuration["xpaths"], ["test_xpath"])
        self.assertEqual(configuration["xpath_operations"], ["update"])
        self.assertEqual(
            configuration["test_xpath"], "test_verification_xpath")
        self.assertEqual(
            configuration["xpath_of_resource_in_put_response"], "/status/vendor")
        self.assertEqual(configuration["dry_run"], True)
        self.assertEqual(configuration["update_limit"], None)
        self.assertEqual(configuration["retry_failed"], False)
        self.assertEqual(configuration["update_file"],
                         "tests/testdata/testprojectconfig/input.csv")
        self.assertEqual(configuration["api_url_template"],
                         "https://alma.exlibrisgroup.com/users/<resource_id>")
        self.assertEqual(configuration["query_param_api_key"], "apikey=1234")

    def test_read_input_mismatched_xpaths_and_operations(self):
        """If 'operations' is an array, there should be the same number of operations as xpaths"""
        with self.assertRaises(ValueError):
            read_configuration(
                "tests/testdata/testprojectconfig_mismatched_operations")
