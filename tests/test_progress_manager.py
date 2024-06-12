import unittest

from src.progress_manager import ProgressManager
from src.api_resource import ApiResource


class TestProgressManager(unittest.TestCase):

    def test_initialize_progress_manager_read_application_state(self):
        pm = ProgressManager("tests/testdata/testproject")

        expected_completed_api_resources = ["1234", "1235", "1236", "1237"]

        self.assertListEqual(
            pm.previously_completed_api_resources, expected_completed_api_resources)

    def test_initialize_progress_manager_read_application_retry_failed(self):
        pm = ProgressManager("tests/testdata/testproject", retry_failed=True)

        expected_completed_api_resources = ["1235", "1236", "1237"]

        self.assertListEqual(
            pm.previously_completed_api_resources, expected_completed_api_resources)

    def test_create_updated_state(self):
        # This test simulates adding new, finished API resources to a previous run that wasn't
        # fully finished.
        pm = ProgressManager("tests/testdata/testproject")

        completed_api_resources = [ApiResource("7683", None, status="success"), ApiResource(
            "3829", None, status="success"), ApiResource("2345", None, status="success")]

        new_state = pm._get_new_state(
            pm.previous_state, completed_api_resources)
        expected_new_state = [
            {
                "ID": "1234",
                "Status": "failed"
            },
            {
                "ID": "1235",
                "Status": "success"
            },
            {
                "ID": "1236",
                "Status": "success"
            },
            {
                "ID": "1237",
                "Status": "success"
            },
            {
                "ID": "7683",
                "Status": "success"
            },
            {
                "ID": "3829",
                "Status": "success"
            },
            {
                "ID": "2345",
                "Status": "success"
            }
        ]

        for i, state_object in enumerate(expected_new_state):
            self.assertDictEqual(new_state[i], state_object)

    def test_create_updated_state_retry_failed_true(self):
        # This test simulates the program picking up from where it left off, with the option
        # to retry failures set to true. As you can see, id '1234' was marked as failed, so
        # this utility will remove it from the previous state and re-run it.
        # We can see '1234' moved from the first position in the csv file to the 4th, because
        # it was the first ID that was retried in the second run. As you can see, it was
        # successful the second time.
        pm = ProgressManager("tests/testdata/testproject", retry_failed=True)

        completed_api_resources = [ApiResource("1234", None, status="success"), ApiResource(
            "7683", None, status="success"), ApiResource("3829", None, status="success"), ApiResource("2345", None, status="success")]

        new_state = pm._get_new_state(
            pm.previous_state, completed_api_resources)
        expected_new_state = [
            {
                "ID": "1235",
                "Status": "success"
            },
            {
                "ID": "1236",
                "Status": "success"
            },
            {
                "ID": "1237",
                "Status": "success"
            },
            {
                "ID": "1234",
                "Status": "success"
            },
            {
                "ID": "7683",
                "Status": "success"
            },
            {
                "ID": "3829",
                "Status": "success"
            },
            {
                "ID": "2345",
                "Status": "success"
            }
        ]

        for i, state_object in enumerate(expected_new_state):
            self.assertDictEqual(new_state[i], state_object)
