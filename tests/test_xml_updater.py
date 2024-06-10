import unittest
from src.api_resource import ApiResource
from src.xml_updater import XMLUpdater

import xmltodict

class TestResourceUpdaterXML(unittest.TestCase):
    
    def test_update_one_resource_update_el_with_xpath(self):
        xu = XMLUpdater(xpaths=["/vendor/meta/gracePeriod/days"], operations=["update"])
        test_resource = ApiResource("11224", "https://fakeserver/id", ["8"])

        with open("tests/testdata/xml_resource.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource
        
        updated_resources = xu.run([test_resource])

        with open("tests/testdata/xml_resource_updated_el.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_request)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)

    def test_update_one_resource_update_or_insert_el_with_xpath_el_exists(self):
        xu = XMLUpdater(xpaths=["/vendor/meta/gracePeriod/days"], operations=["updateOrInsert"])
        test_resource = ApiResource("11224", "https://fakeserver/id", ["8"])

        with open("tests/testdata/xml_resource.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource
        
        updated_resources = xu.run([test_resource])

        with open("tests/testdata/xml_resource_updated_el.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_request)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)

    def test_update_one_resource_update_or_insert_el_with_xpath_el_does_not_exist(self):
        xu = XMLUpdater(xpaths=["/vendor/meta/gracePeriod/hours"], operations=["updateOrInsert"])
        test_resource = ApiResource("11224", "https://fakeserver/id", ["12"])

        with open("tests/testdata/xml_resource.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource
        
        updated_resources = xu.run([test_resource])

        with open("tests/testdata/xml_resource_inserted_el.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_request)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)

    def test_update_one_resource_insert_el_with_xpath(self):
        xu = XMLUpdater(xpaths=["/vendor/meta/gracePeriod"], operations=["insert"])
        test_resource = ApiResource("11224", "https://fakeserver/id",["<hours>12</hours>"])

        with open("tests/testdata/xml_resource.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource

        updated_resources = xu.run([test_resource])
        with open("tests/testdata/xml_resource_inserted_el.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_request)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)

    def test_update_one_resource_delete_el_with_xpath(self):
        xu = XMLUpdater(xpaths=["/vendor/meta"], operations=["delete"])
        test_resource = ApiResource("11224", "https://fakeserver/id", update_values=["gracePeriod"])

        with open("tests/testdata/xml_resource.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource

        updated_resources = xu.run([test_resource])
        with open("tests/testdata/xml_resource_deleted_el.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_request)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)

    def test_update_one_resource_delete_el_in_list_with_xpath(self):
        xu = XMLUpdater(xpaths=["/vendor/meta/gracePeriod"], operations=["delete"])
        test_resource = ApiResource("11224", "https://fakeserver/id", update_values=["hours"])

        with open("tests/testdata/xml_resource_inserted_el.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource

        updated_resources = xu.run([test_resource])
        with open("tests/testdata/xml_resource.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_request)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)

    def test_update_one_resource_delete_el_all_in_list_with_xpath(self):
        xu = XMLUpdater(xpaths=["/vendor/meta/gracePeriod"], operations=["delete"])
        test_resource = ApiResource("11224", "https://fakeserver/id", update_values=["*"])

        with open("tests/testdata/xml_resource_inserted_el.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource

        updated_resources = xu.run([test_resource])
        with open("tests/testdata/xml_resource_children_removed.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_request)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)

    def test_update_one_resource_delete_el_middle_in_list_with_xpath(self):
        xu = XMLUpdater(xpaths=["/vendor/meta"], operations=["delete"])
        test_resource = ApiResource("11224", "https://fakeserver/id", update_values=["title[2]"])

        with open("tests/testdata/xml_resource_with_list.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource

        updated_resources = xu.run([test_resource])
        with open("tests/testdata/xml_resource_with_list_middle_removed.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_request)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)

    def test_update_one_resource_delete_all_el_of_one_type(self):
        xu = XMLUpdater(xpaths=["/vendor/meta"], operations=["delete"])
        test_resource = ApiResource("11224", "https://fakeserver/id", update_values=["title"])

        with open("tests/testdata/xml_resource_with_list.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource

        updated_resources = xu.run([test_resource])
        with open("tests/testdata/xml_resource_with_list_removed.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_request)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)