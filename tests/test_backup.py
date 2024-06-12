import unittest

from src.backup import Backup


class TestBackupResource(unittest.TestCase):

    def test_normalize_identifier(self):
        name_to_normalize = "**VENDOR_03"

        updated_name = Backup.normalize_identifier(name_to_normalize)

        self.assertEqual(updated_name, "__VENDOR_03")

    def test_normalize_identifier_1(self):
        name_to_normalize = "/VENDOR_03"

        updated_name = Backup.normalize_identifier(name_to_normalize)

        self.assertEqual(updated_name, "_VENDOR_03")

    def test_normalize_identifier_2(self):
        name_to_normalize = "/VENDOR_03/."

        updated_name = Backup.normalize_identifier(name_to_normalize)

        self.assertEqual(updated_name, "_VENDOR_03__")
