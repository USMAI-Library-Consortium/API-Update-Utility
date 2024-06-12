import unittest 

from src.read_input import read_input

class TestReadInput(unittest.TestCase):

    def test_read_input(self):
        configuration = {
            "update_file": "tests/testdata/testprojectconfig/input.csv",
            "api_url_template": "https://alma.exlibrisgroup.com/users/<resource_id>",
            "query_param_api_key": "apikey=1234",
            "xpaths": ["test_xpath"]
        }
        api_resources = read_input(configuration, api_resources_finished=[])

        self.assertEqual(api_resources[0].identifier, "19982")
        self.assertEqual(api_resources[1].identifier, "123199")
        self.assertEqual(api_resources[2].identifier, "23844")
        self.assertEqual(api_resources[3].identifier, "182848")

        self.assertEqual(api_resources[0].api_url, "https://alma.exlibrisgroup.com/users/19982?apikey=1234")
        self.assertEqual(api_resources[1].api_url, "https://alma.exlibrisgroup.com/users/123199?apikey=1234")
        self.assertEqual(api_resources[2].api_url, "https://alma.exlibrisgroup.com/users/23844?apikey=1234")
        self.assertEqual(api_resources[3].api_url, "https://alma.exlibrisgroup.com/users/182848?apikey=1234")

        self.assertEqual(api_resources[0].update_values[0], "USA")
        self.assertEqual(api_resources[1].update_values[0], "USA")
        self.assertEqual(api_resources[2].update_values[0], "Denmark")
        self.assertEqual(api_resources[3].update_values[0], "Chile")

    def test_read_configuration_with_previously_completed_values(self):
        configuration = {
            "update_file": "tests/testdata/testprojectconfig/input.csv",
            "api_url_template": "https://alma.exlibrisgroup.com/users/<resource_id>",
            "query_param_api_key": "apikey=1234",
            "xpaths": ["test_xpath"]
        }
        api_resources = read_input(configuration, api_resources_finished=["19982"])

        self.assertEqual(api_resources[0].identifier, "123199")
        self.assertEqual(api_resources[1].identifier, "23844")
        self.assertEqual(api_resources[2].identifier, "182848")

        self.assertEqual(api_resources[0].api_url, "https://alma.exlibrisgroup.com/users/123199?apikey=1234")
        self.assertEqual(api_resources[1].api_url, "https://alma.exlibrisgroup.com/users/23844?apikey=1234")
        self.assertEqual(api_resources[2].api_url, "https://alma.exlibrisgroup.com/users/182848?apikey=1234")

        self.assertEqual(api_resources[0].update_values[0], "USA")
        self.assertEqual(api_resources[1].update_values[0], "Denmark")
        self.assertEqual(api_resources[2].update_values[0], "Chile")

    def test_read_configuration_multiple_xpaths(self):
        configuration = {
            "update_file": "tests/testdata/testprojectconfig_multiplexpaths/input.csv",
            "api_url_template": "https://alma.exlibrisgroup.com/users/<resource_id>",
            "query_param_api_key": "apikey=1234",
            "xpaths": ["test_xpath", "test_xpath_2"]
        }
        api_resources = read_input(configuration, api_resources_finished=[])

        self.assertListEqual(api_resources[0].update_values, ["USA", "20093"])
        self.assertListEqual(api_resources[1].update_values, ["USA", "88283"])
        self.assertListEqual(api_resources[2].update_values, ["Denmark", "024"])
        self.assertListEqual(api_resources[3].update_values, ["Chile", "8839"])

    def test_read_input_mismatched_xpaths_and_values(self):
        """There should be the same number of values and xpaths"""
        configuration = {
            "update_file": "tests/testdata/testprojectconfig_mismatchedxpaths/input.csv",
            "api_url_template": "https://alma.exlibrisgroup.com/users/<resource_id>",
            "query_param_api_key": "apikey=1234",
            "xpaths": ["test_xpath"]
        }
        with self.assertRaises(ValueError):
            read_input(configuration, [])
