import unittest 
import importlib

from src.read_input import read_input

class TestReadInput(unittest.TestCase):

    def test_read_input(self):
        settings = importlib.import_module("tests.testdata.proj_basic.project_settings")
        settings.update_file = "tests/testdata/proj_basic/input.csv"
        api_resources = read_input(settings, api_resources_finished=[])

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
        settings = importlib.import_module("tests.testdata.proj_basic.project_settings")
        settings.update_file = "tests/testdata/proj_basic/input.csv"
        api_resources = read_input(settings, api_resources_finished=["19982"])

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
        settings = importlib.import_module("tests.testdata.proj_multiple_xpaths.project_settings")
        settings.update_file = "tests/testdata/proj_multiple_xpaths/input.csv"
        api_resources = read_input(settings, api_resources_finished=[])

        self.assertListEqual(api_resources[0].update_values, ["USA", "20093"])
        self.assertListEqual(api_resources[1].update_values, ["USA", "88283"])
        self.assertListEqual(api_resources[2].update_values, ["Denmark", "024"])
        self.assertListEqual(api_resources[3].update_values, ["Chile", "8839"])

    def test_read_input_mismatched_xpaths_and_values(self):
        """There should be the same number of values and xpaths"""
        settings = importlib.import_module("tests.testdata.proj_mismatched_xpaths.project_settings")
        settings.update_file = "tests/testdata/proj_mismatched_xpaths/input.csv"
        settings.use_custom_xml_update_function = False
        with self.assertRaises(ValueError):
            read_input(settings, [])

    def test_read_input_mismatched_xpath_and_values_custom_function_no_error(self):
        """We should be able to put whatever combo of xpaths and values when we use a custom function"""
        """There should be the same number of values and xpaths"""
        settings = importlib.import_module("tests.testdata.proj_mismatched_xpaths.project_settings")
        settings.update_file = "tests/testdata/proj_mismatched_xpaths/input.csv"
        settings.use_custom_xml_update_function = True
        
        # Just assert there's no errors thrown
        read_input(settings, [])