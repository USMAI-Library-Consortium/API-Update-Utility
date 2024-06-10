import unittest

from src.read_configuration import read_configuration

class TestReadConfiguration(unittest.TestCase):

    def test_read_configuration(self):
        configuration, api_resources = read_configuration("tests/testdata/testprojectconfig", [])

        self.assertEqual(configuration["xpaths"], ["test_xpath"])
        self.assertEqual(configuration["xpath_operations"], ["update"])
        self.assertEqual(configuration["test_xpath"], "test_verification_xpath")
        self.assertEqual(configuration["dry_run"], True)
        self.assertEqual(configuration["request_limit"], None)

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
        configuration, api_resources = read_configuration("tests/testdata/testprojectconfig", ["19982"])

        self.assertEqual(configuration["xpaths"], ["test_xpath"])
        self.assertEqual(configuration["xpath_operations"], ["update"])
        self.assertEqual(configuration["dry_run"], True)
        self.assertEqual(configuration["request_limit"], None)

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
        configuration, api_resources = read_configuration("tests/testdata/testprojectconfig_multiplexpaths", [])

        self.assertListEqual(configuration["xpaths"], ["test_xpath", "test_xpath_2"])
        self.assertListEqual(configuration["xpath_operations"], ["update", "delete"])
        self.assertEqual(configuration["test_xpath"], "test_verification_xpath")
        self.assertEqual(configuration["dry_run"], True)
        self.assertEqual(configuration["request_limit"], None)

        self.assertListEqual(api_resources[0].update_values, ["USA", "20093"])
        self.assertListEqual(api_resources[1].update_values, ["USA", "88283"])
        self.assertListEqual(api_resources[2].update_values, ["Denmark", "024"])
        self.assertListEqual(api_resources[3].update_values, ["Chile", "8839"])

    def test_read_configuration_mismatched_xpaths_and_values(self):
        """There should be the same number of values and xpaths"""
        with self.assertRaises(ValueError):
            configuration, api_resources = read_configuration("tests/testdata/testprojectconfig_mismatchedxpaths", [])

    def test_read_configuration_mismatched_xpaths_and_operations(self):
        """If 'operations' is an array, there should be the same number of operations as xpaths"""
        with self.assertRaises(ValueError):
            configuration, api_resources = read_configuration("tests/testdata/testprojectconfig_mismatched_operations", [])

        

