import unittest
from src.api_resource import ApiResource
from src.xml_updater import XMLUpdater

import xmltodict

class TestResourceUpdaterXML(unittest.TestCase):
    
    def test_update_one_resource_update_el_with_xpath(self):
        xu = XMLUpdater(xpath="/vendor/meta/gracePeriod/days")
        test_resource = ApiResource("11224", "https://fakeserver/id", "8")

        with open("tests/testdata/xml_resource.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource
        
        updated_resources = xu.run([test_resource])

        with open("tests/testdata/xml_resource_updated_el.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_resquest)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)

    def test_update_one_resource_insert_el_with_xpath(self):
        xu = XMLUpdater(xpath="/vendor/meta/gracePeriod")
        test_resource = ApiResource("11224", "https://fakeserver/id", "<hours>12</hours>", operation="insert")

        with open("tests/testdata/xml_resource.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource

        updated_resources = xu.run([test_resource])
        with open("tests/testdata/xml_resource_inserted_el.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_resquest)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)

    def test_update_one_resource_delete_el_with_xpath(self):
        xu = XMLUpdater(xpath="/vendor/meta")
        test_resource = ApiResource("11224", "https://fakeserver/id", update_value="gracePeriod", operation="delete")

        with open("tests/testdata/xml_resource.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource

        updated_resources = xu.run([test_resource])
        with open("tests/testdata/xml_resource_deleted_el.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_resquest)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)

    def test_update_one_resource_delete_el_in_list_with_xpath(self):
        xu = XMLUpdater(xpath="/vendor/meta/gracePeriod")
        test_resource = ApiResource("11224", "https://fakeserver/id", update_value="hours", operation="delete")

        with open("tests/testdata/xml_resource_inserted_el.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource

        updated_resources = xu.run([test_resource])
        with open("tests/testdata/xml_resource.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_resquest)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)

    def test_update_one_resource_delete_el_all_in_list_with_xpath(self):
        xu = XMLUpdater(xpath="/vendor/meta/gracePeriod")
        test_resource = ApiResource("11224", "https://fakeserver/id", update_value="*", operation="delete")

        with open("tests/testdata/xml_resource_inserted_el.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource

        updated_resources = xu.run([test_resource])
        with open("tests/testdata/xml_resource_children_removed.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_resquest)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)

    def test_update_one_resource_delete_el_middle_in_list_with_xpath(self):
        xu = XMLUpdater(xpath="/vendor/meta")
        test_resource = ApiResource("11224", "https://fakeserver/id", update_value="title[2]", operation="delete")

        with open("tests/testdata/xml_resource_with_list.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource

        updated_resources = xu.run([test_resource])
        with open("tests/testdata/xml_resource_with_list_middle_removed.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_resquest)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)

    def test_update_one_resource_delete_all_el_of_one_type(self):
        xu = XMLUpdater(xpath="/vendor/meta")
        test_resource = ApiResource("11224", "https://fakeserver/id", update_value="title", operation="delete")

        with open("tests/testdata/xml_resource_with_list.xml", "rb") as f:
            xml_resource = f.read()
        test_resource.xml_from_get_request = xml_resource

        updated_resources = xu.run([test_resource])
        with open("tests/testdata/xml_resource_with_list_removed.xml", "rb") as f:
            expected_xml_resource = f.read()

        real_xml_dict = xmltodict.parse(updated_resources[0].xml_for_update_resquest)
        expected_xml_dict = xmltodict.parse(expected_xml_resource)

        self.assertDictEqual(real_xml_dict, expected_xml_dict)