import unittest
from common.common_utils import is_base64


class TestBase64Validation(unittest.TestCase):

    def test_valid_base64(self):
        valid_base64_strings = [
            "SGVsbG8gV29ybGQ=",  # 'Hello World' in base64
            "U29tZXRoaW5n",  # 'Something' without padding
            "",  # An empty string is technically a valid base64
            "YQ==",  # 'a' with padding
        ]
        for s in valid_base64_strings:
            self.assertTrue(is_base64(s), f"Expected {s} to be valid base64.")

    def test_invalid_base64(self):
        invalid_base64_strings = [
            "SGVsbG8gV29ybGQ",  # No padding when required
            "U29tZXRoaW5n===",  # Improper padding
            "This$$is%%invalid",  # Invalid characters
            "YWJjZA=",  # Incorrect padding: 'abcd' decodes to 'abc'
        ]
        for s in invalid_base64_strings:
            self.assertFalse(is_base64(s), f"Expected {s} to be invalid base64.")
